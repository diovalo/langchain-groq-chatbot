import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI  # Add this import
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Multi-Model Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.write("""
    This chatbot uses:
    - Groq's LLM
    - Google's Gemini
    - LangChain for conversation management
    - Streamlit for the user interface
    """)
    
    # Updated model selection
    model = st.selectbox(
        "Select Model",
        ["mixtral-8x7b-32768", "llama2-70b-4096", "gemini-pro"]
    )

# Initialize LLM based on selected model
if "conversation" not in st.session_state or st.session_state.current_model != model:
    st.session_state.current_model = model
    
    if model == "gemini-pro":
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7
        )
    else:
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name=model,
            temperature=0.7
        )

    # Create conversation memory
    memory = ConversationBufferMemory()

    # Define custom prompt template
    template = """You are a helpful and knowledgeable assistant.

    Current conversation:
    {history}
    Human: {input}
    Assistant:"""

    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=template
    )

    # Create conversation chain
    st.session_state.conversation = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=True
    )

# Streamlit UI
st.title("🤖 Multi-Model Chatbot")

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.conversation.predict(input=prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})