# utils/model_utils.py
import os
import streamlit as st
from langchain_groq import ChatGroq
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory

import warnings

warnings.filterwarnings('ignore', category=UserWarning)

warnings.filterwarnings('ignore', message='.*torch.classes.*')

@dataclass
class ModelConfig:
    """Configuration for different models"""
    name: str
    provider: str
    temperature: float = 0.7
    supports_vision: bool = False

class ModelManager:
    """Manage Groq and Gemini Pro models"""
    
    # Available models configuration
    MODELS = {
        "mixtral-8x7b-32768": ModelConfig(
            name="mixtral-8x7b-32768",
            provider="groq"
        ),
        "llama-3.3-70b-versatile": ModelConfig(
            name="llama-3.3-70b-versatile",
            provider="groq"
        ),
        "gemini-pro": ModelConfig(
            name="gemini-pro",
            provider="google",
            supports_vision=True
        )
    }
    
    def __init__(self):
        """Initialize model clients"""
        self.clients = {}
        self._initialize_clients()
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
    
    def _initialize_clients(self):
        """Initialize Groq and Gemini clients"""
        # Initialize Groq
        if os.getenv("GROQ_API_KEY"):
            self.clients["groq"] = True
        
        # Initialize Gemini
        try:
            if os.getenv("GOOGLE_API_KEY"):
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                self.clients["google"] = genai
        except Exception as e:
            st.warning(f"Failed to initialize Gemini client: {str(e)}")
    
    def create_chain(self, llm):
        """Create a conversation chain with the new method"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that can analyze both text and uploaded files."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        
        chain = prompt | llm
        
        return chain
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Get initialized model by name"""
        if model_name not in self.MODELS:
            st.error(f"Unsupported model: {model_name}")
            return None
        
        config = self.MODELS[model_name]
        
        try:
            if config.provider == "groq":
                llm = ChatGroq(
                    api_key=os.getenv("GROQ_API_KEY"),
                    model_name=model_name,
                    temperature=config.temperature
                )
                return self.create_chain(llm)
            elif config.provider == "google":
                return self.clients["google"].GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"Error initializing {model_name}: {str(e)}")
            return None
    
    def process_response(self, response: Any, provider: str) -> str:
        """Process response based on provider"""
        if provider == "groq":
            return response.content
        elif provider == "google":
            return response.text
        return str(response)
    
    def analyze_content(self, 
                       content: Dict[str, Any],
                       model_name: str,
                       analysis_type: str = "general") -> Optional[Dict]:
        """Analyze content with specified model and analysis type"""
        model = self.get_model(model_name)
        if not model:
            return None
        
        # Prepare prompt based on content type and analysis type
        prompt = self._generate_prompt(content, analysis_type)
        
        try:
            config = self.MODELS[model_name]
            
            if config.provider == "groq":
                # Use the chain with memory
                response = model.invoke({
                    "input": prompt,
                    "chat_history": self.memory.load_memory_variables({})["chat_history"]
                })
                # Save to memory
                self.memory.save_context(
                    {"input": prompt},
                    {"output": response.content}
                )
                return {"analysis": response.content}
            
            elif config.provider == "google":
                # Handle both text and image content for Gemini
                if content.get('image') and config.supports_vision:
                    response = model.generate_content([prompt, content['image']])
                else:
                    response = model.generate_content(prompt)
                return {"analysis": response.text}
            
        except Exception as e:
            st.error(f"Error analyzing with {model_name}: {str(e)}")
            return None

    # Rest of the class remains the same...
    
    def _generate_prompt(self, content: Dict[str, Any], analysis_type: str) -> str:
        """Generate appropriate prompt based on content and analysis type"""
        prompts = {
            "general": """
                Analyze the following content and provide comprehensive insights:
                {content}
                
                Please provide:
                1. Main topics and concepts
                2. Key information and findings
                3. Technical details if present
                4. Context and relationships
                5. Summary and implications
            """,
            "technical": """
                Perform a technical analysis of the following content:
                {content}
                
                Focus on:
                1. Technical terms and concepts
                2. Processes or methods described
                3. Specifications or measurements
                4. Technical relationships
                5. Implementation details
            """,
            "educational": """
                Analyze the following content from an educational perspective:
                {content}
                
                Consider:
                1. Learning objectives
                2. Key concepts to understand
                3. Prerequisites and background knowledge
                4. Examples and illustrations
                5. Potential questions and exercises
            """
        }
        
        base_prompt = prompts.get(analysis_type, prompts["general"])
        
        # Handle different content types
        if isinstance(content, dict):
            if 'text' in content:
                content_str = content['text']
            elif 'image' in content:
                content_str = "[Image Content] Please analyze the provided image."
            else:
                content_str = str(content)
        else:
            content_str = str(content)
        
        return base_prompt.format(content=content_str)

class BatchProcessor:
    """Handle batch processing of content"""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    def process_batch(self,
                     contents: List[Dict],
                     model_name: str,
                     analysis_type: str = "general") -> List[Dict]:
        """Process a batch of content"""
        results = []
        
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, content in enumerate(contents):
            try:
                status_text.text(f"Processing item {idx + 1}/{len(contents)}")
                
                # Analyze content
                analysis = self.model_manager.analyze_content(
                    content,
                    model_name,
                    analysis_type
                )
                
                results.append({
                    "content_id": content.get('id', f"item_{idx}"),
                    "analysis": analysis,
                    "status": "success" if analysis else "failed"
                })
                
                # Update progress
                progress_bar.progress((idx + 1) / len(contents))
                
            except Exception as e:
                results.append({
                    "content_id": content.get('id', f"item_{idx}"),
                    "error": str(e),
                    "status": "error"
                })
        
        status_text.text("Batch processing complete!")
        return results