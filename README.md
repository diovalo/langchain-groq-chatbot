# Multi-Model Chatbot

A chatbot implementation using LangChain with multiple LLM providers (Groq and Gemini), featuring a Streamlit interface.

### Core Capabilities
- **Multi-Model Support**
  - Groq's Mixtral-8x7b-32768
  - Groq's Llama2-70b-4096
  - Google Gemini Pro (with vision support)
- **File Processing**
  - Image OCR with enhancement options
  - PDF text extraction
  - Video metadata analysis
  - Batch image processing
- **Conversation Features**
  - Persistent chat history
  - Context-aware responses
  - Dynamic model switching
  - Multiple analysis types (general/technical/educational)
- **Knowledge Base**
  - AstraDB vector storage
  - Contextual search capabilities
  - Metadata-rich document storage
 
## Project Structure
                       diovalo-langchain-groq-chatbot/
                       ├── app.py # Main Streamlit application
                       ├── requirements.txt # Python dependencies
                       ├── setup*.py # Environment setup scripts
                       ├── test_*.py # Component test scripts
                       └── utils/ # Core functionality modules
                          ├── astra_utils.py # Database interactions
                          ├── conversation.py # Chat history management
                          ├── file_processors.py# File processing utilities
                          └── model_utils.py # LLM management and processing

## Tech Stack

- **Frameworks**: Streamlit, LangChain
- **LLM Providers**: Groq, Google Gemini
- **Computer Vision**: OpenCV, Tesseract OCR
- **Vector DB**: AstraDB
- **PDF Processing**: PyPDF
- **Video Processing**: MoviePy

## Setup Instructions

1. **Prerequisites**
   - Python 3.9+
   - Tesseract OCR (install separately)
   - FFmpeg (for video processing)
  
2. **Installation**
   ```bash
   git clone https://github.com/yourusername/diovalo-langchain-groq-chatbot.git
   cd diovalo-langchain-groq-chatbot
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. **Environment Variables**

    **Create .env file:**

        GROQ_API_KEY=your_groq_key
        GOOGLE_API_KEY=your_gemini_key
        ASTRA_DB_APPLICATION_TOKEN=your_astra_db_token
        ASTRA_DB_API_ENDPOINT=your_astra_db_endpoint

5. **Run Application**

        streamlit run app.py

## Usage Guide

   1. **Model Selection**

        Choose between different LLMs in the sidebar

        Gemini Pro supports image analysis

  2. **File Processing**

        Upload images/PDFs/videos

        Select enhancement types for images

        Enable batch processing for multiple files

  3. **Chat Interface**

        Natural language queries

        Context-aware responses

        Conversation history maintained

  4. **Advanced Features**

        Database integration for knowledge retention

        Batch processing mode

        Technical/Educational analysis modes

## Troubleshooting

  -  **OCR Issues:** Verify Tesseract installation path in file_processors.py

  -  **Video Processing:** Ensure FFmpeg is installed system-wide

  -  **Database Errors:** Check AstraDB connection credentials

  -  **API Errors:** Verify API keys in .env file

## Contributing

 -  **Fork the repository**

 -  **Create feature branch:** git checkout -b feature/new-feature

 -  **Commit changes:** git commit -m 'Add new feature'

  - **Push to branch:** git push origin feature/new-feature

  - **Submit pull request**

