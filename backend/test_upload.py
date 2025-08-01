#!/usr/bin/env python3
"""
Test script for zip file upload functionality
"""
import requests
import zipfile
import os
import tempfile
import shutil

def create_test_zip():
    """Create a test zip file with some sample files"""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create some sample files
        sample_files = {
            'main.py': 'print("Hello, World!")',
            'utils.py': 'def helper():\n    return "Helper function"',
            'README.md': '# Test Project\nThis is a test project for upload.',
            'config.json': '{"name": "test", "version": "1.0.0"}'
        }
        
        # Write files to temp directory
        for filename, content in sample_files.items():
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        # Create zip file without macOS metadata
        zip_path = 'test_project.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    # Skip macOS metadata files
                    if not file.startswith('.') and file != '.DS_Store':
                        zipf.write(file_path, arcname)
        
        print(f"Created test zip file: {zip_path}")
        return zip_path
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)

def test_upload():
    """Test the upload endpoint"""
    # Create test zip file
    zip_path = create_test_zip()
    
    try:
        # Prepare the upload data
        files = {'file': open(zip_path, 'rb')}
        data = {
            'source_language': 'python',
            'description': 'Test project for zip upload',
            'project_name': 'Test Project'
        }
        
        # Make the upload request
        print("Uploading test zip file...")
        response = requests.post('http://localhost:8000/api/upload', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"Project ID: {result['project_id']}")
            print(f"Project Name: {result['project_name']}")
            print(f"Files extracted: {len(result['files'])}")
            print(f"Files: {result['files']}")
            return result['project_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    finally:
        # Clean up zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)

def test_projects_list():
    """Test the projects list endpoint"""
    print("\nTesting projects list...")
    response = requests.get('http://localhost:8000/api/projects')
    
    if response.status_code == 200:
        projects = response.json()
        print(f"✅ Found {len(projects)} projects")
        for project in projects:
            print(f"  - {project['project_name']} ({project['project_id']})")
    else:
        print(f"❌ Failed to get projects: {response.status_code}")

if __name__ == "__main__":
    print("🧪 Testing Code Modernization Tool Upload Functionality")
    print("=" * 50)
    
    # Test upload
    project_id = test_upload()
    
    # Test projects list
    test_projects_list()
    
    print("\n✅ Test completed!") 