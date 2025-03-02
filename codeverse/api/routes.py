from fastapi import APIRouter, HTTPException
from codeverse.models.schemas import CodeTranslationRequest, TranslationResult, CompileRequest, CompileResponse
from codeverse.services.translation_service import TranslationService
from codeverse.services.compiler_service import CompilerService

router = APIRouter()
translation_service = TranslationService()
compiler_service = CompilerService()

@router.post("/translate", response_model=TranslationResult)
async def translate_code(request: CodeTranslationRequest) -> TranslationResult:
    """
    Translate code from one programming language to another.
    
    Args:
        request (CodeTranslationRequest): The translation request containing source code and languages
        
    Returns:
        TranslationResult: The translated code
        
    Raises:
        HTTPException: If translation fails or languages are not supported
    """
    try:
        # Validate languages
        if request.source_language not in translation_service.supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Source language '{request.source_language}' is not supported. Supported languages: {translation_service.supported_languages}"
            )
            
        if request.target_language not in translation_service.supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Target language '{request.target_language}' is not supported. Supported languages: {translation_service.supported_languages}"
            )
            
        # Clean and validate the source code
        request.source_code = request.source_code.strip()
        if not request.source_code:
            raise HTTPException(
                status_code=400,
                detail="Source code cannot be empty"
            )

        # Perform the translation
        result = await translation_service.translate(request)
        
        # Validate the result
        if not result.translated_code or not result.translated_code.strip():
            raise HTTPException(
                status_code=500,
                detail="Translation failed: No code was generated"
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )

@router.get("/languages")
async def get_supported_languages():
    """Get the list of supported programming languages"""
    return {"languages": translation_service.supported_languages}

@router.post("/compile")
async def compile_code(request: CompileRequest) -> CompileResponse:
    """
    Compile and execute code using the compiler service.
    """
    try:
        # Clean up the code
        if not request.source_code:
            return CompileResponse(
                success=False,
                error="Source code cannot be empty",
                output="",
                language=request.language
            )
            
        # Remove any "# Write your code here" comments
        code_lines = [line for line in request.source_code.splitlines() if line.strip() != '# Write your code here']
        request.source_code = '\n'.join(code_lines)

        # Execute the code
        result = await compiler_service.compile_and_execute(request)
        return result
        
    except Exception as e:
        return CompileResponse(
            success=False,
            error=str(e),
            output="",
            language=request.language
        )
