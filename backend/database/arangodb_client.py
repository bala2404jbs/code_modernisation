import os
import json
from typing import List, Dict, Any, Optional
from arango import ArangoClient
from arango.exceptions import ArangoError

class ArangoDBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self.projects_collection = None
        self.ast_collection = None
        
    async def initialize(self):
        """Initialize ArangoDB connection and create collections"""
        import time
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Get connection details from environment
                host = os.getenv("ARANGO_HOST", "dfe0f71e8439.arangodb.cloud")
                port = int(os.getenv("ARANGO_PORT", "8529"))
                username = os.getenv("ARANGO_USER", "root")
                password = os.getenv("ARANGO_PASSWORD", "3QFuyS33nuXJGvUP8vQT")
                db_name = os.getenv("ARANGO_DB", "code_modernisation")
                
                print(f"Attempting to connect to ArangoDB at {host}:{port} (attempt {attempt + 1}/{max_retries})")
                
                # Initialize ArangoDB client
                self.client = ArangoClient(hosts=f"https://{host}:{port}")
                
                # First, connect to the system database to create our database if it doesn't exist
                try:
                    sys_db = self.client.db("_system", username=username, password=password)
                    if not sys_db.has_database(db_name):
                        sys_db.create_database(db_name)
                        print(f"Created database: {db_name}")
                    else:
                        print(f"Database {db_name} already exists")
                except Exception as e:
                    print(f"Warning: Could not create database {db_name}: {str(e)}")
                
                # Connect to our database
                self.db = self.client.db(db_name, username=username, password=password)
                
                # Test the connection
                self.db.properties()
                print("Successfully connected to ArangoDB")
                
                # Create collections if they don't exist
                await self._create_collections()
                
                print("ArangoDB client initialized successfully")
                return
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"Failed to initialize ArangoDB client after {max_retries} attempts")
                    raise
    
    async def _create_collections(self):
        """Create necessary collections in ArangoDB"""
        try:
            # Create projects collection
            try:
                if not self.db.has_collection("projects"):
                    self.projects_collection = self.db.create_collection("projects")
                    print("Created projects collection")
                else:
                    self.projects_collection = self.db.collection("projects")
                    print("Using existing projects collection")
            except Exception as e:
                print(f"Warning: Could not create projects collection: {str(e)}")
                # Create a fallback collection
                self.projects_collection = self.db.create_collection("projects", if_exists=True)
            
            # Create AST data collection
            try:
                if not self.db.has_collection("ast_data"):
                    self.ast_collection = self.db.create_collection("ast_data")
                    print("Created ast_data collection")
                else:
                    self.ast_collection = self.db.collection("ast_data")
                    print("Using existing ast_data collection")
            except Exception as e:
                print(f"Warning: Could not create ast_data collection: {str(e)}")
                # Create a fallback collection
                self.ast_collection = self.db.create_collection("ast_data", if_exists=True)
                
            # Create indexes for better performance (optional)
            try:
                if not self.projects_collection.has_index("project_id"):
                    self.projects_collection.add_index("project_id", fields=["project_id"], unique=True)
                    print("Created project_id index")
            except Exception as e:
                print(f"Warning: Could not create project_id index: {str(e)}")
            
            try:
                if not self.ast_collection.has_index("project_id"):
                    self.ast_collection.add_index("project_id", fields=["project_id"], unique=True)
                    print("Created ast_data project_id index")
            except Exception as e:
                print(f"Warning: Could not create ast_data project_id index: {str(e)}")
                
        except Exception as e:
            print(f"Failed to create collections: {str(e)}")
            raise
    
    async def create_project(self, project_data: Dict[str, Any]) -> str:
        """Create a new project in the database"""
        try:
            # Add _key for ArangoDB
            project_data["_key"] = project_data["project_id"]
            # Add created_at timestamp
            project_data["created_at"] = self._get_current_timestamp()
            
            # Insert project into database
            result = self.projects_collection.insert(project_data)
            return result["_key"]
            
        except Exception as e:
            print(f"Failed to create project: {str(e)}")
            raise
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        try:
            result = self.projects_collection.get(project_id)
            return result
        except Exception as e:
            print(f"Failed to get project {project_id}: {str(e)}")
            return None
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        try:
            cursor = self.db.aql.execute("""
                FOR project IN projects
                SORT project.created_at DESC, project.project_id DESC
                RETURN project
            """)
            return list(cursor)
        except Exception as e:
            print(f"Failed to list projects with sorting: {str(e)}")
            # Fallback: return projects without sorting
            try:
                cursor = self.db.aql.execute("""
                    FOR project IN projects
                    RETURN project
                """)
                return list(cursor)
            except Exception as e2:
                print(f"Failed to list projects without sorting: {str(e2)}")
                return []
    
    async def update_project_status(self, project_id: str, status: str):
        """Update project status"""
        try:
            print('project_id', project_id)
            print('status', status)
            self.projects_collection.update(
                {"_key": project_id},
                {"status": status}
            )
        except Exception as e:
            print(f"Failed to update project status: {str(e)}")
            raise
    
    async def store_ast_data(self, project_id: str, ast_data: List[Dict[str, Any]]):
        """Store AST data for a project"""
        try:
            # Prepare AST data for storage
            ast_document = {
                "_key": project_id,
                "project_id": project_id,
                "ast_data": ast_data,
                "created_at": self._get_current_timestamp(),
                "status": "parsed"
            }
            
            # Insert or update AST data
            try:
                self.ast_collection.insert(ast_document)
                print('AST data stored successfully')
            except ArangoError:
                # Update if document already exists
                self.ast_collection.update(
                    {"_key": project_id},
                    ast_document
                )
                print('AST data updated successfully')
                
        except Exception as e:
            print(f"Failed to store AST data: {str(e)}")
            raise
    
    async def get_ast_data(self, project_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get AST data for a project"""
        try:
            result = self.ast_collection.get(project_id)
            return result.get("ast_data") if result else None
        except Exception as e:
            print(f"Failed to get AST data for project {project_id}: {str(e)}")
            return None
    
    async def search_ast_data(self, project_id: str, query: str) -> List[Dict[str, Any]]:
        """Search AST data using AQL"""
        try:
            cursor = self.db.aql.execute("""
                FOR ast IN ast_data
                FILTER ast.project_id == @project_id
                FOR node IN ast.ast_data[*]
                FILTER CONTAINS(node.node_type, @query) OR 
                       CONTAINS(node.value, @query)
                RETURN node
            """, bind_vars={"project_id": project_id, "query": query})
            
            return list(cursor)
        except Exception as e:
            print(f"Failed to search AST data: {str(e)}")
            return []
    
    async def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """Get summary statistics for a project"""
        try:
            ast_data = await self.get_ast_data(project_id)
            if not ast_data:
                return {}
            
            summary = {
                "total_files": len(ast_data),
                "total_functions": 0,
                "total_classes": 0,
                "total_variables": 0,
                "languages": set()
            }
            
            for file_data in ast_data:
                summary["languages"].add(file_data.get("language", "unknown"))
                summary["total_functions"] += len(file_data.get("functions", []))
                summary["total_classes"] += len(file_data.get("classes", []))
                summary["total_variables"] += len(file_data.get("variables", []))
            
            summary["languages"] = list(summary["languages"])
            return summary
            
        except Exception as e:
            print(f"Failed to get project summary: {str(e)}")
            return {}
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close() 