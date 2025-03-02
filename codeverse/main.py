import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from codeverse.models.schemas import (
    CompileRequest, CompileResponse,
    TranslateRequest, TranslateResponse,
    CodeTranslationRequest, TranslationResult
)
from codeverse.services.compiler_service import CompilerService
from codeverse.services.translation_service import TranslationService
from codeverse.api.routes import router as api_router

app = FastAPI(
    title="CodeVerse API",
    description="API for compiling and translating code",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint to verify API is running"""
    return {
        "status": "ok",
        "message": "CodeVerse API is running",
        "version": "1.0.0"
    }

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    return {
        "languages": list(compiler_service.supported_languages.keys())
    }

@app.post("/compile", response_model=CompileResponse)
async def compile_code(request: CompileRequest):
    """Compile and run code in the specified language"""
    try:
        print(f"\nReceived compilation request:")
        print(f"Language: {request.language}")
        print(f"Input data: {request.stdin}")
        print(f"Code:\n{request.source_code}")

        # Ensure stdin is a string and handle empty input
        stdin = "John\n25" if not request.stdin else request.stdin
        
        # Create a CompileRequest object
        compile_request = CompileRequest(
            source_code=request.source_code,
            language=request.language,
            stdin=stdin
        )

        # Pass the CompileRequest object to compile_and_execute
        result = await compiler_service.compile_and_execute(compile_request)

        print(f"Compilation result: {result}")
        
        # Since result is already a CompileResponse object, just return it
        return result

    except Exception as e:
        print(f"Error in compile endpoint: {str(e)}")
        return CompileResponse(
            success=False,
            error=str(e)
        )

@app.post("/translate", response_model=TranslateResponse)
async def translate_code(request: TranslateRequest):
    """Translate code from one language to another"""
    try:
        result = await translation_service.translate(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize services
compiler_service = CompilerService()
translation_service = TranslationService()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
