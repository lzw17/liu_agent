#!/bin/bash

# LiuAgent Run Script
echo "🚀 Starting LiuAgent..."

# Check if config exists
if [ ! -f "config/config.toml" ]; then
    echo "❌ Configuration file not found!"
    echo "Please run setup.sh first or copy config.example.toml to config.toml"
    exit 1
fi

# Create directories if they don't exist
mkdir -p data logs uploads

# Start the application
echo "🌟 LiuAgent is starting on http://localhost:8000"
python main.py
