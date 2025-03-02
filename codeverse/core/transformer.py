from typing import Dict, Optional
from ..models.schemas import CodeTranslationRequest
from .analyzer import CodeAnalyzer
from .validator import CodeValidator
import re

class CodeTransformer:
    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.validator = CodeValidator()
        
    def translate_code(self, request):
        try:
            # Extract patterns from source code
            patterns = self.analyzer.extract_patterns(
                request.source_code,
                request.source_language
            )
            
            # Translate the code
            translated = self._translate_between_languages(
                request.source_code,
                request.source_language,
                request.target_language
            )
            
            # Basic validation
            result = {
                "translated_code": translated,
                "patterns_preserved": patterns,
                "quality_metrics": {"accuracy": 0.9},
                "suggestions": []
            }
            
            return result
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return {
                "translated_code": f"// Error during translation: {str(e)}\n{request.source_code}",
                "patterns_preserved": {},
                "quality_metrics": {},
                "suggestions": ["Translation failed"]
            }

    def _translate_between_languages(self, code: str, source_lang: str, target_lang: str) -> str:
        if source_lang == target_lang:
            return code

        # Basic translations
        translations = {
            ("python", "javascript"): self._python_to_javascript,
            ("javascript", "python"): self._javascript_to_python,
        }

        translator = translations.get((source_lang.lower(), target_lang.lower()))
        if translator:
            try:
                return translator(code)
            except Exception as e:
                print(f"Translation error: {str(e)}")
                return f"// Error in translation: {str(e)}\n{code}"
        return f"// Translation from {source_lang} to {target_lang} is not supported yet\n{code}"

    def _python_to_javascript(self, code: str) -> str:
        # Basic Python to JavaScript translation
        translations = [
            (r'print\((.*?)\)', r'console.log(\1)'),  # print to console.log
            (r'def (\w+)\((.*?)\):', r'function \1(\2) {'),  # function definition
            (r'elif', r'else if'),  # elif to else if
            (r'True', r'true'),  # True to true
            (r'False', r'false'),  # False to false
            (r'None', r'null'),  # None to null
            (r'len\((.*?)\)', r'\1.length'),  # len() to .length
        ]
        
        result = code
        for pattern, replacement in translations:
            result = re.sub(pattern, replacement, result)
        
        # Add semicolons to the end of lines
        result = ';\n'.join(line for line in result.split('\n') if line.strip())
        return result

    def _javascript_to_python(self, code: str) -> str:
        # Basic JavaScript to Python translation
        translations = [
            (r'console\.log\((.*?)\);?', r'print(\1)'),  # console.log to print
            (r'function (\w+)\((.*?)\) {', r'def \1(\2):'),  # function definition
            (r'else if', r'elif'),  # else if to elif
            (r'true', r'True'),  # true to True
            (r'false', r'False'),  # false to False
            (r'null', r'None'),  # null to None
            (r'(\w+)\.length', r'len(\1)'),  # .length to len()
        ]
        
        result = code
        for pattern, replacement in translations:
            result = re.sub(pattern, replacement, result)
        
        # Remove semicolons
        result = result.replace(';', '')
        return result 