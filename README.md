# Multi-Model Chatbot

A chatbot implementation using LangChain with multiple LLM providers (Groq and Gemini), featuring a Streamlit interface.

## Features
- Multiple AI model support:
  - Groq's mixtral-8x7b-32768
  - Groq's llama2-70b-4096
  - Google's Gemini Pro
- Interactive chat interface
- Conversation memory
- Dynamic model switching
- Custom prompt templates

## Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Add your API keys to `.env` file
6. Run the app: `streamlit run app.py`

## Environment Variables
Create a `.env` file with:
```env
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here