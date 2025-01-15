import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.memory 
import ConversationBufferMemory
from langchain.chains 
import ConversationChain
from langchain.prompts 
import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Groq Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation" not in st.session_state:
    # Initialize Groq LLM
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="mixtral-8x7b-32768",  # or your preferred Groq model
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
st.title("🤖 Chatbot with LangChain and Groq")

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.write("""
    This chatbot uses:
    - Groq's LLM
    - LangChain for conversation management
    - Streamlit for the user interface
    """)
    
    # Add model selection if desired
    model = st.selectbox(
        "Select Groq Model",
        ["mixtral-8x7b-32768", "llama2-70b-4096"]
    )

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