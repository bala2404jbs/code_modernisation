from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ProjectUpload(BaseModel):
    project_name: str = Field(..., description="Name of the project")
    source_language: str = Field(..., description="Source programming language")
    source_framework: Optional[str] = Field(None, description="Source framework (e.g., Spring, Django, React)")
    description: Optional[str] = Field(None, description="Project description")

class ParseRequest(BaseModel):
    project_id: str = Field(..., description="ID of the project to parse")

class ChatRequest(BaseModel):
    project_id: str = Field(..., description="ID of the project")
    question: str = Field(..., description="Question about the codebase")

class ConversionRequest(BaseModel):
    project_id: str = Field(..., description="ID of the project to convert")
    target_language: str = Field(..., description="Target programming language")
    target_framework: Optional[str] = Field(None, description="Target framework (e.g., Spring, Django, React)")

class ProjectResponse(BaseModel):
    project_id: str = Field(..., description="Unique project identifier")
    project_name: str = Field(..., description="Name of the project")
    status: str = Field(..., description="Current status of the project")
    message: str = Field(..., description="Response message")
    source_language: Optional[str] = Field(None, description="Source programming language")
    source_framework: Optional[str] = Field(None, description="Source framework")
    description: Optional[str] = Field(None, description="Project description")
    files: Optional[List[str]] = Field(None, description="List of uploaded files")
    created_at: Optional[str] = Field(None, description="Project creation timestamp")

class ChatResponse(BaseModel):
    question: str = Field(..., description="User's question")
    answer: str = Field(..., description="AI-generated answer")
    project_id: str = Field(..., description="Project identifier")

class ConversionResponse(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    target_language: str = Field(..., description="Target programming language")
    target_framework: Optional[str] = Field(None, description="Target framework")
    output_directory: str = Field(..., description="Directory containing converted code")
    message: str = Field(..., description="Conversion status message")
    converted_files: Optional[List[Dict[str, Any]]] = Field(None, description="List of converted files with filename, content, dependencies, and notes")
    dependencies: Optional[Dict[str, Any]] = Field(None, description="Dependencies for target language")

class ASTNode(BaseModel):
    node_type: str = Field(..., description="Type of AST node")
    value: Optional[str] = Field(None, description="Value of the node")
    children: List['ASTNode'] = Field(default_factory=list, description="Child nodes")
    line_number: Optional[int] = Field(None, description="Line number in source")
    column: Optional[int] = Field(None, description="Column number in source")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ASTData(BaseModel):
    file_path: str = Field(..., description="Path to the source file")
    language: str = Field(..., description="Programming language")
    root_node: ASTNode = Field(..., description="Root AST node")
    imports: List[str] = Field(default_factory=list, description="Import statements")
    functions: List[Dict[str, Any]] = Field(default_factory=list, description="Function definitions")
    classes: List[Dict[str, Any]] = Field(default_factory=list, description="Class definitions")
    variables: List[Dict[str, Any]] = Field(default_factory=list, description="Variable declarations")

class ParsedProject(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    ast_data: List[ASTData] = Field(..., description="AST data for all files")
    summary: Dict[str, Any] = Field(..., description="Project summary statistics")

# Framework definitions for different languages
class FrameworkOptions(BaseModel):
    language: str = Field(..., description="Programming language")
    frameworks: List[Dict[str, str]] = Field(..., description="List of available frameworks with name and description")

# Update forward references
ASTNode.model_rebuild() 