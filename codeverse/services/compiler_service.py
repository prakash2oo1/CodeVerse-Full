import os
from pathlib import Path
import httpx
from typing import Dict, Any
import json
import asyncio
from codeverse.models.schemas import CompileRequest, CompileResponse

class CompilerService:
    def __init__(self):
        self.base_url = "https://emkc.org/api/v2/piston"
        self.headers = {
            'Content-Type': 'application/json'
        }
        
        # Language mapping for Piston API
        self.language_versions = {
            'python': 'python3',
            'javascript': 'node',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'ruby': 'ruby',
            'go': 'go',
            'rust': 'rust',
            'php': 'php'
        }

    def _get_language_specific_imports(self, language: str) -> str:
        """Get language-specific import statements and boilerplate."""
        imports = {
            'python': """
from typing import List, Dict, Any, Optional
import sys
import math
import json
import random
""",
            'javascript': """
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function input(prompt) {
    return new Promise((resolve) => {
        rl.question(prompt, (answer) => {
            resolve(answer);
        });
    });
}
""",
            'java': """
import java.util.*;
import java.io.*;
""",
            'cpp': """
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;
""",
            'c': """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
""",
            'ruby': "require 'json'\n",
            'php': "<?php\n",
            'go': """
package main
import (
    "fmt"
    "bufio"
    "os"
)
""",
            'rust': """
use std::io::{self, Write};
use std::str::FromStr;
""",
        }
        return imports.get(language.lower(), "")

    def _prepare_code_with_input(self, code: str, language: str, stdin: str = "") -> str:
        """Prepare code with proper input handling based on language."""
        base_imports = self._get_language_specific_imports(language)
        
        if language.lower() == 'python':
            return f"""{base_imports}
{code}"""
        
        elif language.lower() == 'javascript':
            return f"""{base_imports}
async function main() {{
    {code}
}}

main().then(() => rl.close());"""
        
        elif language.lower() == 'java':
            # Check if code already has a class definition
            if "class" not in code:
                return f"""{base_imports}
public class Main {{
    public static void main(String[] args) {{
        Scanner scanner = new Scanner(System.in);
        {code}
    }}
}}"""
            return f"{base_imports}\n{code}"
        
        elif language.lower() in ['cpp', 'c']:
            if "main" not in code:
                return f"""{base_imports}
int main() {{
    {code}
    return 0;
}}"""
            return f"{base_imports}\n{code}"
        
        return code

    async def compile_and_execute(self, request: CompileRequest) -> CompileResponse:
        """Compile and execute code using the Piston API."""
        try:
            language = request.language.lower()
            if language not in self.language_versions:
                return CompileResponse(
                    success=False,
                    error=f"Language {request.language} is not supported",
                    output="",
                    language=request.language
                )

            # Prepare code with proper input handling
            prepared_code = self._prepare_code_with_input(
                request.source_code,
                language,
                request.stdin
            )

            # Create submission for Piston API
            submission_data = {
                "language": self.language_versions[language],
                "version": "*",
                "files": [{
                    "content": prepared_code
                }],
                "stdin": request.stdin,
                "args": []
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/execute",
                    json=submission_data,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    return CompileResponse(
                        success=False,
                        error=f"API Error: {response.text}",
                        output="",
                        language=request.language
                    )

                result = response.json()
                
                # Check for runtime output
                if result.get("ran", False):
                    output = result.get("output", "")
                    if output:
                        return CompileResponse(
                            success=True,
                            error="",
                            output=output.strip(),
                            language=request.language
                        )
                
                # Check for compilation error
                if result.get("compile_error"):
                    return CompileResponse(
                        success=False,
                        error=f"Compilation Error: {result['compile_error']}",
                        output="",
                        language=request.language
                    )
                
                # Check for runtime error
                if result.get("run_error"):
                    return CompileResponse(
                        success=False,
                        error=f"Runtime Error: {result['run_error']}",
                        output="",
                        language=request.language
                    )

                return CompileResponse(
                    success=True,
                    error="",
                    output=result.get("output", "").strip(),
                    language=request.language
                )

        except Exception as e:
            return CompileResponse(
                success=False,
                error=str(e),
                output="",
                language=request.language
            )

    def get_supported_languages(self) -> list:
        """Get list of supported programming languages"""
        return list(self.language_versions.keys())

    def _preprocess_code(self, code: str, language: str) -> str:
        """
        Preprocess code to fix common formatting issues.
        """
        if not code:
            return code

        # Remove any BOM characters
        code = code.replace('\ufeff', '')
        
        if language == 'python':
            lines = code.split('\n')
            processed_lines = []
            
            # Track indentation level
            current_indent = 0
            indent_stack = [0]
            
            for line in lines:
                stripped = line.strip()
                if not stripped:  # Empty line
                    processed_lines.append('')
                    continue
                    
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())
                
                # Check if this line should be indented (previous line ends with ':')
                if processed_lines and processed_lines[-1].strip().endswith(':'):
                    current_indent = indent_stack[-1] + 4  # Standard Python indentation
                    indent_stack.append(current_indent)
                
                # If line starts with specific keywords, reduce indent
                if stripped.startswith(('else:', 'elif', 'except:', 'finally:', 'case')):
                    if len(indent_stack) > 1:
                        indent_stack.pop()
                    current_indent = indent_stack[-1]
                
                # Add proper indentation
                processed_lines.append(' ' * current_indent + stripped)
                
                # If line doesn't end with ':', and next line has less indentation
                if not stripped.endswith(':') and len(lines) > len(processed_lines):
                    next_line = lines[len(processed_lines)].strip()
                    if next_line and not next_line.startswith(('else:', 'elif', 'except:', 'finally:', 'case')):
                        if len(indent_stack) > 1:
                            indent_stack.pop()
                        current_indent = indent_stack[-1]
            
            return '\n'.join(processed_lines)
        
        return code