#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI integration
"""
import asyncio
import os
from services.genai_service import GenAIService

async def test_azure_openai():
    """Test Azure OpenAI integration"""
    print("Testing Azure OpenAI integration...")
    
    # Initialize the service
    genai_service = GenAIService()
    await genai_service.initialize()
    
    if not genai_service.azure_client:
        print("❌ Azure OpenAI client not initialized")
        return False
    
    print("✅ Azure OpenAI client initialized successfully")
    
    # Test simple chat
    try:
        response = await genai_service.chat_about_codebase(
            "What is the main purpose of this code?",
            [
                {
                    "file_path": "main.py",
                    "functions": [{"name": "main", "line": 1}],
                    "classes": [],
                    "imports": ["fastapi", "uvicorn"]
                }
            ],
            "python"
        )
        print(f"✅ Chat response received: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Chat test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Set environment variables if not already set
    if not os.getenv("AZURE_ENDPOINT"):
        os.environ["AZURE_ENDPOINT"] = "https://fintechazureopenai.openai.azure.com/"
    if not os.getenv("AZURE_API_KEY"):
        os.environ["AZURE_API_KEY"] = "2822f31331b348abb8daed1311e4070a"
    if not os.getenv("AZURE_API_VERSION"):
        os.environ["AZURE_API_VERSION"] = "2024-05-01-preview"
    if not os.getenv("AZURE_DEPLOYMENT_NAME"):
        os.environ["AZURE_DEPLOYMENT_NAME"] = "gpt-4o-mini"
    
    success = asyncio.run(test_azure_openai())
    if success:
        print("\n🎉 Azure OpenAI integration test passed!")
    else:
        print("\n❌ Azure OpenAI integration test failed!") 