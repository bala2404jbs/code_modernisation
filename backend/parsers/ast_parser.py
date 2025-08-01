import os
import ast
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import gc

class ASTParser:
    """AST Parser for multiple programming languages"""
    
    # Performance configuration
    MAX_FILE_SIZE_MB = 10  # Maximum file size to parse (MB)
    MAX_FILES_TO_PARSE = 5000  # Maximum number of files to parse
    BATCH_SIZE = 100  # Number of files to process in each batch
    
    def __init__(self):
        self.parsers = {}
        self.supported_languages = {
            'python': ['.py', '.pyw', '.pyi', '.pyx', '.pxd', '.pxi'],
            'java': ['.java', '.jav'],
            'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
            'typescript': ['.ts', '.tsx', '.mts', '.cts'],
            'cobol': ['.cbl', '.cob', '.cpy', '.cobol'],
            'cpp': ['.cpp', '.cc', '.cxx', '.c++', '.h', '.hpp', '.hxx', '.hh', '.h++'],
            'c': ['.c', '.h'],
            'go': ['.go'],
            'rust': ['.rs'],
            'php': ['.php', '.php3', '.php4', '.php5', '.phtml'],
            'ruby': ['.rb', '.rbw'],
            'scala': ['.scala'],
            'kotlin': ['.kt', '.kts'],
            'swift': ['.swift'],
            'dart': ['.dart'],
            'r': ['.r', '.R'],
            'matlab': ['.m', '.mat'],
            'fortran': ['.f', '.f90', '.f95', '.f03', '.f08'],
            'pascal': ['.pas', '.pp', '.p'],
            'ada': ['.adb', '.ads'],
            'lisp': ['.lisp', '.lsp', '.cl'],
            'scheme': ['.scm', '.ss'],
            'haskell': ['.hs', '.lhs'],
            'ocaml': ['.ml', '.mli'],
            'fsharp': ['.fs', '.fsi'],
            'erlang': ['.erl'],
            'elixir': ['.ex', '.exs'],
            'clojure': ['.clj', '.cljs', '.cljc'],
            'groovy': ['.groovy', '.gvy'],
            'perl': ['.pl', '.pm', '.t'],
            'bash': ['.sh', '.bash'],
            'powershell': ['.ps1', '.psm1', '.psd1'],
            'sql': ['.sql'],
            'html': ['.html', '.htm', '.xhtml'],
            'css': ['.css', '.scss', '.sass', '.less'],
            'xml': ['.xml', '.xsd', '.xsl'],
            'json': ['.json'],
            'yaml': ['.yml', '.yaml'],
            'toml': ['.toml'],
            'ini': ['.ini', '.cfg', '.conf'],
            'markdown': ['.md', '.markdown'],
            'dockerfile': ['Dockerfile', '.dockerfile'],
            'makefile': ['Makefile', '.mk', '.make'],
            'cmake': ['CMakeLists.txt', '.cmake'],
            'gradle': ['build.gradle', '.gradle'],
            'maven': ['pom.xml'],
            'npm': ['package.json', 'package-lock.json'],
            'pip': ['requirements.txt', 'setup.py', 'pyproject.toml'],
            'cargo': ['Cargo.toml', 'Cargo.lock'],
            'go_mod': ['go.mod', 'go.sum'],
            'composer': ['composer.json', 'composer.lock'],
            'gemfile': ['Gemfile', 'Gemfile.lock'],
            'pubspec': ['pubspec.yaml', 'pubspec.lock'],
            'cabal': ['.cabal'],
            'stack': ['stack.yaml'],
            'mix': ['mix.exs', 'mix.lock'],
            'rebar': ['rebar.config'],
            'leiningen': ['project.clj'],
            'sbt': ['build.sbt', 'project/build.properties'],
            'gradle_wrapper': ['gradlew', 'gradlew.bat'],
            'maven_wrapper': ['mvnw', 'mvnw.cmd'],
            'npm_scripts': ['package.json'],
            'pip_scripts': ['setup.py', 'pyproject.toml'],
            'cargo_scripts': ['Cargo.toml'],
            'go_scripts': ['go.mod'],
            'composer_scripts': ['composer.json'],
            'gem_scripts': ['Gemfile'],
            'pub_scripts': ['pubspec.yaml'],
            'cabal_scripts': ['.cabal'],
            'stack_scripts': ['stack.yaml'],
            'mix_scripts': ['mix.exs'],
            'rebar_scripts': ['rebar.config'],
            'lein_scripts': ['project.clj'],
            'sbt_scripts': ['build.sbt']
        }
        
    async def initialize(self):
        """Initialize language parsers"""
        try:
            # Initialize tree-sitter parsers for different languages
            await self._setup_tree_sitter()
            print("AST Parser initialized successfully")
        except Exception as e:
            print(f"Failed to initialize AST Parser: {str(e)}")
            raise
    
    async def _setup_tree_sitter(self):
        """Setup parsers for supported languages"""
        try:
            # Python uses built-in ast module
            self.parsers['python'] = 'builtin'
            
            # For other languages, we'll implement basic parsing
            for lang in ['java', 'javascript', 'typescript', 'cobol', 'cpp', 'c', 'go', 'rust', 'php', 'ruby', 'scala', 'kotlin', 'swift', 'dart', 'r', 'matlab', 'fortran', 'pascal', 'ada', 'lisp', 'scheme', 'haskell', 'ocaml', 'fsharp', 'erlang', 'elixir', 'clojure', 'groovy', 'perl', 'bash', 'powershell', 'sql', 'html', 'css', 'xml', 'json', 'yaml', 'toml', 'ini', 'markdown', 'dockerfile', 'makefile', 'cmake', 'gradle', 'maven', 'npm', 'pip', 'cargo', 'go_mod', 'composer', 'gemfile', 'pubspec', 'cabal', 'stack', 'mix', 'rebar', 'leiningen', 'sbt', 'gradle_wrapper', 'maven_wrapper', 'npm_scripts', 'pip_scripts', 'cargo_scripts', 'go_scripts', 'composer_scripts', 'gem_scripts', 'pub_scripts', 'cabal_scripts', 'stack_scripts', 'mix_scripts', 'rebar_scripts', 'lein_scripts', 'sbt_scripts']:
                self.parsers[lang] = 'basic'
                
        except Exception as e:
            print(f"Failed to setup parsers: {str(e)}")
            raise
    
    async def parse_project(self, project_dir: str, source_language: str) -> List[Dict[str, Any]]:
        """Parse all files in a project directory"""
        try:
            ast_data = []
            project_path = Path(project_dir)
            
            print(f"Parsing project: {project_dir} with language: {source_language}")
            
            # Get file extensions for the language
            extensions = self.supported_languages.get(source_language.lower(), [])
            print(f"Looking for extensions: {extensions}")
            
            # Find all relevant files including dependency files
            all_files = []
            
            # Add specific dependency files for the language
            dependency_files = self._get_dependency_files(source_language)
            extensions.extend(dependency_files)
            
            # Define files to skip for performance
            skip_patterns = [
                'node_modules', '.git', '.svn', '.hg', '.bzr',
                '__pycache__', '.pytest_cache', '.mypy_cache',
                'target', 'build', 'dist', 'out', 'bin',
                '.DS_Store', 'Thumbs.db', '.idea', '.vscode',
                '*.log', '*.tmp', '*.temp', '*.bak', '*.backup',
                '*.min.js', '*.min.css', '*.map',
                '*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.ico',
                '*.mp3', '*.mp4', '*.avi', '*.mov', '*.wmv',
                '*.zip', '*.tar', '*.gz', '*.rar', '*.7z',
                '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx',
                '*.ppt', '*.pptx', '*.odt', '*.ods', '*.odp'
            ]
            
            # Find all files with matching extensions
            for ext in extensions:
                print(f"Searching for files with extension/name: {ext}")
                if ext.startswith('.'):
                    # File extension
                    for file_path in project_path.rglob(f"*{ext}"):
                        if file_path.is_file() and not self._should_skip_file(file_path, skip_patterns):
                            all_files.append(file_path)
                else:
                    # Specific filename
                    for file_path in project_path.rglob(ext):
                        if file_path.is_file() and not self._should_skip_file(file_path, skip_patterns):
                            all_files.append(file_path)
            
            # Remove duplicates and sort
            all_files = sorted(list(set(all_files)))
            
            # Limit the number of files to parse for performance
            if len(all_files) > self.MAX_FILES_TO_PARSE:
                print(f"Warning: Found {len(all_files)} files, limiting to {self.MAX_FILES_TO_PARSE} for performance")
                all_files = all_files[:self.MAX_FILES_TO_PARSE]
            
            print(f"Found {len(all_files)} files to parse")
            
            # Parse each file with progress tracking
            batch_size = self.BATCH_SIZE  # Process files in batches
            for i in range(0, len(all_files), batch_size):
                batch = all_files[i:i + batch_size]
                print(f"Processing batch {i//batch_size + 1}/{(len(all_files) + batch_size - 1)//batch_size}")
                
                for j, file_path in enumerate(batch, 1):
                    if j % 50 == 0:
                        print(f"Progress: {i + j}/{len(all_files)} files parsed")
                    
                    print(f"Parsing file: {file_path}")
                    file_ast = await self.parse_file(str(file_path), source_language)
                    if file_ast:
                        print(f"Successfully parsed: {file_path}")
                        ast_data.append(file_ast)
                    else:
                        print(f"Failed to parse: {file_path}")
                
                # Clear some memory after each batch
                gc.collect()
            
            print(f"Total files parsed: {len(ast_data)}")
            return ast_data
            
        except Exception as e:
            print(f"Failed to parse project {project_dir}: {str(e)}")
            raise
    
    def _should_skip_file(self, file_path: Path, skip_patterns: List[str]) -> bool:
        """Check if file should be skipped based on patterns"""
        file_str = str(file_path)
        
        for pattern in skip_patterns:
            if pattern.startswith('*.'):
                # File extension pattern
                ext = pattern[1:]  # Remove the *
                if file_str.endswith(ext):
                    return True
            elif pattern.startswith('*'):
                # Wildcard pattern
                if pattern[1:] in file_str:
                    return True
            else:
                # Direct path/name pattern
                if pattern in file_str:
                    return True
        
        return False
    
    def _get_dependency_files(self, language: str) -> List[str]:
        """Get dependency file names for a specific language"""
        dependency_files = {
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 'poetry.lock', 'Pipfile.lock'],
            'java': ['pom.xml', 'build.gradle', 'gradle.properties', 'gradle-wrapper.properties', 'settings.gradle'],
            'javascript': ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', '.npmrc', '.yarnrc'],
            'typescript': ['package.json', 'package-lock.json', 'tsconfig.json', 'tslint.json', '.eslintrc'],
            'go': ['go.mod', 'go.sum', 'go.work', 'go.work.sum'],
            'rust': ['Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml'],
            'php': ['composer.json', 'composer.lock', 'phpunit.xml', '.phpunit.result.cache'],
            'ruby': ['Gemfile', 'Gemfile.lock', 'Rakefile', '.ruby-version', '.ruby-gemset'],
            'scala': ['build.sbt', 'project/build.properties', 'project/plugins.sbt'],
            'kotlin': ['build.gradle.kts', 'gradle.properties', 'settings.gradle.kts'],
            'swift': ['Package.swift', 'Cartfile', 'Cartfile.resolved'],
            'dart': ['pubspec.yaml', 'pubspec.lock', 'analysis_options.yaml'],
            'r': ['DESCRIPTION', 'NAMESPACE', '.Rprofile', '.Rhistory'],
            'matlab': ['.matlabrc', 'startup.m'],
            'fortran': ['Makefile', 'CMakeLists.txt'],
            'pascal': ['Makefile', 'CMakeLists.txt'],
            'ada': ['Makefile', 'CMakeLists.txt'],
            'lisp': ['asd', 'asdf', 'quicklisp.lisp'],
            'scheme': ['Makefile', 'CMakeLists.txt'],
            'haskell': ['cabal.project', 'stack.yaml', 'package.yaml'],
            'ocaml': ['dune', 'dune-project', 'opam'],
            'fsharp': ['*.fsproj', 'paket.dependencies', 'paket.lock'],
            'erlang': ['rebar.config', 'rebar.lock', 'relx.config'],
            'elixir': ['mix.exs', 'mix.lock', 'rel/config.exs'],
            'clojure': ['project.clj', 'deps.edn', 'shadow-cljs.edn'],
            'groovy': ['build.gradle', 'gradle.properties'],
            'perl': ['Makefile.PL', 'Build.PL', 'cpanfile'],
            'bash': ['Makefile', 'CMakeLists.txt'],
            'powershell': ['*.psd1', '*.psm1'],
            'sql': ['*.sql', 'migration.sql'],
            'html': ['*.html', '*.htm', '*.xhtml'],
            'css': ['*.css', '*.scss', '*.sass', '*.less'],
            'xml': ['*.xml', '*.xsd', '*.xsl'],
            'json': ['*.json'],
            'yaml': ['*.yml', '*.yaml'],
            'toml': ['*.toml'],
            'ini': ['*.ini', '*.cfg', '*.conf'],
            'markdown': ['*.md', '*.markdown'],
            'dockerfile': ['Dockerfile', '.dockerfile', 'docker-compose.yml', 'docker-compose.yaml'],
            'makefile': ['Makefile', '*.mk', '*.make'],
            'cmake': ['CMakeLists.txt', '*.cmake'],
            'gradle': ['build.gradle', 'gradle.properties', 'settings.gradle'],
            'maven': ['pom.xml', 'settings.xml'],
            'npm': ['package.json', 'package-lock.json', '.npmrc'],
            'pip': ['requirements.txt', 'setup.py', 'pyproject.toml'],
            'cargo': ['Cargo.toml', 'Cargo.lock'],
            'go_mod': ['go.mod', 'go.sum'],
            'composer': ['composer.json', 'composer.lock'],
            'gemfile': ['Gemfile', 'Gemfile.lock'],
            'pubspec': ['pubspec.yaml', 'pubspec.lock'],
            'cabal': ['*.cabal'],
            'stack': ['stack.yaml'],
            'mix': ['mix.exs', 'mix.lock'],
            'rebar': ['rebar.config'],
            'leiningen': ['project.clj'],
            'sbt': ['build.sbt', 'project/build.properties'],
            'gradle_wrapper': ['gradlew', 'gradlew.bat'],
            'maven_wrapper': ['mvnw', 'mvnw.cmd'],
            'npm_scripts': ['package.json'],
            'pip_scripts': ['setup.py', 'pyproject.toml'],
            'cargo_scripts': ['Cargo.toml'],
            'go_scripts': ['go.mod'],
            'composer_scripts': ['composer.json'],
            'gem_scripts': ['Gemfile'],
            'pub_scripts': ['pubspec.yaml'],
            'cabal_scripts': ['*.cabal'],
            'stack_scripts': ['stack.yaml'],
            'mix_scripts': ['mix.exs'],
            'rebar_scripts': ['rebar.config'],
            'lein_scripts': ['project.clj'],
            'sbt_scripts': ['build.sbt']
        }
        return dependency_files.get(language.lower(), [])
    
    async def parse_file(self, file_path: str, language: str) -> Optional[Dict[str, Any]]:
        """Parse a single file and return AST data with line numbers"""
        try:
            # Check file size - skip files larger than configured limit
            file_size = os.path.getsize(file_path)
            max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
            if file_size > max_size_bytes:
                print(f"Skipping large file: {file_path} ({file_size} bytes, limit: {self.MAX_FILE_SIZE_MB}MB)")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine the actual language based on file extension
            actual_language = self._detect_language_from_file(file_path, language)
            
            if actual_language == 'python':
                return await self._parse_python_file(file_path, content)
            elif actual_language == 'java':
                return await self._parse_java_file(file_path, content)
            elif actual_language == 'javascript':
                return await self._parse_javascript_file(file_path, content)
            elif actual_language == 'typescript':
                return await self._parse_typescript_file(file_path, content)
            elif actual_language == 'cobol':
                return await self._parse_cobol_file(file_path, content)
            elif actual_language in ['cpp', 'c']:
                return await self._parse_cpp_file(file_path, content)
            elif actual_language == 'go':
                return await self._parse_go_file(file_path, content)
            elif actual_language == 'rust':
                return await self._parse_rust_file(file_path, content)
            elif actual_language == 'php':
                return await self._parse_php_file(file_path, content)
            elif actual_language == 'ruby':
                return await self._parse_ruby_file(file_path, content)
            elif actual_language == 'sql':
                return await self._parse_sql_file(file_path, content)
            elif actual_language == 'html':
                return await self._parse_html_file(file_path, content)
            elif actual_language == 'css':
                return await self._parse_css_file(file_path, content)
            elif actual_language == 'xml':
                return await self._parse_xml_file(file_path, content)
            elif actual_language == 'json':
                return await self._parse_json_file(file_path, content)
            elif actual_language == 'yaml':
                return await self._parse_yaml_file(file_path, content)
            elif actual_language == 'toml':
                return await self._parse_toml_file(file_path, content)
            elif actual_language == 'ini':
                return await self._parse_ini_file(file_path, content)
            elif actual_language == 'markdown':
                return await self._parse_markdown_file(file_path, content)
            elif actual_language == 'dockerfile':
                return await self._parse_dockerfile(file_path, content)
            elif actual_language == 'makefile':
                return await self._parse_makefile(file_path, content)
            elif actual_language == 'cmake':
                return await self._parse_cmake_file(file_path, content)
            else:
                # Generic parser for other file types
                return await self._parse_generic_file(file_path, content, actual_language)
                
        except Exception as e:
            print(f"Failed to parse file {file_path}: {str(e)}")
            return None
    
    def _detect_language_from_file(self, file_path: str, default_language: str) -> str:
        """Detect language based on file extension and content"""
        file_path_lower = file_path.lower()
        
        # Check file extensions
        if file_path_lower.endswith(('.py', '.pyw', '.pyi', '.pyx', '.pxd', '.pxi')):
            return 'python'
        elif file_path_lower.endswith(('.java', '.jav')):
            return 'java'
        elif file_path_lower.endswith(('.js', '.jsx', '.mjs', '.cjs')):
            return 'javascript'
        elif file_path_lower.endswith(('.ts', '.tsx', '.mts', '.cts')):
            return 'typescript'
        elif file_path_lower.endswith(('.cbl', '.cob', '.cpy', '.cobol')):
            return 'cobol'
        elif file_path_lower.endswith(('.cpp', '.cc', '.cxx', '.c++', '.h', '.hpp', '.hxx', '.hh', '.h++')):
            return 'cpp'
        elif file_path_lower.endswith(('.c', '.h')):
            return 'c'
        elif file_path_lower.endswith('.go'):
            return 'go'
        elif file_path_lower.endswith('.rs'):
            return 'rust'
        elif file_path_lower.endswith(('.php', '.php3', '.php4', '.php5', '.phtml')):
            return 'php'
        elif file_path_lower.endswith(('.rb', '.rbw')):
            return 'ruby'
        elif file_path_lower.endswith('.sql'):
            return 'sql'
        elif file_path_lower.endswith(('.html', '.htm', '.xhtml')):
            return 'html'
        elif file_path_lower.endswith(('.css', '.scss', '.sass', '.less')):
            return 'css'
        elif file_path_lower.endswith(('.xml', '.xsd', '.xsl')):
            return 'xml'
        elif file_path_lower.endswith('.json'):
            return 'json'
        elif file_path_lower.endswith(('.yml', '.yaml')):
            return 'yaml'
        elif file_path_lower.endswith('.toml'):
            return 'toml'
        elif file_path_lower.endswith(('.ini', '.cfg', '.conf')):
            return 'ini'
        elif file_path_lower.endswith(('.md', '.markdown')):
            return 'markdown'
        elif file_path_lower in ['dockerfile', '.dockerfile']:
            return 'dockerfile'
        elif file_path_lower in ['makefile', '.mk', '.make']:
            return 'makefile'
        elif file_path_lower in ['cmakelists.txt', '.cmake']:
            return 'cmake'
        elif file_path_lower in ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml']:
            return 'npm'
        elif file_path_lower in ['requirements.txt', 'setup.py', 'pyproject.toml', 'pipfile', 'poetry.lock']:
            return 'pip'
        elif file_path_lower in ['cargo.toml', 'cargo.lock']:
            return 'cargo'
        elif file_path_lower in ['go.mod', 'go.sum']:
            return 'go_mod'
        elif file_path_lower in ['composer.json', 'composer.lock']:
            return 'composer'
        elif file_path_lower in ['gemfile', 'gemfile.lock']:
            return 'gemfile'
        elif file_path_lower in ['pubspec.yaml', 'pubspec.lock']:
            return 'pubspec'
        elif file_path_lower.endswith('.cabal'):
            return 'cabal'
        elif file_path_lower in ['stack.yaml']:
            return 'stack'
        elif file_path_lower in ['mix.exs', 'mix.lock']:
            return 'mix'
        elif file_path_lower in ['rebar.config']:
            return 'rebar'
        elif file_path_lower in ['project.clj']:
            return 'leiningen'
        elif file_path_lower in ['build.sbt', 'project/build.properties']:
            return 'sbt'
        elif file_path_lower in ['gradlew', 'gradlew.bat']:
            return 'gradle_wrapper'
        elif file_path_lower in ['mvnw', 'mvnw.cmd']:
            return 'maven_wrapper'
        elif file_path_lower in ['pom.xml', 'build.gradle', 'gradle.properties', 'settings.gradle']:
            return 'gradle'
        elif file_path_lower in ['maven']:
            return 'maven'
        else:
            return default_language
    
    async def _parse_python_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse Python file using built-in ast module"""
        try:
            tree = ast.parse(content)
            
            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            imports.append(f"{module}.{alias.name}")
            
            # Extract functions with full body
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_body = self._extract_node_source(content, node)
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [d.id for d in node.decorator_list if hasattr(d, 'id')],
                        "body": function_body,
                        "full_code": self._get_full_function_code(content, node)
                    })
            
            # Extract classes with full implementation
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_body = self._extract_node_source(content, node)
                    class_methods = []
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            class_methods.append({
                                "name": child.name,
                                "line": child.lineno,
                                "body": self._extract_node_source(content, child)
                            })
                    
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "bases": [base.id for base in node.bases if hasattr(base, 'id')],
                        "methods": class_methods,
                        "body": class_body,
                        "full_code": self._get_full_class_code(content, node)
                    })
            
            # Extract variables with values
            variables = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            variables.append({
                                "name": target.id,
                                "line": node.lineno,
                                "value": ast.unparse(node.value) if hasattr(ast, 'unparse') else str(node.value),
                                "full_assignment": self._extract_node_source(content, node)
                            })
            
            return {
                "file_path": file_path,
                "language": "python",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": self._ast_to_dict(tree),
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse Python file {file_path}: {str(e)}")
            return None
    
    async def _parse_java_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse Java file and create AST structure with full code"""
        try:
            # Create AST structure
            ast_tree = {
                "node_type": "CompilationUnit",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            current_class = None
            current_method = None
            brace_count = 0
            class_start_line = 0
            method_start_line = 0
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                original_line = line
                
                # Skip empty lines and comments
                if not line or line.startswith('//') or line.startswith('/*'):
                    continue
                
                # Track brace count for scope
                brace_count += line.count('{') - line.count('}')
                
                # Extract imports
                if line.startswith('import '):
                    import_stmt = line[7:].rstrip(';')
                    imports.append(import_stmt)
                    ast_tree["children"].append({
                        "node_type": "ImportDeclaration",
                        "line": i,
                        "import": import_stmt
                    })
                
                # Extract package declaration
                elif line.startswith('package '):
                    package_name = line[8:].rstrip(';')
                    ast_tree["children"].append({
                        "node_type": "PackageDeclaration",
                        "line": i,
                        "package": package_name
                    })
                
                # Extract class definitions with full body
                elif re.match(r'(public\s+)?(abstract\s+)?(final\s+)?class\s+\w+', line):
                    class_match = re.search(r'class\s+(\w+)', line)
                    if class_match:
                        class_name = class_match.group(1)
                        class_start_line = i
                        class_code = self._extract_code_block(lines, i, content)
                        
                        class_node = {
                            "node_type": "ClassDeclaration",
                            "name": class_name,
                            "line": i,
                            "modifiers": self._extract_modifiers(line),
                            "children": [],
                            "full_code": class_code
                        }
                        classes.append({
                            "name": class_name,
                            "line": i,
                            "type": "public" if "public" in line else "default",
                            "modifiers": self._extract_modifiers(line),
                            "full_code": class_code
                        })
                        current_class = class_node
                        ast_tree["children"].append(class_node)
                
                # Extract method definitions with full body
                elif re.match(r'(public|private|protected|static|final|abstract)\s+.*\(.*\)', line):
                    if 'class' not in line and 'interface' not in line:
                        method_match = re.search(r'(\w+)\s*\([^)]*\)', line)
                        if method_match:
                            method_name = method_match.group(1)
                            method_start_line = i
                            method_code = self._extract_code_block(lines, i, content)
                            
                            method_node = {
                                "node_type": "MethodDeclaration",
                                "name": method_name,
                                "line": i,
                                "modifiers": self._extract_modifiers(line),
                                "children": [],
                                "full_code": method_code
                            }
                            functions.append({
                                "name": method_name,
                                "line": i,
                                "visibility": "public" if "public" in line else "private" if "private" in line else "protected",
                                "modifiers": self._extract_modifiers(line),
                                "full_code": method_code
                            })
                            current_method = method_node
                            if current_class:
                                current_class["children"].append(method_node)
                
                # Extract variable declarations with full assignment
                elif re.match(r'(public|private|protected|static|final)\s+.*\w+\s+\w+', line):
                    var_match = re.search(r'(\w+)\s+(\w+)', line)
                    if var_match:
                        var_type = var_match.group(1)
                        var_name = var_match.group(2)
                        # Get the full variable declaration including initialization
                        var_code = self._extract_variable_declaration(lines, i, content)
                        variables.append({
                            "name": var_name,
                            "type": var_type,
                            "line": i,
                            "modifiers": self._extract_modifiers(line),
                            "full_code": var_code
                        })
            
            return {
                "file_path": file_path,
                "language": "java",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse Java file {file_path}: {str(e)}")
            return None
    
    async def _parse_javascript_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse JavaScript file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "Program",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract imports
                if line.startswith('import ') or ('require(' in line and line.startswith('const ')):
                    imports.append(line)
                    ast_tree["children"].append({
                        "node_type": "ImportDeclaration",
                        "line": i,
                        "import": line
                    })
                
                # Extract function declarations with full body
                elif re.match(r'function\s+\w+\s*\(', line):
                    func_match = re.search(r'function\s+(\w+)', line)
                    if func_match:
                        func_name = func_match.group(1)
                        func_code = self._extract_code_block(lines, i, content)
                        functions.append({
                            "name": func_name,
                            "line": i,
                            "type": "function",
                            "full_code": func_code
                        })
                        ast_tree["children"].append({
                            "node_type": "FunctionDeclaration",
                            "name": func_name,
                            "line": i,
                            "full_code": func_code
                        })
                
                # Extract arrow functions and const functions with full body
                elif re.match(r'const\s+\w+\s*=\s*.*=>', line) or re.match(r'const\s+\w+\s*=\s*function', line):
                    func_match = re.search(r'const\s+(\w+)', line)
                    if func_match:
                        func_name = func_match.group(1)
                        func_code = self._extract_code_block(lines, i, content)
                        functions.append({
                            "name": func_name,
                            "line": i,
                            "type": "arrow" if '=>' in line else "function",
                            "full_code": func_code
                        })
                        ast_tree["children"].append({
                            "node_type": "VariableDeclaration",
                            "name": func_name,
                            "line": i,
                            "kind": "const",
                            "full_code": func_code
                        })
                
                # Extract class declarations with full body
                elif line.startswith('class '):
                    class_match = re.search(r'class\s+(\w+)', line)
                    if class_match:
                        class_name = class_match.group(1)
                        class_code = self._extract_code_block(lines, i, content)
                        classes.append({
                            "name": class_name,
                            "line": i,
                            "full_code": class_code
                        })
                        ast_tree["children"].append({
                            "node_type": "ClassDeclaration",
                            "name": class_name,
                            "line": i,
                            "full_code": class_code
                        })
                
                # Extract variable declarations with full assignment
                elif re.match(r'(let|const|var)\s+\w+', line):
                    var_match = re.search(r'(let|const|var)\s+(\w+)', line)
                    if var_match:
                        var_kind = var_match.group(1)
                        var_name = var_match.group(2)
                        var_code = self._extract_variable_declaration(lines, i, content)
                        variables.append({
                            "name": var_name,
                            "kind": var_kind,
                            "line": i,
                            "full_code": var_code
                        })
                        ast_tree["children"].append({
                            "node_type": "VariableDeclaration",
                            "name": var_name,
                            "line": i,
                            "kind": var_kind,
                            "full_code": var_code
                        })
            
            return {
                "file_path": file_path,
                "language": "javascript",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse JavaScript file {file_path}: {str(e)}")
            return None
    
    async def _parse_typescript_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse TypeScript file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "Program",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract imports
                if line.startswith('import '):
                    imports.append(line)
                    ast_tree["children"].append({
                        "node_type": "ImportDeclaration",
                        "line": i,
                        "import": line
                    })
                
                # Extract interfaces with full body
                elif line.startswith('interface '):
                    interface_match = re.search(r'interface\s+(\w+)', line)
                    if interface_match:
                        interface_name = interface_match.group(1)
                        interface_code = self._extract_code_block(lines, i, content)
                        ast_tree["children"].append({
                            "node_type": "InterfaceDeclaration",
                            "name": interface_name,
                            "line": i,
                            "full_code": interface_code
                        })
                
                # Extract type definitions with full body
                elif line.startswith('type '):
                    type_match = re.search(r'type\s+(\w+)', line)
                    if type_match:
                        type_name = type_match.group(1)
                        type_code = self._extract_code_block(lines, i, content)
                        ast_tree["children"].append({
                            "node_type": "TypeAliasDeclaration",
                            "name": type_name,
                            "line": i,
                            "full_code": type_code
                        })
                
                # Extract function declarations with types and full body
                elif re.match(r'function\s+\w+\s*\(.*\)\s*:\s*\w+', line):
                    func_match = re.search(r'function\s+(\w+)', line)
                    if func_match:
                        func_name = func_match.group(1)
                        func_code = self._extract_code_block(lines, i, content)
                        functions.append({
                            "name": func_name,
                            "line": i,
                            "type": "function",
                            "full_code": func_code
                        })
                        ast_tree["children"].append({
                            "node_type": "FunctionDeclaration",
                            "name": func_name,
                            "line": i,
                            "full_code": func_code
                        })
                
                # Extract class declarations with full body
                elif line.startswith('class '):
                    class_match = re.search(r'class\s+(\w+)', line)
                    if class_match:
                        class_name = class_match.group(1)
                        class_code = self._extract_code_block(lines, i, content)
                        classes.append({
                            "name": class_name,
                            "line": i,
                            "full_code": class_code
                        })
                        ast_tree["children"].append({
                            "node_type": "ClassDeclaration",
                            "name": class_name,
                            "line": i,
                            "full_code": class_code
                        })
                
                # Extract variable declarations with types and full assignment
                elif re.match(r'(let|const|var)\s+\w+\s*:\s*\w+', line):
                    var_match = re.search(r'(let|const|var)\s+(\w+)', line)
                    if var_match:
                        var_kind = var_match.group(1)
                        var_name = var_match.group(2)
                        var_code = self._extract_variable_declaration(lines, i, content)
                        variables.append({
                            "name": var_name,
                            "kind": var_kind,
                            "line": i,
                            "full_code": var_code
                        })
                        ast_tree["children"].append({
                            "node_type": "VariableDeclaration",
                            "name": var_name,
                            "line": i,
                            "kind": var_kind,
                            "full_code": var_code
                        })
            
            return {
                "file_path": file_path,
                "language": "typescript",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse TypeScript file {file_path}: {str(e)}")
            return None
    
    async def _parse_cobol_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse COBOL file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "CobolProgram",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            current_division = None
            current_section = None
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract divisions with full body
                if 'DIVISION' in line.upper():
                    division_name = line.split()[0]
                    division_code = self._extract_cobol_block(lines, i, content)
                    current_division = {
                        "node_type": "Division",
                        "name": division_name,
                        "line": i,
                        "children": [],
                        "full_code": division_code
                    }
                    functions.append({
                        "name": division_name,
                        "line": i,
                        "type": "division",
                        "full_code": division_code
                    })
                    ast_tree["children"].append(current_division)
                
                # Extract sections with full body
                elif 'SECTION' in line.upper():
                    section_name = line.split()[0]
                    section_code = self._extract_cobol_block(lines, i, content)
                    current_section = {
                        "node_type": "Section",
                        "name": section_name,
                        "line": i,
                        "children": [],
                        "full_code": section_code
                    }
                    functions.append({
                        "name": section_name,
                        "line": i,
                        "type": "section",
                        "full_code": section_code
                    })
                    if current_division:
                        current_division["children"].append(current_section)
                
                # Extract data definitions with full declaration
                elif re.match(r'^\d{2}\s+\w+', line):
                    parts = line.split()
                    if len(parts) >= 2:
                        level = parts[0]
                        var_name = parts[1]
                        var_code = self._extract_cobol_data_item(lines, i, content)
                        variables.append({
                            "name": var_name,
                            "line": i,
                            "level": level,
                            "full_code": var_code
                        })
                        data_node = {
                            "node_type": "DataItem",
                            "name": var_name,
                            "level": level,
                            "line": i,
                            "full_code": var_code
                        }
                        if current_section:
                            current_section["children"].append(data_node)
                        elif current_division:
                            current_division["children"].append(data_node)
            
            return {
                "file_path": file_path,
                "language": "cobol",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse COBOL file {file_path}: {str(e)}")
            return None
    
    async def _parse_cpp_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse C++ file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "TranslationUnit",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract includes
                if line.startswith('#include '):
                    include_path = line[9:].strip('"<>')
                    imports.append(line)
                    ast_tree["children"].append({
                        "node_type": "IncludeDirective",
                        "line": i,
                        "path": include_path
                    })
                
                # Extract class declarations with full body
                elif re.match(r'class\s+\w+', line) or re.match(r'struct\s+\w+', line):
                    class_match = re.search(r'(class|struct)\s+(\w+)', line)
                    if class_match:
                        class_type = class_match.group(1)
                        class_name = class_match.group(2)
                        class_code = self._extract_code_block(lines, i, content)
                        classes.append({
                            "name": class_name,
                            "line": i,
                            "type": class_type,
                            "full_code": class_code
                        })
                        ast_tree["children"].append({
                            "node_type": "ClassDeclaration",
                            "name": class_name,
                            "type": class_type,
                            "line": i,
                            "full_code": class_code
                        })
                
                # Extract function declarations with full body
                elif re.match(r'\w+\s+\w+\s*\([^)]*\)', line) and not line.startswith('#'):
                    func_match = re.search(r'(\w+)\s+(\w+)\s*\(', line)
                    if func_match:
                        return_type = func_match.group(1)
                        func_name = func_match.group(2)
                        func_code = self._extract_code_block(lines, i, content)
                        functions.append({
                            "name": func_name,
                            "line": i,
                            "return_type": return_type,
                            "full_code": func_code
                        })
                        ast_tree["children"].append({
                            "node_type": "FunctionDeclaration",
                            "name": func_name,
                            "return_type": return_type,
                            "line": i,
                            "full_code": func_code
                        })
                
                # Extract variable declarations with full assignment
                elif re.match(r'\w+\s+\w+\s*[=;]', line) and not line.startswith('#'):
                    var_match = re.search(r'(\w+)\s+(\w+)', line)
                    if var_match:
                        var_type = var_match.group(1)
                        var_name = var_match.group(2)
                        var_code = self._extract_variable_declaration(lines, i, content)
                        variables.append({
                            "name": var_name,
                            "type": var_type,
                            "line": i,
                            "full_code": var_code
                        })
                        ast_tree["children"].append({
                            "node_type": "VariableDeclaration",
                            "name": var_name,
                            "type": var_type,
                            "line": i,
                            "full_code": var_code
                        })
            
            return {
                "file_path": file_path,
                "language": "cpp",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse C++ file {file_path}: {str(e)}")
            return None
    
    def _extract_modifiers(self, line: str) -> List[str]:
        """Extract modifiers from a Java line"""
        modifiers = []
        if 'public' in line:
            modifiers.append('public')
        if 'private' in line:
            modifiers.append('private')
        if 'protected' in line:
            modifiers.append('protected')
        if 'static' in line:
            modifiers.append('static')
        if 'final' in line:
            modifiers.append('final')
        if 'abstract' in line:
            modifiers.append('abstract')
        return modifiers
    
    def _extract_node_source(self, content: str, node) -> str:
        """Extract source code for a specific AST node"""
        try:
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                lines = content.split('\n')
                start_line = node.lineno - 1
                end_line = node.end_lineno
                return '\n'.join(lines[start_line:end_line])
            else:
                return str(node)
        except:
            return str(node)
    
    def _get_full_function_code(self, content: str, node) -> str:
        """Get full function code including decorators"""
        try:
            lines = content.split('\n')
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            # Include decorators
            if hasattr(node, 'decorator_list') and node.decorator_list:
                decorator_start = node.decorator_list[0].lineno - 1
                start_line = min(start_line, decorator_start)
            
            return '\n'.join(lines[start_line:end_line])
        except:
            return str(node)
    
    def _get_full_class_code(self, content: str, node) -> str:
        """Get full class code including decorators"""
        try:
            lines = content.split('\n')
            start_line = node.lineno - 1
            end_line = node.end_lineno
            
            # Include decorators
            if hasattr(node, 'decorator_list') and node.decorator_list:
                decorator_start = node.decorator_list[0].lineno - 1
                start_line = min(start_line, decorator_start)
            
            return '\n'.join(lines[start_line:end_line])
        except:
            return str(node)
    
    def _extract_code_block(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract a complete code block from a starting line"""
        try:
            start_idx = start_line - 1
            brace_count = 0
            end_idx = start_idx
            
            # Find the opening brace
            for i in range(start_idx, len(lines)):
                line = lines[i]
                brace_count += line.count('{') - line.count('}')
                if brace_count > 0:
                    end_idx = i + 1
                    break
            
            # Find the closing brace
            for i in range(end_idx, len(lines)):
                line = lines[i]
                brace_count += line.count('{') - line.count('}')
                if brace_count <= 0:
                    end_idx = i + 1
                    break
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_variable_declaration(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract complete variable declaration including initialization"""
        try:
            start_idx = start_line - 1
            line = lines[start_idx]
            
            # If line ends with semicolon, it's complete
            if line.strip().endswith(';'):
                return line
            
            # Look for semicolon in subsequent lines
            for i in range(start_idx + 1, min(start_idx + 5, len(lines))):
                line += '\n' + lines[i]
                if lines[i].strip().endswith(';'):
                    break
            
            return line
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_cobol_block(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract COBOL division or section block"""
        try:
            start_idx = start_line - 1
            end_idx = start_idx
            
            # Find the end of the division/section
            for i in range(start_idx + 1, len(lines)):
                line = lines[i].strip()
                if line and (line.startswith('DIVISION') or line.startswith('SECTION') or 
                           line.startswith('PROCEDURE') or line.startswith('DATA')):
                    break
                end_idx = i + 1
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_cobol_data_item(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract COBOL data item declaration"""
        try:
            start_idx = start_line - 1
            line = lines[start_idx]
            
            # Look for period or next data item
            for i in range(start_idx + 1, min(start_idx + 3, len(lines))):
                next_line = lines[i].strip()
                if next_line.startswith('.') or re.match(r'^\d{2}\s+', next_line):
                    break
                line += '\n' + next_line
            
            return line
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _ast_to_dict(self, node) -> Dict[str, Any]:
        """Convert AST node to dictionary"""
        if isinstance(node, ast.AST):
            result = {
                'node_type': node.__class__.__name__,
                'lineno': getattr(node, 'lineno', None),
                'col_offset': getattr(node, 'col_offset', None)
            }
            
            for field, value in ast.iter_fields(node):
                result[field] = self._ast_to_dict(value)
            
            return result
        elif isinstance(node, list):
            return [self._ast_to_dict(item) for item in node]
        else:
            return node 

    async def _parse_go_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse Go file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "GoFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract package declaration
                if line.startswith('package '):
                    package_name = line[8:]
                    ast_tree["children"].append({
                        "node_type": "PackageDeclaration",
                        "line": i,
                        "package": package_name
                    })
                
                # Extract imports
                elif line.startswith('import '):
                    import_stmt = line[7:].strip('"')
                    imports.append(import_stmt)
                    ast_tree["children"].append({
                        "node_type": "ImportDeclaration",
                        "line": i,
                        "import": import_stmt
                    })
                
                # Extract function declarations with full body
                elif re.match(r'func\s+\w+\s*\(', line):
                    func_match = re.search(r'func\s+(\w+)', line)
                    if func_match:
                        func_name = func_match.group(1)
                        func_code = self._extract_code_block(lines, i, content)
                        functions.append({
                            "name": func_name,
                            "line": i,
                            "type": "function",
                            "full_code": func_code
                        })
                        ast_tree["children"].append({
                            "node_type": "FunctionDeclaration",
                            "name": func_name,
                            "line": i,
                            "full_code": func_code
                        })
                
                # Extract struct declarations with full body
                elif line.startswith('type ') and 'struct' in line:
                    struct_match = re.search(r'type\s+(\w+)', line)
                    if struct_match:
                        struct_name = struct_match.group(1)
                        struct_code = self._extract_code_block(lines, i, content)
                        classes.append({
                            "name": struct_name,
                            "line": i,
                            "type": "struct",
                            "full_code": struct_code
                        })
                        ast_tree["children"].append({
                            "node_type": "StructDeclaration",
                            "name": struct_name,
                            "line": i,
                            "full_code": struct_code
                        })
                
                # Extract variable declarations with full assignment
                elif re.match(r'(var|const)\s+\w+', line):
                    var_match = re.search(r'(var|const)\s+(\w+)', line)
                    if var_match:
                        var_kind = var_match.group(1)
                        var_name = var_match.group(2)
                        var_code = self._extract_variable_declaration(lines, i, content)
                        variables.append({
                            "name": var_name,
                            "kind": var_kind,
                            "line": i,
                            "full_code": var_code
                        })
                        ast_tree["children"].append({
                            "node_type": "VariableDeclaration",
                            "name": var_name,
                            "line": i,
                            "kind": var_kind,
                            "full_code": var_code
                        })
            
            return {
                "file_path": file_path,
                "language": "go",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse Go file {file_path}: {str(e)}")
            return None
    
    async def _parse_rust_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse Rust file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "RustFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract use statements (imports)
                if line.startswith('use '):
                    use_stmt = line[4:].rstrip(';')
                    imports.append(use_stmt)
                    ast_tree["children"].append({
                        "node_type": "UseDeclaration",
                        "line": i,
                        "use": use_stmt
                    })
                
                # Extract function declarations with full body
                elif re.match(r'fn\s+\w+\s*\(', line):
                    func_match = re.search(r'fn\s+(\w+)', line)
                    if func_match:
                        func_name = func_match.group(1)
                        func_code = self._extract_code_block(lines, i, content)
                        functions.append({
                            "name": func_name,
                            "line": i,
                            "type": "function",
                            "full_code": func_code
                        })
                        ast_tree["children"].append({
                            "node_type": "FunctionDeclaration",
                            "name": func_name,
                            "line": i,
                            "full_code": func_code
                        })
                
                # Extract struct declarations with full body
                elif line.startswith('struct ') or line.startswith('pub struct '):
                    struct_match = re.search(r'struct\s+(\w+)', line)
                    if struct_match:
                        struct_name = struct_match.group(1)
                        struct_code = self._extract_code_block(lines, i, content)
                        classes.append({
                            "name": struct_name,
                            "line": i,
                            "type": "struct",
                            "full_code": struct_code
                        })
                        ast_tree["children"].append({
                            "node_type": "StructDeclaration",
                            "name": struct_name,
                            "line": i,
                            "full_code": struct_code
                        })
                
                # Extract variable declarations with full assignment
                elif re.match(r'let\s+\w+', line):
                    var_match = re.search(r'let\s+(\w+)', line)
                    if var_match:
                        var_name = var_match.group(1)
                        var_code = self._extract_variable_declaration(lines, i, content)
                        variables.append({
                            "name": var_name,
                            "kind": "let",
                            "line": i,
                            "full_code": var_code
                        })
                        ast_tree["children"].append({
                            "node_type": "VariableDeclaration",
                            "name": var_name,
                            "line": i,
                            "kind": "let",
                            "full_code": var_code
                        })
            
            return {
                "file_path": file_path,
                "language": "rust",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse Rust file {file_path}: {str(e)}")
            return None
    
    async def _parse_php_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse PHP file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "PHPFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract require/include statements
                if line.startswith('require ') or line.startswith('include ') or line.startswith('require_once ') or line.startswith('include_once '):
                    import_stmt = line
                    imports.append(import_stmt)
                    ast_tree["children"].append({
                        "node_type": "IncludeDeclaration",
                        "line": i,
                        "include": import_stmt
                    })
                
                # Extract function declarations with full body
                elif re.match(r'function\s+\w+\s*\(', line):
                    func_match = re.search(r'function\s+(\w+)', line)
                    if func_match:
                        func_name = func_match.group(1)
                        func_code = self._extract_code_block(lines, i, content)
                        functions.append({
                            "name": func_name,
                            "line": i,
                            "type": "function",
                            "full_code": func_code
                        })
                        ast_tree["children"].append({
                            "node_type": "FunctionDeclaration",
                            "name": func_name,
                            "line": i,
                            "full_code": func_code
                        })
                
                # Extract class declarations with full body
                elif line.startswith('class '):
                    class_match = re.search(r'class\s+(\w+)', line)
                    if class_match:
                        class_name = class_match.group(1)
                        class_code = self._extract_code_block(lines, i, content)
                        classes.append({
                            "name": class_name,
                            "line": i,
                            "full_code": class_code
                        })
                        ast_tree["children"].append({
                            "node_type": "ClassDeclaration",
                            "name": class_name,
                            "line": i,
                            "full_code": class_code
                        })
                
                # Extract variable declarations with full assignment
                elif re.match(r'\$\w+\s*=', line):
                    var_match = re.search(r'\$(\w+)', line)
                    if var_match:
                        var_name = var_match.group(1)
                        var_code = self._extract_variable_declaration(lines, i, content)
                        variables.append({
                            "name": var_name,
                            "kind": "variable",
                            "line": i,
                            "full_code": var_code
                        })
                        ast_tree["children"].append({
                            "node_type": "VariableDeclaration",
                            "name": var_name,
                            "line": i,
                            "kind": "variable",
                            "full_code": var_code
                        })
            
            return {
                "file_path": file_path,
                "language": "php",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse PHP file {file_path}: {str(e)}")
            return None
    
    async def _parse_ruby_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse Ruby file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "RubyFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract require statements
                if line.startswith('require ') or line.startswith('require_relative '):
                    import_stmt = line
                    imports.append(import_stmt)
                    ast_tree["children"].append({
                        "node_type": "RequireDeclaration",
                        "line": i,
                        "require": import_stmt
                    })
                
                # Extract method definitions with full body
                elif re.match(r'def\s+\w+', line):
                    method_match = re.search(r'def\s+(\w+)', line)
                    if method_match:
                        method_name = method_match.group(1)
                        method_code = self._extract_code_block(lines, i, content)
                        functions.append({
                            "name": method_name,
                            "line": i,
                            "type": "method",
                            "full_code": method_code
                        })
                        ast_tree["children"].append({
                            "node_type": "MethodDeclaration",
                            "name": method_name,
                            "line": i,
                            "full_code": method_code
                        })
                
                # Extract class declarations with full body
                elif line.startswith('class '):
                    class_match = re.search(r'class\s+(\w+)', line)
                    if class_match:
                        class_name = class_match.group(1)
                        class_code = self._extract_code_block(lines, i, content)
                        classes.append({
                            "name": class_name,
                            "line": i,
                            "full_code": class_code
                        })
                        ast_tree["children"].append({
                            "node_type": "ClassDeclaration",
                            "name": class_name,
                            "line": i,
                            "full_code": class_code
                        })
                
                # Extract variable declarations with full assignment
                elif re.match(r'@\w+\s*=', line) or re.match(r'@@\w+\s*=', line) or re.match(r'\$\w+\s*=', line):
                    var_match = re.search(r'(@@?|\$)(\w+)', line)
                    if var_match:
                        var_prefix = var_match.group(1)
                        var_name = var_match.group(2)
                        var_code = self._extract_variable_declaration(lines, i, content)
                        variables.append({
                            "name": var_name,
                            "kind": "instance" if var_prefix == "@" else "class" if var_prefix == "@@" else "global",
                            "line": i,
                            "full_code": var_code
                        })
                        ast_tree["children"].append({
                            "node_type": "VariableDeclaration",
                            "name": var_name,
                            "line": i,
                            "kind": "instance" if var_prefix == "@" else "class" if var_prefix == "@@" else "global",
                            "full_code": var_code
                        })
            
            return {
                "file_path": file_path,
                "language": "ruby",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse Ruby file {file_path}: {str(e)}")
            return None
    
    async def _parse_sql_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse SQL file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "SQLFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract CREATE statements
                if line.upper().startswith('CREATE '):
                    create_type = line.split()[1].upper()
                    create_code = self._extract_sql_statement(lines, i, content)
                    functions.append({
                        "name": f"CREATE_{create_type}",
                        "line": i,
                        "type": "create",
                        "full_code": create_code
                    })
                    ast_tree["children"].append({
                        "node_type": "CreateStatement",
                        "type": create_type,
                        "line": i,
                        "full_code": create_code
                    })
                
                # Extract INSERT statements
                elif line.upper().startswith('INSERT '):
                    insert_code = self._extract_sql_statement(lines, i, content)
                    functions.append({
                        "name": "INSERT",
                        "line": i,
                        "type": "insert",
                        "full_code": insert_code
                    })
                    ast_tree["children"].append({
                        "node_type": "InsertStatement",
                        "line": i,
                        "full_code": insert_code
                    })
                
                # Extract SELECT statements
                elif line.upper().startswith('SELECT '):
                    select_code = self._extract_sql_statement(lines, i, content)
                    functions.append({
                        "name": "SELECT",
                        "line": i,
                        "type": "select",
                        "full_code": select_code
                    })
                    ast_tree["children"].append({
                        "node_type": "SelectStatement",
                        "line": i,
                        "full_code": select_code
                    })
                
                # Extract UPDATE statements
                elif line.upper().startswith('UPDATE '):
                    update_code = self._extract_sql_statement(lines, i, content)
                    functions.append({
                        "name": "UPDATE",
                        "line": i,
                        "type": "update",
                        "full_code": update_code
                    })
                    ast_tree["children"].append({
                        "node_type": "UpdateStatement",
                        "line": i,
                        "full_code": update_code
                    })
                
                # Extract DELETE statements
                elif line.upper().startswith('DELETE '):
                    delete_code = self._extract_sql_statement(lines, i, content)
                    functions.append({
                        "name": "DELETE",
                        "line": i,
                        "type": "delete",
                        "full_code": delete_code
                    })
                    ast_tree["children"].append({
                        "node_type": "DeleteStatement",
                        "line": i,
                        "full_code": delete_code
                    })
            
            return {
                "file_path": file_path,
                "language": "sql",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse SQL file {file_path}: {str(e)}")
            return None
    
    async def _parse_html_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse HTML file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "HTMLFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract script tags
                if '<script' in line:
                    script_code = self._extract_html_tag(lines, i, content, 'script')
                    functions.append({
                        "name": "script",
                        "line": i,
                        "type": "script",
                        "full_code": script_code
                    })
                    ast_tree["children"].append({
                        "node_type": "ScriptTag",
                        "line": i,
                        "full_code": script_code
                    })
                
                # Extract style tags
                elif '<style' in line:
                    style_code = self._extract_html_tag(lines, i, content, 'style')
                    functions.append({
                        "name": "style",
                        "line": i,
                        "type": "style",
                        "full_code": style_code
                    })
                    ast_tree["children"].append({
                        "node_type": "StyleTag",
                        "line": i,
                        "full_code": style_code
                    })
                
                # Extract link tags (imports)
                elif '<link' in line:
                    link_code = line
                    imports.append(link_code)
                    ast_tree["children"].append({
                        "node_type": "LinkTag",
                        "line": i,
                        "full_code": link_code
                    })
                
                # Extract meta tags
                elif '<meta' in line:
                    meta_code = line
                    variables.append({
                        "name": "meta",
                        "line": i,
                        "type": "meta",
                        "full_code": meta_code
                    })
                    ast_tree["children"].append({
                        "node_type": "MetaTag",
                        "line": i,
                        "full_code": meta_code
                    })
            
            return {
                "file_path": file_path,
                "language": "html",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse HTML file {file_path}: {str(e)}")
            return None
    
    async def _parse_css_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse CSS file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "CSSFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract @import statements
                if line.startswith('@import '):
                    import_stmt = line
                    imports.append(import_stmt)
                    ast_tree["children"].append({
                        "node_type": "ImportRule",
                        "line": i,
                        "import": import_stmt
                    })
                
                # Extract CSS rules
                elif re.match(r'^[.#]?\w+', line) and '{' in line:
                    rule_match = re.search(r'^([.#]?\w+)', line)
                    if rule_match:
                        rule_name = rule_match.group(1)
                        rule_code = self._extract_css_rule(lines, i, content)
                        classes.append({
                            "name": rule_name,
                            "line": i,
                            "type": "css_rule",
                            "full_code": rule_code
                        })
                        ast_tree["children"].append({
                            "node_type": "CSSRule",
                            "name": rule_name,
                            "line": i,
                            "full_code": rule_code
                        })
            
            return {
                "file_path": file_path,
                "language": "css",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse CSS file {file_path}: {str(e)}")
            return None
    
    async def _parse_xml_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse XML file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "XMLFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract XML declarations
                if line.startswith('<?xml'):
                    declaration = line
                    imports.append(declaration)
                    ast_tree["children"].append({
                        "node_type": "XMLDeclaration",
                        "line": i,
                        "declaration": declaration
                    })
                
                # Extract DOCTYPE declarations
                elif line.startswith('<!DOCTYPE'):
                    doctype = line
                    imports.append(doctype)
                    ast_tree["children"].append({
                        "node_type": "DOCTYPEDeclaration",
                        "line": i,
                        "doctype": doctype
                    })
                
                # Extract element tags
                elif re.match(r'^<[^/!]', line):
                    element_match = re.search(r'<(\w+)', line)
                    if element_match:
                        element_name = element_match.group(1)
                        element_code = self._extract_xml_element(lines, i, content)
                        classes.append({
                            "name": element_name,
                            "line": i,
                            "type": "xml_element",
                            "full_code": element_code
                        })
                        ast_tree["children"].append({
                            "node_type": "XMLElement",
                            "name": element_name,
                            "line": i,
                            "full_code": element_code
                        })
            
            return {
                "file_path": file_path,
                "language": "xml",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse XML file {file_path}: {str(e)}")
            return None
    
    async def _parse_json_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse JSON file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "JSONFile",
                "children": []
            }
            
            # Parse JSON content
            try:
                json_data = json.loads(content)
                ast_tree["children"].append({
                    "node_type": "JSONRoot",
                    "data": json_data
                })
            except json.JSONDecodeError:
                # If not valid JSON, treat as text
                ast_tree["children"].append({
                    "node_type": "TextContent",
                    "content": content
                })
            
            return {
                "file_path": file_path,
                "language": "json",
                "imports": [],
                "functions": [],
                "classes": [],
                "variables": [],
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse JSON file {file_path}: {str(e)}")
            return None
    
    async def _parse_yaml_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse YAML file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "YAMLFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            # Parse YAML structure
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract key-value pairs
                if ':' in line and not line.startswith('#'):
                    key_value = line.split(':', 1)
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()
                        variables.append({
                            "name": key,
                            "line": i,
                            "type": "yaml_key",
                            "full_code": line
                        })
                        ast_tree["children"].append({
                            "node_type": "YAMLKeyValue",
                            "key": key,
                            "value": value,
                            "line": i,
                            "full_code": line
                        })
            
            return {
                "file_path": file_path,
                "language": "yaml",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse YAML file {file_path}: {str(e)}")
            return None
    
    async def _parse_toml_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse TOML file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "TOMLFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract sections
                if line.startswith('[') and line.endswith(']'):
                    section_name = line[1:-1]
                    section_code = self._extract_toml_section(lines, i, content)
                    classes.append({
                        "name": section_name,
                        "line": i,
                        "type": "toml_section",
                        "full_code": section_code
                    })
                    ast_tree["children"].append({
                        "node_type": "TOMLSection",
                        "name": section_name,
                        "line": i,
                        "full_code": section_code
                    })
                
                # Extract key-value pairs
                elif '=' in line and not line.startswith('#'):
                    key_value = line.split('=', 1)
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()
                        variables.append({
                            "name": key,
                            "line": i,
                            "type": "toml_key",
                            "full_code": line
                        })
                        ast_tree["children"].append({
                            "node_type": "TOMLKeyValue",
                            "key": key,
                            "value": value,
                            "line": i,
                            "full_code": line
                        })
            
            return {
                "file_path": file_path,
                "language": "toml",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse TOML file {file_path}: {str(e)}")
            return None
    
    async def _parse_ini_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse INI file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "INIFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract sections
                if line.startswith('[') and line.endswith(']'):
                    section_name = line[1:-1]
                    section_code = self._extract_ini_section(lines, i, content)
                    classes.append({
                        "name": section_name,
                        "line": i,
                        "type": "ini_section",
                        "full_code": section_code
                    })
                    ast_tree["children"].append({
                        "node_type": "INISection",
                        "name": section_name,
                        "line": i,
                        "full_code": section_code
                    })
                
                # Extract key-value pairs
                elif '=' in line and not line.startswith('#'):
                    key_value = line.split('=', 1)
                    if len(key_value) == 2:
                        key = key_value[0].strip()
                        value = key_value[1].strip()
                        variables.append({
                            "name": key,
                            "line": i,
                            "type": "ini_key",
                            "full_code": line
                        })
                        ast_tree["children"].append({
                            "node_type": "INIKeyValue",
                            "key": key,
                            "value": value,
                            "line": i,
                            "full_code": line
                        })
            
            return {
                "file_path": file_path,
                "language": "ini",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse INI file {file_path}: {str(e)}")
            return None
    
    async def _parse_markdown_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse Markdown file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "MarkdownFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract headers
                if line.startswith('#'):
                    header_level = len(line) - len(line.lstrip('#'))
                    header_text = line.lstrip('#').strip()
                    functions.append({
                        "name": f"header_{header_level}",
                        "line": i,
                        "type": "header",
                        "full_code": line
                    })
                    ast_tree["children"].append({
                        "node_type": "MarkdownHeader",
                        "level": header_level,
                        "text": header_text,
                        "line": i,
                        "full_code": line
                    })
                
                # Extract code blocks
                elif line.startswith('```'):
                    code_block = self._extract_markdown_code_block(lines, i, content)
                    functions.append({
                        "name": "code_block",
                        "line": i,
                        "type": "code_block",
                        "full_code": code_block
                    })
                    ast_tree["children"].append({
                        "node_type": "MarkdownCodeBlock",
                        "line": i,
                        "full_code": code_block
                    })
            
            return {
                "file_path": file_path,
                "language": "markdown",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse Markdown file {file_path}: {str(e)}")
            return None
    
    async def _parse_dockerfile(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse Dockerfile and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "Dockerfile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract FROM instructions
                if line.upper().startswith('FROM '):
                    from_instruction = line
                    imports.append(from_instruction)
                    ast_tree["children"].append({
                        "node_type": "FROMInstruction",
                        "line": i,
                        "instruction": from_instruction
                    })
                
                # Extract RUN instructions
                elif line.upper().startswith('RUN '):
                    run_instruction = line
                    functions.append({
                        "name": "RUN",
                        "line": i,
                        "type": "run",
                        "full_code": run_instruction
                    })
                    ast_tree["children"].append({
                        "node_type": "RUNInstruction",
                        "line": i,
                        "full_code": run_instruction
                    })
                
                # Extract COPY instructions
                elif line.upper().startswith('COPY '):
                    copy_instruction = line
                    functions.append({
                        "name": "COPY",
                        "line": i,
                        "type": "copy",
                        "full_code": copy_instruction
                    })
                    ast_tree["children"].append({
                        "node_type": "COPYInstruction",
                        "line": i,
                        "full_code": copy_instruction
                    })
                
                # Extract ENV instructions
                elif line.upper().startswith('ENV '):
                    env_instruction = line
                    variables.append({
                        "name": "ENV",
                        "line": i,
                        "type": "environment",
                        "full_code": env_instruction
                    })
                    ast_tree["children"].append({
                        "node_type": "ENVInstruction",
                        "line": i,
                        "full_code": env_instruction
                    })
            
            return {
                "file_path": file_path,
                "language": "dockerfile",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse Dockerfile {file_path}: {str(e)}")
            return None
    
    async def _parse_makefile(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse Makefile and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "Makefile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract targets
                if re.match(r'^\w+:', line):
                    target_name = line.split(':')[0]
                    target_code = self._extract_makefile_target(lines, i, content)
                    functions.append({
                        "name": target_name,
                        "line": i,
                        "type": "target",
                        "full_code": target_code
                    })
                    ast_tree["children"].append({
                        "node_type": "MakefileTarget",
                        "name": target_name,
                        "line": i,
                        "full_code": target_code
                    })
                
                # Extract variable assignments
                elif '=' in line and not line.startswith('\t'):
                    var_match = re.search(r'(\w+)\s*=', line)
                    if var_match:
                        var_name = var_match.group(1)
                        var_code = line
                        variables.append({
                            "name": var_name,
                            "line": i,
                            "type": "makefile_var",
                            "full_code": var_code
                        })
                        ast_tree["children"].append({
                            "node_type": "MakefileVariable",
                            "name": var_name,
                            "line": i,
                            "full_code": var_code
                        })
            
            return {
                "file_path": file_path,
                "language": "makefile",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse Makefile {file_path}: {str(e)}")
            return None
    
    async def _parse_cmake_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Parse CMake file and create AST structure with full code"""
        try:
            ast_tree = {
                "node_type": "CMakeFile",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Extract project declarations
                if line.startswith('project('):
                    project_code = self._extract_cmake_command(lines, i, content)
                    functions.append({
                        "name": "project",
                        "line": i,
                        "type": "project",
                        "full_code": project_code
                    })
                    ast_tree["children"].append({
                        "node_type": "CMakeProject",
                        "line": i,
                        "full_code": project_code
                    })
                
                # Extract add_executable commands
                elif line.startswith('add_executable('):
                    exec_code = self._extract_cmake_command(lines, i, content)
                    functions.append({
                        "name": "add_executable",
                        "line": i,
                        "type": "add_executable",
                        "full_code": exec_code
                    })
                    ast_tree["children"].append({
                        "node_type": "CMakeAddExecutable",
                        "line": i,
                        "full_code": exec_code
                    })
                
                # Extract set commands
                elif line.startswith('set('):
                    set_code = self._extract_cmake_command(lines, i, content)
                    variables.append({
                        "name": "set",
                        "line": i,
                        "type": "cmake_set",
                        "full_code": set_code
                    })
                    ast_tree["children"].append({
                        "node_type": "CMakeSet",
                        "line": i,
                        "full_code": set_code
                    })
            
            return {
                "file_path": file_path,
                "language": "cmake",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse CMake file {file_path}: {str(e)}")
            return None
    
    async def _parse_generic_file(self, file_path: str, content: str, language: str) -> Dict[str, Any]:
        """Parse generic file and create basic AST structure"""
        try:
            ast_tree = {
                "node_type": f"{language.capitalize()}File",
                "children": []
            }
            
            lines = content.split('\n')
            imports = []
            functions = []
            classes = []
            variables = []
            
            # Basic line-by-line parsing
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                if line:
                    # Treat each non-empty line as a statement
                    functions.append({
                        "name": f"line_{i}",
                        "line": i,
                        "type": "statement",
                        "full_code": line
                    })
                    ast_tree["children"].append({
                        "node_type": "Statement",
                        "line": i,
                        "content": line
                    })
            
            return {
                "file_path": file_path,
                "language": language,
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "ast_tree": ast_tree,
                "full_source_code": content
            }
            
        except Exception as e:
            print(f"Failed to parse generic file {file_path}: {str(e)}")
            return None
    
    def _extract_sql_statement(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract complete SQL statement"""
        try:
            start_idx = start_line - 1
            end_idx = start_idx
            
            # Find the end of the SQL statement (semicolon)
            for i in range(start_idx, len(lines)):
                line = lines[i]
                if line.strip().endswith(';'):
                    end_idx = i + 1
                    break
                elif line.strip() and not line.strip().startswith('--'):
                    end_idx = i + 1
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_html_tag(self, lines: List[str], start_line: int, content: str, tag_name: str) -> str:
        """Extract complete HTML tag content"""
        try:
            start_idx = start_line - 1
            end_idx = start_idx
            
            # Find the closing tag
            closing_tag = f"</{tag_name}>"
            for i in range(start_idx, len(lines)):
                line = lines[i]
                if closing_tag in line:
                    end_idx = i + 1
                    break
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_css_rule(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract complete CSS rule"""
        try:
            start_idx = start_line - 1
            end_idx = start_idx
            brace_count = 0
            
            # Find the opening brace
            for i in range(start_idx, len(lines)):
                line = lines[i]
                brace_count += line.count('{') - line.count('}')
                if brace_count > 0:
                    end_idx = i + 1
                    break
            
            # Find the closing brace
            for i in range(end_idx, len(lines)):
                line = lines[i]
                brace_count += line.count('{') - line.count('}')
                if brace_count <= 0:
                    end_idx = i + 1
                    break
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_xml_element(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract complete XML element"""
        try:
            start_idx = start_line - 1
            end_idx = start_idx
            
            # Find the closing tag
            for i in range(start_idx, len(lines)):
                line = lines[i]
                if line.strip().startswith('</'):
                    end_idx = i + 1
                    break
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_toml_section(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract TOML section content"""
        try:
            start_idx = start_line - 1
            end_idx = start_idx
            
            # Find the end of the section
            for i in range(start_idx + 1, len(lines)):
                line = lines[i].strip()
                if line.startswith('[') and line.endswith(']'):
                    break
                end_idx = i + 1
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_ini_section(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract INI section content"""
        try:
            start_idx = start_line - 1
            end_idx = start_idx
            
            # Find the end of the section
            for i in range(start_idx + 1, len(lines)):
                line = lines[i].strip()
                if line.startswith('[') and line.endswith(']'):
                    break
                end_idx = i + 1
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_markdown_code_block(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract Markdown code block"""
        try:
            start_idx = start_line - 1
            end_idx = start_idx
            
            # Find the end of the code block
            for i in range(start_idx + 1, len(lines)):
                line = lines[i]
                if line.startswith('```'):
                    end_idx = i + 1
                    break
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_makefile_target(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract Makefile target content"""
        try:
            start_idx = start_line - 1
            end_idx = start_idx
            
            # Find the end of the target (next target or end of file)
            for i in range(start_idx + 1, len(lines)):
                line = lines[i].strip()
                if line and not line.startswith('\t') and ':' in line:
                    break
                end_idx = i + 1
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""
    
    def _extract_cmake_command(self, lines: List[str], start_line: int, content: str) -> str:
        """Extract CMake command content"""
        try:
            start_idx = start_line - 1
            end_idx = start_idx
            
            # Find the end of the command (closing parenthesis)
            paren_count = 0
            for i in range(start_idx, len(lines)):
                line = lines[i]
                paren_count += line.count('(') - line.count(')')
                if paren_count <= 0:
                    end_idx = i + 1
                    break
            
            return '\n'.join(lines[start_idx:end_idx])
        except:
            return lines[start_line - 1] if start_line <= len(lines) else ""