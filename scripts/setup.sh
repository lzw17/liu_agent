#!/bin/bash

# LiuAgent Setup Script
echo "🚀 Setting up LiuAgent..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs uploads

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if config file exists
if [ ! -f "config/config.toml" ]; then
    echo "⚙️ Creating configuration file..."
    cp config/config.example.toml config/config.toml
    echo "⚠️  Please edit config/config.toml and add your API keys!"
fi

# Setup frontend (if Node.js is available)
if command -v node &> /dev/null; then
    echo "🎨 Setting up frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    echo "✅ Frontend built successfully!"
else
    echo "⚠️  Node.js not found. Frontend will use fallback HTML page."
fi

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit config/config.toml and add your API keys"
echo "2. Run: python main.py"
echo "3. Open http://localhost:8000 in your browser"
echo ""
echo "🔗 API Documentation: http://localhost:8000/docs"
