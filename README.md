# Code Modernization Tool

A comprehensive tool for analyzing, understanding, and modernizing legacy code using GenAI and ArangoDB.

## Features

- **Project Upload**: Upload projects in various languages (Java, Python, COBOL, etc.)
- **AST Parsing**: Automatic parsing of source code into Abstract Syntax Trees
- **ArangoDB Integration**: Store and query parsed code structures
- **AI-Powered Chat**: Ask questions about your codebase using Azure OpenAI
- **Code Conversion**: Convert code between different programming languages
- **Dependency Management**: Handle language-specific dependencies during conversion

## Tech Stack

- **Frontend**: React with TypeScript
- **Backend**: FastAPI (Python)
- **Database**: ArangoDB
- **AI**: Azure OpenAI integration
- **AST Parsing**: Language-specific parsers (tree-sitter, ast, etc.)

## Project Structure

```
code_modernisation/
├── frontend/                 # React frontend application
├── backend/                  # FastAPI backend server
├── database/                 # ArangoDB setup and schemas
├── parsers/                  # Language-specific AST parsers
├── converters/               # Code conversion modules
├── docker-compose.yml        # Development environment
└── README.md
```

## Quick Start

1. **Setup Environment**:
   ```bash
   docker-compose up -d
   ```

2. **Install Dependencies**:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

3. **Run the Application**:
   ```bash
   # Backend
   cd backend
   uvicorn main:app --reload
   
   # Frontend
   cd frontend
   npm start
   ```

## Usage

1. **Upload Project**: Upload your source code project
2. **Select Language**: Choose the source language (Java, Python, COBOL, etc.)
3. **Parse Code**: Click "Parse" to generate AST and store in ArangoDB
4. **Chat Interface**: Ask questions about your codebase
5. **Code Conversion**: Convert to target language with dependencies

## Supported Languages

- **Source Languages**: Java, Python, COBOL, C++, JavaScript
- **Target Languages**: Python, Java, JavaScript, TypeScript, Go, Rust

## API Endpoints

- `POST /api/upload` - Upload project files
- `POST /api/parse` - Parse uploaded code
- `POST /api/chat` - Chat with AI about codebase
- `POST /api/convert` - Convert code to target language
- `GET /api/projects` - List parsed projects

## Development

See individual component READMEs for detailed development instructions. 