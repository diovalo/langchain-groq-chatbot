# setup.py
from setuptools import setup, find_packages

setup(
    name="langchain-groq-chatbot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'langchain-groq',
        'langchain-google-genai',
        'python-dotenv',
        'pillow',
        'pytesseract',
        'pypdf',
        'moviepy',
        'langchain_community',
        'sentence-transformers',
        'langchain-huggingface',
        'langchain-astradb',
    ],
)