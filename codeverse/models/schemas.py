from pydantic import BaseModel
from typing import Dict, List, Optional

class CompileRequest(BaseModel):
    source_code: str
    language: str
    stdin: str = ""

class CompileResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None

class TranslateRequest(BaseModel):
    source_code: str
    source_language: str
    target_language: str

class TranslateResponse(BaseModel):
    success: bool
    translated_code: Optional[str] = None
    error: Optional[str] = None

# Alias for backward compatibility
CodeTranslationRequest = TranslateRequest
TranslationResult = TranslateResponse

class LLMConfig(BaseModel):
    model: str
    temperature: float = 0.1
    max_tokens: int = 4096
    top_p: float = 0.95
    stream: bool = True
    stop: Optional[List[str]] = None