#!/usr/bin/env python3
"""
Debug script to test parsing functionality
"""
import asyncio
import os
from pathlib import Path
from parsers.ast_parser import ASTParser

async def debug_parse():
    """Debug the parsing functionality"""
    print("=== Debugging Parse Functionality ===")
    
    # Initialize parser
    parser = ASTParser()
    await parser.initialize()
    
    # Test with a specific project
    project_id = "b35d683a-c1c6-47ea-b47c-c4f2c7e1d4c5"  # From your JSON
    project_dir = f"uploads/{project_id}"
    
    print(f"\n1. Checking project directory: {project_dir}")
    if os.path.exists(project_dir):
        print("✅ Directory exists")
        
        # List all files
        print(f"\n2. Files in directory:")
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"   - {file_path}")
        
        # Check for Java files specifically
        print(f"\n3. Looking for Java files:")
        java_files = list(Path(project_dir).rglob("*.java"))
        print(f"   Found {len(java_files)} Java files:")
        for file in java_files:
            print(f"   - {file}")
        
        # Test parsing
        print(f"\n4. Testing parsing:")
        try:
            ast_data = await parser.parse_project(project_dir, "java")
            print(f"   Parsing result: {len(ast_data)} files parsed")
            for file_data in ast_data:
                print(f"   - {file_data.get('file_path', 'unknown')}")
                print(f"     Classes: {len(file_data.get('classes', []))}")
                print(f"     Functions: {len(file_data.get('functions', []))}")
                print(f"     Imports: {len(file_data.get('imports', []))}")
        except Exception as e:
            print(f"   ❌ Parsing failed: {str(e)}")
    else:
        print("❌ Directory does not exist")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    asyncio.run(debug_parse()) 