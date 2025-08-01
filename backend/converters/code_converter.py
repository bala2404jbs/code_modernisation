import os
import json
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path
from services.genai_service import GenAIService

class CodeConverter:
    def __init__(self):
        self.genai_service = GenAIService()
        self.supported_conversions = {
            'python': ['python', 'java', 'javascript', 'typescript', 'go', 'rust'],
            'java': ['java', 'python', 'javascript', 'typescript', 'go', 'rust'],
            'javascript': ['javascript', 'python', 'java', 'typescript', 'go', 'rust'],
            'typescript': ['typescript', 'python', 'java', 'javascript', 'go', 'rust'],
            'cobol': ['cobol', 'python', 'java', 'javascript', 'typescript'],
            'cpp': ['cpp', 'python', 'java', 'javascript', 'typescript', 'go', 'rust'],
            'c': ['c', 'python', 'java', 'javascript', 'typescript', 'go', 'rust'],
            'php': ['php', 'python', 'java', 'javascript', 'typescript'],
            'ruby': ['ruby', 'python', 'java', 'javascript', 'typescript'],
            'go': ['go', 'python', 'java', 'javascript', 'typescript', 'rust'],
            'rust': ['rust', 'python', 'java', 'javascript', 'typescript', 'go']
        }
        
    async def initialize(self):
        """Initialize the code converter"""
        try:
            await self.genai_service.initialize()
            print("Code Converter initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Code Converter: {str(e)}")
            raise
    
    async def convert_code(
        self, 
        ast_data: List[Dict[str, Any]], 
        source_language: str, 
        target_language: str,
        source_framework: Optional[str] = None,
        target_framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """Convert code from source language to target language"""
        try:
            if not self._is_conversion_supported(source_language, target_language):
                raise ValueError(f"Conversion from {source_language} to {target_language} is not supported")
            
            converted_files = []
            all_dependencies = {}
            
            # Convert each file individually
            for file_data in ast_data:
                file_path = file_data.get("file_path", "unknown")
                print(f"Converting file: {file_path}")
                
                try:
                    # Prepare source code for this specific file
                    source_code = self._prepare_single_file_code(file_data, source_language)
                    
                    # Generate conversion prompt for this file
                    prompt = self._create_single_file_conversion_prompt(
                        source_code, 
                        source_language, 
                        target_language, 
                        file_path,
                        source_framework,
                        target_framework
                    )
                    
                    # Get AI response for this file
                    converted_code = await self.genai_service._chat_with_azure(prompt)
                    
                    # Parse the converted code for this file
                    parsed_conversion = self._parse_single_file_conversion(
                        converted_code, 
                        target_language, 
                        file_path,
                        target_framework
                    )
                    
                    if parsed_conversion:
                        converted_files.append(parsed_conversion)
                        # Merge dependencies
                        file_deps = parsed_conversion.get("dependencies", {})
                        all_dependencies.update(file_deps)
                        print(f"Successfully converted: {file_path}")
                    else:
                        print(f"Failed to convert: {file_path} - no valid content extracted")
                        
                except Exception as e:
                    print(f"Error converting file {file_path}: {str(e)}")
                    # Continue with other files instead of failing completely
                    continue
            
            # Create startup files based on target language and framework
            startup_files = await self._create_startup_files(target_language, target_framework, converted_files)
            converted_files.extend(startup_files)
            
            # Generate dependencies with framework support
            dependencies = await self.generate_dependencies(target_language, {
                "converted_files": converted_files
            }, target_framework)
            
            result = {
                "source_language": source_language,
                "source_framework": source_framework,
                "target_language": target_language,
                "target_framework": target_framework,
                "converted_files": [
                    {
                        "filename": file_data["filename"],
                        "content": file_data["content"]
                    }
                    for file_data in converted_files
                ],
                "dependencies": dependencies,
                "conversion_notes": f"Converted {len(converted_files)} files from {source_language} to {target_language}"
            }
            
            print(f'Conversion result: {len(converted_files)} files converted')
            return result
            
        except Exception as e:
            print(f"Failed to convert code: {str(e)}")
            raise
    
    async def generate_dependencies(self, target_language: str, converted_code: Dict[str, Any], target_framework: Optional[str] = None) -> Dict[str, Any]:
        """Generate dependencies file for target language"""
        try:
            dependencies = self._get_default_dependencies(target_language, target_framework)
            
            # Analyze converted code to add specific dependencies
            for file_data in converted_code.get("converted_files", []):
                content = file_data.get("content", "")
                file_deps = self._analyze_file_dependencies(content, target_language)
                dependencies.update(file_deps)
            
            return dependencies
            
        except Exception as e:
            print(f"Failed to generate dependencies: {str(e)}")
            return self._get_default_dependencies(target_language)
    
    async def save_converted_code(
        self, 
        output_dir: str, 
        converted_code: Dict[str, Any], 
        dependencies: Dict[str, Any]
    ):
        """Save converted code to local directory"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Save converted files
            for file_data in converted_code.get("converted_files", []):
                file_path = os.path.join(output_dir, file_data["filename"])
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_data["content"])
            
            # Save dependencies file
            deps_file = self._get_dependencies_filename(converted_code.get("target_language", "unknown"))
            deps_path = os.path.join(output_dir, deps_file)
            
            with open(deps_path, 'w', encoding='utf-8') as f:
                if deps_file.endswith('.json'):
                    json.dump(dependencies, f, indent=2)
                elif deps_file.endswith('.txt'):
                    for dep, version in dependencies.items():
                        f.write(f"{dep}=={version}\n")
                elif deps_file.endswith('.toml'):
                    f.write("[dependencies]\n")
                    for dep, version in dependencies.items():
                        f.write(f'{dep} = "{version}"\n')
                elif deps_file == 'pom.xml':
                    # Generate proper Maven pom.xml for Spring Boot
                    pom_content = self._generate_spring_boot_pom_xml(dependencies, converted_code)
                    f.write(pom_content)
            
            # Save conversion notes
            notes_path = os.path.join(output_dir, "CONVERSION_NOTES.md")
            with open(notes_path, 'w', encoding='utf-8') as f:
                f.write("# Code Conversion Notes\n\n")
                f.write(f"**Source Language:** {converted_code.get('source_language', 'unknown')}\n")
                f.write(f"**Target Language:** {converted_code.get('target_language', 'unknown')}\n\n")
                f.write("## Conversion Summary\n\n")
                f.write(converted_code.get("conversion_notes", "No notes available."))
            
            print(f"Converted code saved to {output_dir}")
            
        except Exception as e:
            print(f"Failed to save converted code: {str(e)}")
            raise
    
    def _is_conversion_supported(self, source_language: str, target_language: str) -> bool:
        """Check if conversion is supported"""
        source_lang = source_language.lower()
        target_lang = target_language.lower()
        
        return (source_lang in self.supported_conversions and 
                target_lang in self.supported_conversions[source_lang])
    
    def _prepare_source_code(self, ast_data: List[Dict[str, Any]]) -> str:
        """Prepare source code from AST data for conversion"""
        code_parts = []
        
        for file_data in ast_data:
            file_path = file_data.get("file_path", "unknown")
            imports = file_data.get("imports", [])
            functions = file_data.get("functions", [])
            classes = file_data.get("classes", [])
            variables = file_data.get("variables", [])
            
            file_content = f"// File: {file_path}\n"
            
            # Add imports
            for imp in imports:
                file_content += f"{imp}\n"
            
            file_content += "\n"
            
            # Add classes
            for cls in classes:
                file_content += f"// Class: {cls.get('name', 'unknown')}\n"
                file_content += f"class {cls.get('name', 'unknown')} {{\n"
                file_content += "    // Class implementation\n"
                file_content += "}\n\n"
            
            # Add functions
            for func in functions:
                file_content += f"// Function: {func.get('name', 'unknown')}\n"
                file_content += f"function {func.get('name', 'unknown')}() {{\n"
                file_content += "    // Function implementation\n"
                file_content += "}\n\n"
            
            code_parts.append(file_content)
        
        return "\n".join(code_parts)
    
    def _create_conversion_prompt(self, source_code: str, source_language: str, target_language: str) -> str:
        """Create prompt for code conversion"""
        return f"""
Convert this {source_language} code to {target_language}. 

Provide the converted code in the following JSON format:
{{
    "files": [
        {{
            "filename": "main.{self._get_file_extension(target_language)}",
            "content": "// Write actual {target_language} code here, NOT JSON or markdown"
        }}
    ],
    "dependencies": {{
        "dependency_name": "version"
    }},
    "notes": "conversion notes and important changes"
}}

Source code:
```{source_language}
{source_code}
```

Important conversion guidelines:
1. Maintain the same functionality
2. Use {target_language} best practices
3. Handle language-specific features appropriately
4. Include proper imports and dependencies
5. Add comments explaining major changes
6. The "content" field should contain ONLY {target_language} code, not JSON or markdown
7. Provide clean, executable {target_language} code
8. Do NOT wrap the content in JSON strings or markdown code blocks
9. Write the code directly in the content field as plain {target_language} code

Example of what the content field should look like:
"content": "import logging\\n\\nclass MyClass:\\n    def __init__(self):\\n        pass"

Provide only the JSON response, no additional text. The content field should be pure {target_language} code with escaped newlines.
"""
    
    def _parse_converted_code(self, ai_response: str, target_language: str) -> Dict[str, Any]:
        """Parse AI response into structured converted code"""
        try:
            print(f"Parsing AI response for {target_language}")
            print(f"Response length: {len(ai_response)}")
            print(f"Response preview: {ai_response[:200]}...")
            
            # Try to extract JSON from response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = ai_response[start_idx:end_idx]
                print(f"Extracted JSON string length: {len(json_str)}")
                
                parsed = json.loads(json_str)
                print(f"Successfully parsed JSON with keys: {list(parsed.keys())}")
                
                # Extract the actual code content from the JSON structure
                files = parsed.get("files", [])
                if files and len(files) > 0:
                    # Get the content from the first file
                    first_file = files[0]
                    content = first_file.get("content", "")
                    print(f"Extracted content length: {len(content)}")
                    print(f"Content preview: {content[:200]}...")
                    
                    # If content is still JSON, try to extract the actual code
                    if content.startswith('```'):
                        # Extract code from markdown code blocks
                        lines = content.split('\n')
                        code_lines = []
                        in_code_block = False
                        
                        for line in lines:
                            if line.startswith('```'):
                                in_code_block = not in_code_block
                                continue
                            if in_code_block:
                                code_lines.append(line)
                        
                        content = '\n'.join(code_lines)
                        print(f"Extracted code from markdown blocks, length: {len(content)}")
                    
                    # If content contains escaped newlines, unescape them
                    if '\\n' in content:
                        content = content.replace('\\n', '\n')
                        print("Unescaped newlines in content")
                    
                    return {
                        "files": [{
                            "filename": f"main.{self._get_file_extension(target_language)}",
                            "content": content
                        }],
                        "dependencies": parsed.get("dependencies", {}),
                        "notes": parsed.get("notes", "Conversion completed")
                    }
                else:
                    print("No files found in JSON response")
                    # No files in JSON, use the entire response as content
                    return {
                        "files": [{
                            "filename": f"main.{self._get_file_extension(target_language)}",
                            "content": ai_response
                        }],
                        "dependencies": parsed.get("dependencies", {}),
                        "notes": "No files found in JSON response"
                    }
            else:
                print("Could not find JSON structure in response")
                # Fallback: create basic structure
                return {
                    "files": [{
                        "filename": f"main.{self._get_file_extension(target_language)}",
                        "content": ai_response
                    }],
                    "dependencies": {},
                    "notes": "AI response could not be parsed as JSON"
                }
                
        except Exception as e:
            print(f"Failed to parse converted code: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            return {
                "files": [{
                    "filename": f"main.{self._get_file_extension(target_language)}",
                    "content": ai_response
                }],
                "dependencies": {},
                "notes": f"Error parsing response: {str(e)}"
            }
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for target language"""
        extensions = {
            'python': 'py',
            'java': 'java',
            'javascript': 'js',
            'typescript': 'ts',
            'go': 'go',
            'rust': 'rs',
            'cpp': 'cpp',
            'c': 'c'
        }
        return extensions.get(language.lower(), 'txt')
    
    def _get_default_dependencies(self, language: str, target_framework: Optional[str] = None) -> Dict[str, str]:
        """Get default dependencies for target language"""
        if language.lower() == 'java' and target_framework in ['spring', 'spring_boot']:
            return {
                'spring-boot-starter-web': '3.2.0',
                'spring-boot-starter-data-jpa': '3.2.0',
                'spring-boot-starter-security': '3.2.0',
                'spring-boot-starter-thymeleaf': '3.2.0',
                'spring-boot-devtools': '3.2.0',
                'spring-boot-starter-test': '3.2.0',
                'junit-jupiter': '5.9.2',
                'slf4j-api': '2.0.7',
                'logback-classic': '1.4.7'
            }
        
        dependencies = {
            'python': {
                'requests': '2.31.0',
                'pydantic': '2.5.0'
            },
            'java': {
                'junit': '5.9.2',
                'slf4j': '2.0.7'
            },
            'javascript': {
                'axios': '1.6.0',
                'lodash': '4.17.21'
            },
            'typescript': {
                '@types/node': '20.8.0',
                'typescript': '5.2.0'
            },
            'go': {
                'github.com/gorilla/mux': 'v1.8.0'
            },
            'rust': {
                'serde': '1.0',
                'tokio': '1.0'
            }
        }
        return dependencies.get(language.lower(), {})
    
    def _analyze_file_dependencies(self, content: str, language: str) -> Dict[str, str]:
        """Analyze file content to determine dependencies"""
        dependencies = {}
        
        if language.lower() == 'python':
            if 'import requests' in content or 'from requests' in content:
                dependencies['requests'] = '2.31.0'
            if 'import json' in content:
                dependencies['json'] = 'builtin'
            if 'import asyncio' in content:
                dependencies['asyncio'] = 'builtin'
        
        elif language.lower() == 'javascript':
            if 'require(' in content or 'import ' in content:
                if 'axios' in content:
                    dependencies['axios'] = '1.6.0'
                if 'lodash' in content:
                    dependencies['lodash'] = '4.17.21'
        
        elif language.lower() == 'java':
            if 'import java.util' in content:
                dependencies['java.util'] = 'builtin'
            if 'import org.junit' in content:
                dependencies['junit'] = '5.9.2'
        
        return dependencies
    
    def _get_dependencies_filename(self, language: str) -> str:
        """Get dependencies filename for target language"""
        filenames = {
            'python': 'requirements.txt',
            'java': 'pom.xml',
            'javascript': 'package.json',
            'typescript': 'package.json',
            'go': 'go.mod',
            'rust': 'Cargo.toml'
        }
        return filenames.get(language.lower(), 'dependencies.txt')

    def _get_framework_directory_structure(self, target_language: str, target_framework: str, original_path: str) -> str:
        """Generate proper directory structure based on target framework"""
        if not target_framework or target_framework == "none":
            return original_path
        
        # Extract filename from original path
        filename = os.path.basename(original_path)
        name_without_ext = os.path.splitext(filename)[0]
        extension = self._get_file_extension(target_language)
        
        # Framework-specific directory structures
        if target_language == "java":
            if target_framework == "spring":
                # Spring Boot structure: src/main/java/com/example/project/
                return f"src/main/java/com/example/{name_without_ext.lower()}/{filename}"
            elif target_framework == "spring_boot":
                return f"src/main/java/com/example/{name_without_ext.lower()}/{filename}"
            elif target_framework == "jakarta_ee":
                return f"src/main/java/com/example/{name_without_ext.lower()}/{filename}"
            else:
                return f"src/{filename}"
        
        elif target_language == "python":
            if target_framework == "django":
                # Django structure: app_name/models.py, views.py, etc.
                return f"django_app/{filename}"
            elif target_framework == "flask":
                return f"flask_app/{filename}"
            elif target_framework == "fastapi":
                return f"fastapi_app/{filename}"
            else:
                return f"src/{filename}"
        
        elif target_language == "javascript":
            if target_framework == "react":
                return f"src/components/{filename}"
            elif target_framework == "vue":
                return f"src/components/{filename}"
            elif target_framework == "angular":
                return f"src/app/{filename}"
            elif target_framework == "express":
                return f"src/{filename}"
            else:
                return f"src/{filename}"
        
        elif target_language == "typescript":
            if target_framework == "react":
                return f"src/components/{filename}"
            elif target_framework == "vue":
                return f"src/components/{filename}"
            elif target_framework == "angular":
                return f"src/app/{filename}"
            else:
                return f"src/{filename}"
        
        elif target_language == "php":
            if target_framework == "laravel":
                return f"app/{filename}"
            elif target_framework == "symfony":
                return f"src/{filename}"
            else:
                return f"src/{filename}"
        
        elif target_language == "ruby":
            if target_framework == "rails":
                return f"app/{filename}"
            else:
                return f"src/{filename}"
        
        else:
            # Default structure for other languages
            return f"src/{filename}"

    def _generate_spring_boot_pom_xml(self, dependencies: Dict[str, str], converted_code: Dict[str, Any]) -> str:
        """Generate proper Maven pom.xml for Spring Boot project"""
        pom_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>

    <groupId>com.example</groupId>
    <artifactId>converted-spring-boot-app</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>

    <name>Converted Spring Boot Application</name>
    <description>Spring Boot application converted from J2EE</description>

    <properties>
        <java.version>17</java.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>'''

        # Add dependencies
        for dep, version in dependencies.items():
            if dep.startswith('spring-boot'):
                pom_xml += f'''
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>{dep}</artifactId>
        </dependency>'''
            else:
                pom_xml += f'''
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>{dep}</artifactId>
            <version>{version}</version>
            <scope>test</scope>
        </dependency>'''

        pom_xml += '''
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>'''
        return pom_xml

    def _prepare_single_file_code(self, file_data: Dict[str, Any], source_language: str) -> str:
        """Prepare source code for a single file"""
        file_path = file_data.get("file_path", "unknown")
        imports = file_data.get("imports", [])
        functions = file_data.get("functions", [])
        classes = file_data.get("classes", [])
        variables = file_data.get("variables", [])
        full_source_code = file_data.get("full_source_code", "")
        
        # If we have the full source code, use it
        if full_source_code:
            return full_source_code
        
        # Otherwise, reconstruct from AST components
        code_parts = []
        
        # Add imports
        for imp in imports:
            if source_language == "java":
                code_parts.append(f"import {imp};")
            elif source_language in ["javascript", "typescript"]:
                code_parts.append(f"import {imp};")
            else:
                code_parts.append(f"import {imp}")
        
        code_parts.append("")
        
        # Add classes
        for cls in classes:
            class_name = cls.get('name', 'unknown')
            full_code = cls.get('full_code', '')
            
            if full_code:
                code_parts.append(full_code)
            else:
                # Fallback to basic class structure
                if source_language == "java":
                    code_parts.append(f"public class {class_name} {{")
                    code_parts.append("    // Class implementation")
                    code_parts.append("}")
                elif source_language in ["javascript", "typescript"]:
                    code_parts.append(f"class {class_name} {{")
                    code_parts.append("    // Class implementation")
                    code_parts.append("}")
                else:
                    code_parts.append(f"class {class_name}:")
                    code_parts.append("    # Class implementation")
                    code_parts.append("    pass")
            
            code_parts.append("")
        
        # Add functions
        for func in functions:
            func_name = func.get('name', 'unknown')
            full_code = func.get('full_code', '')
            
            if full_code:
                code_parts.append(full_code)
            else:
                # Fallback to basic function structure
                if source_language == "java":
                    code_parts.append(f"public void {func_name}() {{")
                    code_parts.append("    // Function implementation")
                    code_parts.append("}")
                elif source_language in ["javascript", "typescript"]:
                    code_parts.append(f"function {func_name}() {{")
                    code_parts.append("    // Function implementation")
                    code_parts.append("}")
                else:
                    code_parts.append(f"def {func_name}():")
                    code_parts.append("    # Function implementation")
                    code_parts.append("    pass")
            
            code_parts.append("")
        
        return "\n".join(code_parts)
    
    def _create_single_file_conversion_prompt(
        self, 
        source_code: str, 
        source_language: str, 
        target_language: str, 
        file_path: str,
        source_framework: Optional[str] = None,
        target_framework: Optional[str] = None
    ) -> str:
        """Create prompt for converting a single file"""
        # Determine the target filename based on the original file path
        original_name = os.path.splitext(os.path.basename(file_path))[0]
        target_extension = self._get_file_extension(target_language)
        target_filename = f"{original_name}.{target_extension}"
        
        # Add framework information to the prompt
        framework_info = ""
        if source_framework and source_framework != "none":
            framework_info += f"\nSource Framework: {source_framework}"
        if target_framework and target_framework != "none":
            framework_info += f"\nTarget Framework: {target_framework}"
        
        # Handle same-language conversions
        if source_language == target_language:
            conversion_type = "modernize and refactor"
            if source_framework != target_framework:
                conversion_type = f"convert from {source_framework} to {target_framework} framework"
        else:
            conversion_type = f"convert from {source_language} to {target_language}"
        
        # Generate target directory structure
        target_directory = ""
        if target_framework and target_framework != "none":
            target_directory = self._get_framework_directory_structure(target_language, target_framework, file_path)
            target_filename = os.path.basename(target_directory)
        else:
            target_filename = os.path.splitext(os.path.basename(file_path))[0] + self._get_file_extension(target_language)

        return f"""
{conversion_type.title()} this {source_language} file.{framework_info}

Original file: {file_path}
Target file: {target_filename}
Target directory structure: {target_directory if target_directory else "Standard structure"}

IMPORTANT: You must respond with ONLY valid JSON. No additional text, no explanations outside the JSON.

Required JSON format:
{{
    "filename": "{target_filename}",
    "content": "// Your {target_language} code here - write actual code, not JSON strings",
    "dependencies": {{
        "package_name": "version"
    }},
    "notes": "Brief conversion notes"
}}

Source code:
```{source_language}
{source_code}
```

Conversion rules:
1. Write ONLY valid {target_language} code in the "content" field
2. Do NOT wrap code in quotes or markdown blocks
3. Use proper {target_language} syntax and best practices
4. Include necessary imports and dependencies
5. Maintain the original functionality
6. Add comments for major changes
7. Ensure the JSON is properly formatted with escaped quotes and newlines
8. If converting between frameworks, adapt the code to use the target framework's patterns and conventions
9. Include framework-specific dependencies and imports when applicable
10. For same-language conversions, focus on code modernization, best practices, and framework-specific improvements
11. Follow the target framework's directory structure and naming conventions

Example of correct content field:
"content": "import os\\nimport sys\\n\\ndef main():\\n    print('Hello World')\\n\\nif __name__ == '__main__':\\n    main()"

Respond with ONLY the JSON object, no other text.
""" 

    def _parse_single_file_conversion(
        self, 
        ai_response: str, 
        target_language: str, 
        original_file_path: str,
        target_framework: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Parse AI response for a single file conversion"""
        try:
            print(f"Parsing single file conversion for {original_file_path}")
            print(f"Response length: {len(ai_response)}")
            print(f"Response preview: {ai_response[:200]}...")
            
            # Try multiple strategies to extract valid JSON
            json_data = None
            
            # Strategy 1: Try to find and parse JSON directly
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = ai_response[start_idx:end_idx]
                print(f"Extracted JSON string length: {len(json_str)}")
                
                try:
                    json_data = json.loads(json_str)
                    print(f"Successfully parsed JSON with keys: {list(json_data.keys())}")
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Problematic JSON: {json_str[:500]}...")
                    
                    # Strategy 2: Try to fix common JSON issues
                    fixed_json = self._fix_common_json_issues(json_str)
                    try:
                        json_data = json.loads(fixed_json)
                        print(f"Successfully parsed fixed JSON")
                    except json.JSONDecodeError as e2:
                        print(f"Fixed JSON still has errors: {e2}")
                        json_data = None
            
            # Strategy 3: If JSON parsing fails, try to extract content manually
            if json_data is None:
                print("JSON parsing failed, trying manual extraction...")
                json_data = self._extract_content_manually(ai_response, target_language, original_file_path)
            
            if json_data:
                # Extract the filename and content
                filename = json_data.get("filename", "")
                content = json_data.get("content", "")
                dependencies = json_data.get("dependencies", {})
                notes = json_data.get("notes", "")
                
                print(f"Extracted filename: {filename}")
                print(f"Content length: {len(content)}")
                print(f"Content preview: {content[:200]}...")
                
                # If content contains escaped newlines, unescape them
                if '\\n' in content:
                    content = content.replace('\\n', '\n')
                    print("Unescaped newlines in content")
                
                # Validate that we have content
                if not content.strip():
                    print("Warning: No content found in conversion")
                    return None
                
                # Generate proper directory structure based on framework
                if target_framework:
                    framework_path = self._get_framework_directory_structure(target_language, target_framework, original_file_path)
                    filename = framework_path
                    print(f"Generated framework path: {filename}")
                
                return {
                    "filename": filename,
                    "content": content,
                    "dependencies": dependencies,
                    "notes": notes
                }
            else:
                print("Could not extract valid data from response")
                return None
                
        except Exception as e:
            print(f"Failed to parse single file conversion: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            return None
    
    def _fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues"""
        try:
            # Fix unescaped quotes in content
            import re
            
            # Find content field and fix quotes
            content_pattern = r'"content":\s*"([^"]*(?:\\.[^"]*)*)"'
            match = re.search(content_pattern, json_str)
            
            if match:
                content_start = match.start(1)
                content_end = match.end(1)
                
                # Extract content and fix it
                content = json_str[content_start:content_end]
                
                # Fix common issues
                content = content.replace('"', '\\"')  # Escape quotes
                content = content.replace('\n', '\\n')  # Escape newlines
                content = content.replace('\t', '\\t')  # Escape tabs
                
                # Replace the content in the JSON
                json_str = json_str[:content_start] + content + json_str[content_end:]
            
            # Fix trailing commas
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            # Fix missing quotes around property names
            json_str = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', json_str)
            
            return json_str
            
        except Exception as e:
            print(f"Error fixing JSON: {e}")
            return json_str
    
    def _extract_content_manually(self, ai_response: str, target_language: str, original_file_path: str) -> Optional[Dict[str, Any]]:
        """Extract content manually when JSON parsing fails"""
        try:
            # Try to extract filename from original path
            original_name = os.path.splitext(os.path.basename(original_file_path))[0]
            target_extension = self._get_file_extension(target_language)
            filename = f"{original_name}.{target_extension}"
            
            # Try to find code blocks in the response
            code_blocks = []
            
            # Look for markdown code blocks
            import re
            code_block_pattern = rf'```{target_language}?\s*\n(.*?)\n```'
            matches = re.findall(code_block_pattern, ai_response, re.DOTALL)
            code_blocks.extend(matches)
            
            # Look for code blocks without language specification
            generic_pattern = r'```\s*\n(.*?)\n```'
            matches = re.findall(generic_pattern, ai_response, re.DOTALL)
            code_blocks.extend(matches)
            
            # If no code blocks found, try to extract content after "content:" or similar
            if not code_blocks:
                content_patterns = [
                    r'"content":\s*"([^"]*(?:\\.[^"]*)*)"',
                    r'content:\s*"([^"]*(?:\\.[^"]*)*)"',
                    r'content:\s*`([^`]*)`',
                    r'content:\s*"""([^"]*)"""',
                ]
                
                for pattern in content_patterns:
                    match = re.search(pattern, ai_response, re.DOTALL)
                    if match:
                        content = match.group(1)
                        # Unescape common escape sequences
                        content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
                        code_blocks.append(content)
                        break
            
            if code_blocks:
                content = code_blocks[0]  # Use the first code block found
                print(f"Manually extracted content with length: {len(content)}")
                
                return {
                    "filename": filename,
                    "content": content,
                    "dependencies": {},
                    "notes": f"Manually extracted from AI response for {original_file_path}"
                }
            
            print("No code content found in response")
            return None
            
        except Exception as e:
            print(f"Error in manual extraction: {e}")
            return None

    async def _create_startup_files(self, target_language: str, target_framework: Optional[str], converted_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create startup files for the target language if they don't exist."""
        startup_files = []
        
        # Check if startup files already exist
        existing_startup_files = []
        for file_data in converted_files:
            filename = file_data["filename"].lower()
            if (target_language == 'python' and (filename == 'main.py' or filename == 'manage.py' or filename == 'start.py')) or \
               (target_language == 'java' and filename == 'main.java') or \
               (target_language == 'javascript' and filename == 'index.js') or \
               (target_language == 'typescript' and filename == 'index.ts') or \
               (target_language == 'go' and filename == 'main.go') or \
               (target_language == 'rust' and filename == 'main.rs'):
                existing_startup_files.append(filename)
        
        if existing_startup_files:
            print(f"Startup files already exist: {existing_startup_files}")
            return startup_files
        
        # Create startup file based on target language and framework
        startup_file_info = self._get_startup_file_info(target_language, target_framework)
        if not startup_file_info:
            print(f"No startup file configuration for {target_language}")
            return startup_files
        
        filename, template = startup_file_info
        
        try:
            # Create startup file using AI
            prompt = self._create_startup_file_prompt(target_language, target_framework, filename, template)
            ai_response = await self.genai_service._chat_with_azure(prompt)
            
            # For Spring Boot, place Main.java in the root of src/main/java
            if target_language == 'java' and target_framework in ['spring', 'spring_boot']:
                startup_filename = "src/main/java/Main.java"
            else:
                startup_filename = filename
                
            parsed_startup_file = self._parse_single_file_conversion(
                ai_response, 
                target_language, 
                f"startup_{filename}",
                target_framework
            )
            
            if parsed_startup_file:
                # Update filename for Spring Boot
                if target_language == 'java' and target_framework in ['spring', 'spring_boot']:
                    parsed_startup_file["filename"] = startup_filename
            
            if parsed_startup_file:
                startup_files.append(parsed_startup_file)
                print(f"Created startup file: {filename}")
            else:
                print(f"Failed to create startup file: {filename}")
                
        except Exception as e:
            print(f"Error creating startup file: {str(e)}")
        
        return startup_files
    
    def _get_startup_file_info(self, target_language: str, target_framework: Optional[str] = None) -> Optional[tuple]:
        """Get startup file information for target language"""
        if target_language.lower() == 'java':
            if target_framework in ['spring', 'spring_boot']:
                return ('Main.java', self._get_java_startup_template())
            else:
                return ('Main.java', self._get_java_startup_template())
        
        startup_files = {
            'python': ('main.py', self._get_python_startup_template()),
            'javascript': ('index.js', self._get_javascript_startup_template()),
            'typescript': ('index.ts', self._get_typescript_startup_template()),
            'go': ('main.go', self._get_go_startup_template()),
            'rust': ('main.rs', self._get_rust_startup_template())
        }
        return startup_files.get(target_language.lower())
    
    def _create_startup_file_prompt(self, target_language: str, target_framework: Optional[str], filename: str, template: str) -> str:
        """Create prompt for startup file generation"""
        framework_info = ""
        if target_framework and target_framework != "none":
            framework_info = f" using {target_framework} framework"
        
        return f"""
Create a startup file for a {target_language} application{framework_info}.

Filename: {filename}

Provide the startup file content in the following JSON format:
{{
    "filename": "{filename}",
    "content": "// Write actual {target_language} code here, NOT JSON or markdown",
    "dependencies": {{
        "dependency_name": "version"
    }},
    "notes": "Startup file for {target_language} application{framework_info}"
}}

Template/Example:
```{target_language}
{template}
```

Important guidelines:
1. Create a simple, runnable startup file
2. Use {target_language} best practices
3. Include proper imports and dependencies
4. Make it easy to run the application
5. The "content" field should contain ONLY {target_language} code, not JSON or markdown
6. Provide clean, executable {target_language} code
7. If using a framework, include framework-specific initialization and configuration
8. Include framework-specific dependencies when applicable
9. For framework-specific startup files, include proper framework initialization and configuration

Provide only the JSON response, no additional text. The content field should be pure {target_language} code with escaped newlines.
"""
    
    def _get_python_startup_template(self) -> str:
        return '''#!/usr/bin/env python3
"""
Main startup file for the application
"""
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        logger.info("Starting application...")
        
        # Add your application initialization here
        logger.info("Application started successfully")
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()'''
    
    def _get_java_startup_template(self) -> str:
        return '''import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SpringBootApplication
public class Main {
    private static final Logger logger = LoggerFactory.getLogger(Main.class);
    
    public static void main(String[] args) {
        try {
            logger.info("Starting Spring Boot application...");
            SpringApplication.run(Main.class, args);
            logger.info("Spring Boot application started successfully");
        } catch (Exception e) {
            logger.error("Spring Boot application failed to start", e);
            System.exit(1);
        }
    }
}'''
    
    def _get_javascript_startup_template(self) -> str:
        return '''#!/usr/bin/env node
/**
 * Main startup file for the application
 */
const logger = console;

function main() {
    try {
        logger.info("Starting application...");
        
        // Add your application initialization here
        logger.info("Application started successfully");
        
    } catch (error) {
        logger.error("Application failed to start:", error);
        process.exit(1);
    }
}

main();'''
    
    def _get_typescript_startup_template(self) -> str:
        return '''#!/usr/bin/env node
/**
 * Main startup file for the application
 */
import { Logger } from './logger';

const logger = new Logger();

async function main(): Promise<void> {
    try {
        logger.info("Starting application...");
        
        // Add your application initialization here
        logger.info("Application started successfully");
        
    } catch (error) {
        logger.error("Application failed to start:", error);
        process.exit(1);
    }
}

main().catch(console.error);'''
    
    def _get_go_startup_template(self) -> str:
        return '''package main

import (
    "log"
    "os"
)

func main() {
    log.Println("Starting application...")
    
    // Add your application initialization here
    log.Println("Application started successfully")
}'''
    
    def _get_rust_startup_template(self) -> str:
        return '''use std::process;

fn main() {
    println!("Starting application...");
    
    // Add your application initialization here
    println!("Application started successfully");
}''' 