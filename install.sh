#!/bin/bash

# Nighttime To-Do List - Installation Script
# This script installs the Nighttime To-Do List app to your Applications folder

echo "🌙 Installing Nighttime To-Do List..."

# Check if the app exists
if [ ! -d "dist/Nighttime To-Do.app" ]; then
    echo "❌ Error: App not found. Please run 'python3 setup.py py2app' first."
    exit 1
fi

# Create Applications directory if it doesn't exist
mkdir -p ~/Applications

# Copy the app to Applications folder
echo "📦 Copying app to Applications folder..."
cp -R "dist/Nighttime To-Do.app" ~/Applications/

# Set proper permissions
chmod -R 755 ~/Applications/"Nighttime To-Do.app"

echo "✅ Installation complete!"
echo "🌙 You can now find 'Nighttime To-Do List' in your Applications folder."
echo "💡 You can also drag it to your Dock for easy access."

# Ask if user wants to open the app
read -p "🚀 Would you like to open the app now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    open ~/Applications/"Nighttime To-Do.app"
fi

echo "✨ Enjoy your new to-do list app!"

