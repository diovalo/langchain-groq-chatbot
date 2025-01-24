# utils/astra_utils.py
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_astradb import AstraDBVectorStore
import os
from typing import Optional, List

def initialize_embeddings() -> Optional[HuggingFaceEmbeddings]:
    """Initialize embeddings model"""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        return embeddings
    except Exception as e:
        st.error(f"Failed to initialize embeddings: {str(e)}")
        return None

def initialize_astra(embeddings: HuggingFaceEmbeddings) -> Optional[AstraDBVectorStore]:
    """Initialize AstraDB connection"""
    try:
        vector_store = AstraDBVectorStore(
            embedding=embeddings,
            collection_name="chatbot_data",
            api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
            token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
            namespace="default_keyspace"
        )
        return vector_store
    except Exception as e:
        st.error(f"Failed to initialize AstraDB: {str(e)}")
        return None

def store_in_astra(vector_store: Optional[AstraDBVectorStore], 
                  text: str, 
                  metadata: dict) -> bool:
    """Store text in AstraDB"""
    try:
        if vector_store is None:
            st.error("AstraDB not initialized")
            return False

        vector_store.add_texts(
            texts=[text],
            metadatas=[metadata]
        )
        return True
    except Exception as e:
        st.error(f"Error storing in AstraDB: {str(e)}")
        return False

def search_astra(vector_store: Optional[AstraDBVectorStore], 
                query: str, 
                k: int = 3) -> List:
    """Search AstraDB for relevant documents"""
    try:
        if vector_store is None:
            return []
            
        results = vector_store.similarity_search(query, k=k)
        return results
    except Exception as e:
        st.error(f"Error searching AstraDB: {str(e)}")
        return []