# utils/conversation.py
from typing import List, Dict
from langchain_core.messages import HumanMessage, AIMessage
from dataclasses import dataclass, field

@dataclass
class Conversation:
    """Manage conversation history"""
    messages: List[Dict] = field(default_factory=list)
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation"""
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def get_messages(self) -> List[Dict]:
        """Get all messages"""
        return self.messages
    
    def clear(self):
        """Clear conversation history"""
        self.messages = []
    
    def to_langchain_messages(self) -> List:
        """Convert messages to LangChain format"""
        return [
            HumanMessage(content=msg["content"]) 
            if msg["role"] == "user" 
            else AIMessage(content=msg["content"])
            for msg in self.messages
        ]