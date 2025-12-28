"""
LLM Service for model interactions
"""
from langchain_openai import ChatOpenAI
from app.config import get_settings


def get_llm():
    """Initialize and return LLM instance"""
    setting = get_settings()
    
    
    return ChatOpenAI(
        model = setting.model_name,
        api_key = setting.openrouter_api_key,
        base_url = setting.openrouter_base_url,
        temperature= setting.llm_temperature
    )
    

def get_llm_with_tools(tools: list):
    """Get LLM instance with tools bound"""
    llm = get_llm()
    return llm.bind_tools(tools)