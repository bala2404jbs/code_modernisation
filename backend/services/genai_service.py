import os
import json
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI

class GenAIService:
    def __init__(self):
        self.azure_client = None
        self.current_provider = "azure"
        
    async def initialize(self):
        """Initialize AI service with Azure OpenAI"""
        try:
            # Initialize Azure OpenAI
            azure_endpoint = os.getenv("AZURE_ENDPOINT", "https://fintechazureopenai.openai.azure.com/")
            azure_api_key = os.getenv("AZURE_API_KEY", "2822f31331b348abb8daed1311e4070a")
            azure_api_version = os.getenv("AZURE_API_VERSION", "2024-05-01-preview")
            azure_deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o-mini")
            
            print(f"Initializing Azure OpenAI with endpoint: {azure_endpoint}")
            
            self.azure_client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_version=azure_api_version,
                api_key=azure_api_key
            )
            
            # Test the connection
            try:
                response = self.azure_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                print("Azure OpenAI connection test successful")
            except Exception as test_error:
                print(f"Azure OpenAI connection test failed: {str(test_error)}")
                # Continue anyway, might be a test issue
            
            self.current_provider = "azure"
            print("GenAI service initialized with Azure OpenAI")
                
        except Exception as e:
            print(f"Failed to initialize Azure OpenAI service: {str(e)}")
            # Don't raise the exception, just log it and continue
            print("Continuing without AI service - some features will be limited")
            self.azure_client = None
    
    async def chat_about_codebase(
        self, 
        question: str, 
        ast_data: List[Dict[str, Any]], 
        source_language: str
    ) -> str:
        """Chat with AI about the codebase"""
        try:
            # if not self.azure_client:
            #     return "AI service not available. Please configure Azure OpenAI API keys."
            
            # Prepare context from AST data
            context = self._prepare_codebase_context(ast_data, source_language)
            
            # Create prompt
            prompt = self._create_chat_prompt(question, context, source_language)
            print('prompt', prompt)
            return await self._chat_with_azure(prompt)
    
        except Exception as e:
            print(f"Failed to chat about codebase: {str(e)}")
            return f"Error: {str(e)}"
    
    async def analyze_code_structure(
        self, 
        ast_data: List[Dict[str, Any]], 
        source_language: str
    ) -> Dict[str, Any]:
        """Analyze code structure and provide insights"""
        try:
            if not self.azure_client:
                return {"error": "AI service not available"}
            
            context = self._prepare_codebase_context(ast_data, source_language)
            prompt = self._create_analysis_prompt(context, source_language)
            
            response = await self._chat_with_azure(prompt)
            
            # Try to parse JSON response
            try:
                return json.loads(response)
            except:
                return {"analysis": response}
                
        except Exception as e:
            print(f"Failed to analyze code structure: {str(e)}")
            return {"error": str(e)}
    
    async def suggest_modernization(
        self, 
        ast_data: List[Dict[str, Any]], 
        source_language: str,
        target_language: str
    ) -> Dict[str, Any]:
        """Suggest modernization strategies"""
        try:
            if not self.azure_client:
                return {"error": "AI service not available"}
            
            context = self._prepare_codebase_context(ast_data, source_language)
            prompt = self._create_modernization_prompt(context, source_language, target_language)
            
            response = await self._chat_with_azure(prompt)
            
            try:
                return json.loads(response)
            except:
                return {"suggestions": response}
                
        except Exception as e:
            print(f"Failed to suggest modernization: {str(e)}")
            return {"error": str(e)}
    
    def _prepare_codebase_context(self, ast_data: List[Dict[str, Any]], source_language: str) -> str:
        """Prepare context from AST data for AI analysis"""
        context = f"Codebase in {source_language} with {len(ast_data)} files:\n\n"
        
        for i, file_data in enumerate(ast_data[:5]):  # Limit to first 5 files
            file_path = file_data.get('file_path', f'file_{i+1}')
            functions = file_data.get('functions', [])
            classes = file_data.get('classes', [])
            imports = file_data.get('imports', [])
            
            context += f"File {i+1}: {file_path}\n"
            if imports:
                context += f"  Imports: {', '.join(imports[:5])}\n"
            if functions:
                context += f"  Functions: {', '.join([f['name'] for f in functions[:3]])}\n"
            if classes:
                context += f"  Classes: {', '.join([c['name'] for c in classes[:3]])}\n"
            context += "\n"
        
        if len(ast_data) > 5:
            context += f"... and {len(ast_data) - 5} more files\n"
        
        return context
    
    def _create_chat_prompt(self, question: str, context: str, source_language: str) -> str:
        """Create a prompt for chatting about the codebase"""
        return f"""
You are an expert software engineer analyzing a {source_language} codebase.

Codebase Context:
{context}

Question: {question}

Please provide a helpful and accurate response based on the codebase context. Be specific and reference the actual code structure when possible.
"""
    
    def _create_analysis_prompt(self, context: str, source_language: str) -> str:
        """Create a prompt for code analysis"""
        return f"""
Analyze this {source_language} codebase and provide insights in JSON format:

{context}

Return a JSON object with:
- language: the programming language
- total_files: number of files analyzed
- structure: brief description of code structure and architecture
- complexity: assessment of code complexity (Low/Medium/High)
- suggestions: list of improvement suggestions
- patterns: common patterns found in the code
"""
    
    def _create_modernization_prompt(self, context: str, source_language: str, target_language: str) -> str:
        """Create a prompt for modernization suggestions"""
        return f"""
Suggest modernization strategies for converting this {source_language} codebase to {target_language}:

{context}

Return a JSON object with:
- source_language: original language
- target_language: target language
- modernization_plan: step-by-step plan for conversion
- estimated_effort: effort assessment (Low/Medium/High)
- key_changes: list of major changes needed
- dependencies: list of new dependencies required
- risks: potential risks and challenges
"""
    
    async def _chat_with_azure(self, prompt: str) -> str:
        """Chat using Azure OpenAI"""
        try:
            response = self.azure_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert software engineer and code modernization specialist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Azure OpenAI error: {str(e)}")
            return f"Error communicating with Azure OpenAI: {str(e)}"
        
    async def generate_code_explanation(self, code_snippet: str, language: str) -> str:
        """Generate explanation for a code snippet"""
        try:
            if not self.azure_client:
                return "AI service not available. Please configure Azure OpenAI API keys."
            
            prompt = f"""
Explain this {language} code snippet in detail:

```{language}
{code_snippet}
```

Provide:
1. What the code does
2. How it works
3. Key concepts and patterns used
4. Potential improvements or optimizations
5. Best practices applied or missing
"""
            
            return await self._chat_with_azure(prompt)
                        
        except Exception as e:
            print(f"Failed to generate code explanation: {str(e)}")
            return f"Error: {str(e)}" 