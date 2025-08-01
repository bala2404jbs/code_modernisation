#!/bin/bash

echo "🚀 Setting up Code Modernization Tool..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p converted
mkdir -p backend/uploads
mkdir -p backend/converted

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please update .env file with your API keys"
fi

# Install backend dependencies
echo "🐍 Installing Python dependencies..."
cd backend
pip3 install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Start the application with: docker-compose up -d"
echo "3. Access the application at: http://localhost:3000"
echo ""
echo "🔧 Manual setup (if not using Docker):"
echo "1. Start ArangoDB: docker run -p 8529:8529 arangodb:latest"
echo "2. Start backend: cd backend && uvicorn main:app --reload"
echo "3. Start frontend: cd frontend && npm start" 