import os
from pathlib import Path
from dotenv import load_dotenv
import json
import httpx
from codeverse.models.schemas import CodeTranslationRequest, TranslationResult

# Get the project root directory and load .env from there
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

class TranslationService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        print(f"Debug - Project root: {project_root}")
        print(f"Debug - Env path: {env_path}")
        print(f"Debug - API key exists: {bool(self.api_key)}")
        
        if not self.api_key or self.api_key == 'your_groq_api_key_here':
            raise Exception(
                "Invalid or missing GROQ_API_KEY in environment variables.\n"
                "Please follow these steps to get a valid API key:\n"
                "1. Go to https://console.groq.com/\n"
                "2. Sign up/Login to your account\n"
                "3. Go to API Keys section\n"
                "4. Create a new API key\n"
                "5. Add the key to your .env file at: {env_path}"
            )
        
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "mixtral-8x7b-32768"
        self.headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }
        self.supported_languages = [
            'python',
            'javascript',
            'java',
            'cpp',
            'c',
            'ruby',
            'php',
            'go',
            'rust',
            'swift',
            'kotlin',
            'typescript'
        ]

    def _create_translation_messages(self, source_code: str, source_lang: str, target_lang: str) -> list:
        return [
            {
                "role": "system",
                "content": f"""You are a code translator specializing in converting code between different programming languages.
Follow these guidelines:
1. Maintain the exact same functionality and logic
2. Use idiomatic {target_lang} code patterns and best practices
3. Preserve all comments and documentation
4. Keep variable names consistent unless they conflict with language keywords
5. Handle language-specific differences appropriately (e.g., array methods, string operations)
6. Ensure proper error handling and type conversions
7. Maintain the same code structure and organization
8. Preserve all input/output behavior exactly

Only return the translated code without any explanations."""
            },
            {
                "role": "user",
                "content": f"""Translate this code from {source_lang} to {target_lang}.
The code must maintain exactly the same functionality and behavior.
DO NOT add any explanations or comments beyond what's in the original code.
ONLY return the translated code.

{source_lang} code:
{source_code}

{target_lang} code:"""
            }
        ]

    async def translate(self, request: CodeTranslationRequest) -> TranslationResult:
        try:
            messages = self._create_translation_messages(
                request.source_code,
                request.source_language,
                request.target_language
            )

            print(f"Debug - Using model: {self.model}")
            print(f"Debug - Request messages: {json.dumps(messages, indent=2)}")

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 4096,
                "top_p": 0.95,
                "stream": False
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code != 200:
                    error_text = response.text
                    print(f"Debug - Error Response: {error_text}")
                    return TranslationResult(
                        success=False,
                        translated_code=None,
                        error=f"API Error: {error_text}"
                    )

                result = response.json()
                translated_code = result['choices'][0]['message']['content'].strip()

                # Clean up the response
                if "```" in translated_code:
                    code_parts = translated_code.split("```")
                    if len(code_parts) >= 2:
                        translated_code = code_parts[1].strip()
                        if translated_code.startswith(request.target_language):
                            translated_code = translated_code[len(request.target_language):].strip()

                if translated_code:
                    return TranslationResult(
                        success=True,
                        translated_code=translated_code,
                        error=None
                    )

                return TranslationResult(
                    success=False,
                    translated_code=None,
                    error="Translation failed - Empty response"
                )

        except Exception as e:
            error_msg = str(e)
            print(f"Translation error: {error_msg}")
            
            if "invalid_api_key" in error_msg.lower():
                error_msg = (
                    "Invalid API key. Please check that:\n"
                    "1. You've copied the full API key from Groq console\n"
                    "2. The API key starts with 'gsk_'\n"
                    "3. There are no extra spaces or characters\n"
                    "4. The API key is active in your Groq console"
                )
            
            return TranslationResult(
                success=False,
                translated_code=None,
                error=f"Translation error: {error_msg}"
            )

    def get_supported_languages(self) -> list:
        return self.supported_languages