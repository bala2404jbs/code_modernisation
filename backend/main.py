from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
import uuid
import zipfile
from typing import List, Optional
import json
from datetime import datetime

# Performance configuration
MAX_UPLOAD_FILE_SIZE_MB = 100  # Maximum file size to upload (MB)
MAX_UPLOAD_FILES = 10000  # Maximum number of files to upload

from database.arangodb_client import ArangoDBClient
from parsers.ast_parser import ASTParser
from converters.code_converter import CodeConverter
from services.genai_service import GenAIService
from models.schemas import (
    ProjectUpload,
    ParseRequest,
    ChatRequest,
    ConversionRequest,
    ProjectResponse,
    ChatResponse,
    ConversionResponse
)
from models.framework_config import get_frameworks_for_language, is_valid_framework

app = FastAPI(title="Code Modernization Tool", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db_client = ArangoDBClient()
ast_parser = ASTParser()
code_converter = CodeConverter()
genai_service = GenAIService()

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    print("Starting up Code Modernization Tool...")
    
    # Initialize database with timeout
    try:
        import asyncio
        await asyncio.wait_for(db_client.initialize(), timeout=10.0)
        print("Database initialized successfully")
    except asyncio.TimeoutError:
        print("Warning: Database connection timed out - continuing without database")
    except Exception as e:
        print(f"Warning: Database initialization failed: {str(e)}")
        print("Continuing without database - some features may not work")
    
    # Initialize other services
    try:
        await ast_parser.initialize()
        print("AST parser initialized successfully")
    except Exception as e:
        print(f"Warning: AST parser initialization failed: {str(e)}")
    
    try:
        await code_converter.initialize()
        print("Code converter initialized successfully")
    except Exception as e:
        print(f"Warning: Code converter initialization failed: {str(e)}")
    
    try:
        await genai_service.initialize()
        print("GenAI service initialized successfully")
    except Exception as e:
        print(f"Warning: GenAI service initialization failed: {str(e)}")
    
    print("Server startup complete!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Code Modernization Tool API", "status": "running"}

@app.post("/api/upload")
async def upload_project(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    source_framework: str = Form(""),
    description: str = Form(""),
    project_name: str = Form("")
):
    """Upload project as ZIP file and extract it"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files are allowed")
        
        # Check file size
        max_size_bytes = MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024
        if file.size and file.size > max_size_bytes:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size is {MAX_UPLOAD_FILE_SIZE_MB}MB"
            )
        
        # Generate project ID
        project_id = str(uuid.uuid4())
        project_dir = os.path.join("uploads", project_id)
        
        # Create project directory
        os.makedirs(project_dir, exist_ok=True)
        
        print(f"Uploading project {project_id} with ZIP file: {file.filename}")
        
        # Save the ZIP file temporarily
        zip_path = os.path.join(project_dir, file.filename)
        with open(zip_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract ZIP file
        print(f"Extracting ZIP file to: {project_dir}")
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of all files in zip
                file_list = zip_ref.namelist()
                
                # Filter out unwanted files and macOS metadata
                skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
                                  '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.wav',
                                  '.pdf', '.doc', '.docx', '.xls', '.xlsx',
                                  '.ppt', '.pptx', '.odt', '.ods', '.odp',
                                  '.log', '.tmp', '.temp', '.bak', '.backup',
                                  '.min.js', '.min.css', '.map'}
                
                # macOS metadata folders and files to skip
                skip_macos_patterns = {
                    '__MACOSX',
                    '.DS_Store',
                    'Thumbs.db',
                    '.Spotlight-V100',
                    '.Trashes',
                    'ehthumbs.db',
                    'Desktop.ini'
                }
                
                filtered_files = []
                for file_name in file_list:
                    # Skip directories
                    if file_name.endswith('/'):
                        continue
                    
                    # Skip macOS metadata folders and files
                    if any(pattern in file_name for pattern in skip_macos_patterns):
                        print(f"Skipping macOS metadata: {file_name}")
                        continue
                    
                    # Skip files with unwanted extensions
                    file_ext = os.path.splitext(file_name)[1].lower()
                    if file_ext in skip_extensions:
                        print(f"Skipping file with unwanted extension: {file_name}")
                        continue
                    
                    filtered_files.append(file_name)
                
                # Limit total number of files
                if len(filtered_files) > MAX_UPLOAD_FILES:
                    print(f"Warning: {len(filtered_files)} files in ZIP, limiting to {MAX_UPLOAD_FILES} for performance")
                    filtered_files = filtered_files[:MAX_UPLOAD_FILES]
                
                print(f"Extracting {len(filtered_files)} files from ZIP")
                
                # Extract files
                for i, file_name in enumerate(filtered_files, 1):
                    if i % 100 == 0:
                        print(f"Extraction progress: {i}/{len(filtered_files)} files extracted")
                    
                    # Extract file
                    zip_ref.extract(file_name, project_dir)
                    extracted_files.append(file_name)
            
            # Remove the original ZIP file
            os.remove(zip_path)
            
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to extract ZIP file: {str(e)}")
        
        # Validate framework if provided
        if source_framework and not is_valid_framework(source_language, source_framework):
            raise HTTPException(status_code=400, detail=f"Invalid framework '{source_framework}' for language '{source_language}'")
        
        # Save project metadata
        project_data = {
            "project_id": project_id,
            "project_name": project_name or f"Project_{project_id[:8]}",
            "source_language": source_language,
            "source_framework": source_framework or None,
            "description": description,
            "files": extracted_files,
            "created_at": datetime.now().isoformat(),
            "status": "uploaded"
        }
        
        try:
            await db_client.create_project(project_data)
            print(f"Project {project_id} saved to database")
        except Exception as e:
            print(f"Warning: Failed to save project to database: {str(e)}")
            # Continue without database - project files are still saved locally
        
        print(f"Project {project_id} uploaded and extracted successfully with {len(extracted_files)} files")
        
        return ProjectResponse(
            project_id=project_id,
            project_name=project_data["project_name"],
            source_language=source_language,
            source_framework=source_framework or None,
            description=description,
            files=extracted_files,
            created_at=project_data["created_at"],
            status="uploaded",
            message=f"Project {project_data['project_name']} uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/parse")
async def parse_project(request: ParseRequest):
    """Parse uploaded project files"""
    try:
        project_id = request.project_id
        print(f"Starting parse for project: {project_id}")
        
        # Get project data
        project_data = await db_client.get_project(project_id)
        if not project_data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update status to parsing
        await db_client.update_project_status(project_id, "parsing")
        print(f"Updated project {project_id} status to parsing")
        
        # Get project directory
        project_dir = os.path.join("uploads", project_id)
        if not os.path.exists(project_dir):
            raise HTTPException(status_code=404, detail="Project directory not found")
        
        # Initialize parser
        parser = ASTParser()
        await parser.initialize()
        
        print(f"Parsing project directory: {project_dir}")
        
        # Parse project with progress tracking
        try:
            ast_data = await parser.parse_project(project_dir, project_data["source_language"])
            print(f"Parsing completed: {len(ast_data)} files parsed")
            
            # Store AST data in database
            try:
                await db_client.store_ast_data(project_id, ast_data)
                print(f"AST data saved to database for project {project_id}")
            except Exception as e:
                print(f"Warning: Failed to save AST data to database: {str(e)}")
                # Continue without database - AST data is still available in memory
            
            # Update status to parsed
            try:
                await db_client.update_project_status(project_id, "parsed")
                print(f"Updated project {project_id} status to parsed")
            except Exception as e:
                print(f"Warning: Failed to update project status: {str(e)}")
            
            return {
                "message": "Project parsed successfully",
                "files_parsed": len(ast_data),
                "status": "parsed"
            }
            
        except Exception as parse_error:
            print(f"Parsing failed: {str(parse_error)}")
            await db_client.update_project_status(project_id, "parse_failed")
            raise HTTPException(status_code=500, detail=f"Parsing failed: {str(parse_error)}")
        
    except Exception as e:
        print(f"Parse endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parse failed: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_codebase(chat_request: ChatRequest):
    """Chat with AI about the codebase"""
    try:
        project_id = chat_request.project_id
        question = chat_request.question
        
        # Get project and AST data
        project = await db_client.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        try:
            ast_data = await db_client.get_ast_data(project_id)
            if not ast_data:
                raise HTTPException(status_code=404, detail="Project not parsed yet")
        except Exception as e:
            print(f"Warning: Failed to get AST data from database: {str(e)}")
            raise HTTPException(status_code=404, detail="Project not parsed yet")
        
        # Generate AI response using GenAI
        response = await genai_service.chat_about_codebase(
            question, 
            ast_data, 
            project["source_language"]
        )
        
        return ChatResponse(
            question=question,
            answer=response,
            project_id=project_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/api/convert", response_model=ConversionResponse)
async def convert_code(conversion_request: ConversionRequest):
    """Convert code to target language"""
    try:
        project_id = conversion_request.project_id
        target_language = conversion_request.target_language
        target_framework = conversion_request.target_framework
        
        # Get project and AST data
        project = await db_client.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Validate target framework if provided
        if target_framework and not is_valid_framework(target_language, target_framework):
            raise HTTPException(status_code=400, detail=f"Invalid framework '{target_framework}' for language '{target_language}'")
        
        ast_data = await db_client.get_ast_data(project_id)
        if not ast_data:
            raise HTTPException(status_code=404, detail="Project not parsed yet")
        
        # Convert code using GenAI
        converted_code = await code_converter.convert_code(
            ast_data,
            project["source_language"],
            target_language,
            project.get("source_framework"),
            target_framework
        )
        
        # Generate dependencies file
        dependencies = await code_converter.generate_dependencies(
            target_language,
            converted_code
        )
        
        # Save converted code locally
        output_dir = f"converted/{project_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        await code_converter.save_converted_code(
            output_dir, 
            converted_code, 
            dependencies
        )
        
        return ConversionResponse(
            project_id=project_id,
            target_language=target_language,
            target_framework=target_framework,
            output_directory=output_dir,
            message="Code converted successfully",
            converted_files=converted_code["converted_files"],
            dependencies=dependencies
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.get("/api/download/{project_id}")
async def download_converted_code(project_id: str):
    """Download converted code as a zip file"""
    try:
        # Check if project exists
        project = await db_client.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if converted code exists
        output_dir = f"converted/{project_id}"
        if not os.path.exists(output_dir):
            raise HTTPException(status_code=404, detail="Converted code not found")
        
        # Create zip file
        zip_filename = f"converted_{project_id}.zip"
        zip_path = f"converted/{zip_filename}"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)
        
        # Return the zip file
        return FileResponse(
            path=zip_path,
            filename=zip_filename,
            media_type='application/zip'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/api/projects", response_model=List[ProjectResponse])
async def list_projects():
    """List all projects"""
    try:
        projects = await db_client.list_projects()
        return [
            ProjectResponse(
                project_id=project["project_id"],
                project_name=project["project_name"],
                status=project["status"],
                message=f"Project: {project['project_name']}",
                source_language=project["source_language"],
                description=project["description"],
                files=project["files"],
                created_at=project["created_at"] if "created_at" in project else None
            )
            for project in projects
        ]
    except Exception as e:
        print(f"Database error: {str(e)}")
        # Return empty list if database is not available
        return []

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get specific project details"""
    try:
        project = await db_client.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return ProjectResponse(
            project_id=project["project_id"],
            project_name=project["project_name"],
            status=project["status"],
            message=f"Project: {project['project_name']}",
            source_language=project["source_language"],
            description=project["description"],
            files=project["files"],
            created_at=project["created_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

@app.get("/api/frameworks/{language}")
async def get_frameworks(language: str):
    """Get available frameworks for a specific language"""
    try:
        frameworks = get_frameworks_for_language(language)
        return {
            "language": language,
            "frameworks": frameworks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get frameworks: {str(e)}")

@app.get("/api/progress/{project_id}")
async def get_progress(project_id: str):
    """Get progress status for a project"""
    try:
        project_data = await db_client.get_project(project_id)
        if not project_data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "project_id": project_id,
            "status": project_data.get("status", "unknown"),
            "files_count": len(project_data.get("files", [])),
            "created_at": project_data.get("created_at"),
            "source_language": project_data.get("source_language")
        }
        
    except Exception as e:
        print(f"Progress check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Progress check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 