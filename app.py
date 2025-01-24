import warnings

warnings.filterwarnings('ignore', category=UserWarning)

warnings.filterwarnings('ignore', message='.*torch.classes.*')

import streamlit as st

# This must be the first Streamlit command
st.set_page_config(
    page_title="Multi-Modal Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Import required libraries
import os
from dotenv import load_dotenv
from PIL import Image
import warnings
from datetime import datetime

# Import utilities
from utils.file_processors import (
    process_image, 
    process_pdf, 
    process_video,
    process_batch_images
)
from utils.model_utils import ModelManager, BatchProcessor
from utils.astra_utils import (
    initialize_embeddings,
    initialize_astra,
    store_in_astra,
    search_astra
)

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Load environment variables
load_dotenv()

# Verify environment variables
def verify_environment():
    """Verify all required environment variables are set"""
    required_vars = {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "ASTRA_DB_APPLICATION_TOKEN": os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
        "ASTRA_DB_API_ENDPOINT": os.getenv("ASTRA_DB_API_ENDPOINT")
    }
    
    missing_vars = [key for key, value in required_vars.items() if not value]
    
    if missing_vars:
        st.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    return True

# Initialize components
def initialize_system():
    """Initialize system components"""
    if not verify_environment():
        st.stop()
        
    # Initialize model manager
    model_manager = ModelManager()
    
    # Initialize batch processor
    batch_processor = BatchProcessor(model_manager)
    
    # Initialize embeddings and vector store
    embeddings = initialize_embeddings()
    if embeddings:
        vector_store = initialize_astra(embeddings)
    else:
        vector_store = None
        st.error("Failed to initialize embeddings. Some features may not work.")
    
    return model_manager, batch_processor, vector_store

# Session state initialization

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = []

# Initialize system components
model_manager, batch_processor, vector_store = initialize_system()

# Sidebar UI
with st.sidebar:
    st.header("Settings and Controls")
    
    # Model selection with detailed info
    st.subheader("Model Selection")
    model = st.selectbox(
        "Select Model",
        list(model_manager.MODELS.keys())
    )
    
    # Show model details
    if model:
        config = model_manager.MODELS[model]
        st.info(f"""
        Model Details:
        - Provider: {config.provider}
        - Vision Support: {'Yes' if config.supports_vision else 'No'}
        """)
    
    # Analysis type selection
    analysis_type = st.selectbox(
        "Analysis Type",
        ["general", "technical", "educational"],
        help="Select the type of analysis to perform"
    )
    
    # Image processing settings
    st.subheader("Image Processing")
    enhancement_type = st.selectbox(
        "Enhancement Type",
        ["default", "document", "handwriting"],
        help="Select image enhancement method"
    )
    
    # Batch processing settings
    enable_batch = st.checkbox("Enable Batch Processing")
    
    if enable_batch:
        batch_size = st.number_input(
            "Batch Size", 
            min_value=2, 
            max_value=10, 
            value=5
        )
    
    # Database connection test
    if st.button("Test Database Connection"):
        if vector_store:
            try:
                search_astra(vector_store, "test", k=1)
                st.success("Database connection successful!")
            except Exception as e:
                st.error(f"Database connection failed: {str(e)}")

# Main interface
st.title("🤖 Multi-Modal Chatbot")

# File upload section
uploaded_files = st.file_uploader(
    "Upload files (Images/PDFs/Videos)",
    type=['png', 'jpg', 'jpeg', 'pdf', 'mp4'],
    accept_multiple_files=enable_batch
)

if uploaded_files:
    # Handle batch or single file processing
    if enable_batch and isinstance(uploaded_files, list):
        st.subheader("Batch Processing")
        
        # Prepare batch data
        batch_data = []
        for file in uploaded_files:
            if 'image' in file.type:
                batch_data.append({
                    'name': file.name,
                    'image': Image.open(file),
                    'enhancement_type': enhancement_type
                })
        
        if batch_data:
            # Process batch
            with st.spinner('Processing batch...'):
                results = process_batch_images(batch_data)
                
                # Analyze results with selected model
                analyzed_results = batch_processor.process_batch(
                    [{'text': r['text'], 'id': r['filename']} 
                     for r in results if 'text' in r],
                    model,
                    analysis_type
                )
                
                # Store results
                st.session_state.batch_results = analyzed_results
                
                # Display results
                st.subheader("Batch Results")
                for result in analyzed_results:
                    with st.expander(f"Result: {result['content_id']}"):
                        st.json(result)
    
    else:
        # Single file processing
        file = uploaded_files if not isinstance(uploaded_files, list) else uploaded_files[0]
        
        try:
            file_type = file.type
            st.info(f"Processing {file.name}...")
            
            if 'image' in file_type:
                # Process image
                image = Image.open(file)
                st.image(image, caption='Uploaded Image')
                
                text, confidence, stats = process_image(
                    image,
                    enhancement_type
                )
                
                if text:
                    # Use Gemini Pro for image analysis if selected
                    if model == "gemini-pro":
                        analysis = model_manager.analyze_content(
                            {'image': image, 'text': text},
                            model,
                            analysis_type
                        )
                    else:
                        # Use Groq for text analysis
                        analysis = model_manager.analyze_content(
                            {'text': text},
                            model,
                            analysis_type
                        )
                    
                    if analysis:
                        # Display results
                        st.subheader("Analysis Results")
                        st.write(analysis['analysis'])
                        
                        # Store in AstraDB
                        metadata = {
                            "file_type": "image",
                            "filename": file.name,
                            "confidence": confidence,
                            "stats": stats,
                            "model_used": model,
                            "analysis_type": analysis_type
                        }
                        
                        if store_in_astra(vector_store, text, metadata):
                            st.success("Results stored successfully!")
                
            elif 'pdf' in file_type:
                text = process_pdf(file)
                if text:
                    st.success("PDF processed successfully!")
                    
                    # Analyze with selected model
                    analysis = model_manager.analyze_content(
                        {'text': text},
                        model,
                        analysis_type
                    )
                    
                    if analysis:
                        st.subheader("Analysis Results")
                        st.write(analysis['analysis'])
            
            elif 'video' in file_type:
                result = process_video(file)
                if result:
                    st.success(result)
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# Chat interface
st.subheader("Chat Interface")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Search for relevant context
                additional_context = ""
                if vector_store:
                    with st.spinner("Searching knowledge base..."):
                        search_results = search_astra(vector_store, prompt, k=3)
                        if search_results:
                            additional_context = "\nRelevant context:\n" + \
                                "\n".join([doc.page_content for doc in search_results])
                
                # Generate response
                response = model_manager.analyze_content(
                    {
                        'text': prompt + additional_context if additional_context else prompt
                    },
                    model,
                    analysis_type
                )
                
                if response:
                    st.markdown(response['analysis'])
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response['analysis']}
                    )
                
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Built with Streamlit, LangChain, and AstraDB</p>
    </div>
    """,
    unsafe_allow_html=True
)