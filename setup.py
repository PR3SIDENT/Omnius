#!/usr/bin/env python3
"""
Setup script for the Omnius Discord bot.
This script helps the user configure the bot by updating the .env file.
"""

import os
import sys
import getpass

def update_env_file():
    """Update the .env file with user-provided values"""
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    # Check if .env file exists
    if not os.path.exists(env_file):
        print("Error: .env file not found. Please make sure you have copied .env.example to .env")
        return False
    
    # Read the current .env file
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    # Get Discord token
    discord_token = input("Enter your Discord bot token (or press Enter to keep the current value): ")
    if discord_token:
        env_content = env_content.replace("DISCORD_TOKEN=your_discord_token_here", f"DISCORD_TOKEN={discord_token}")
    
    # Get OpenAI API key
    openai_api_key = input("Enter your OpenAI API key (or press Enter to keep the current value): ")
    if openai_api_key:
        env_content = env_content.replace("OPENAI_API_KEY=your_openai_api_key_here", f"OPENAI_API_KEY={openai_api_key}")
    
    # Write the updated .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("Configuration updated successfully!")
    return True

def create_directories():
    """Create necessary directories for the bot"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directories = [
        os.path.join(base_dir, 'data', 'knowledge', 'messages'),
        os.path.join(base_dir, 'data', 'knowledge', 'vector_store'),
        os.path.join(base_dir, 'logs')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    return True

def main():
    """Main function"""
    print("Welcome to the Omnius Discord bot setup!")
    print("This script will help you configure the bot.")
    print()
    
    # Create directories
    if not create_directories():
        print("Error: Failed to create directories")
        return
    
    # Update .env file
    if not update_env_file():
        print("Error: Failed to update .env file")
        return
    
    print()
    print("Setup completed successfully!")
    print("You can now run the bot using: python3 src/main.py")
    print("Or using Docker: docker-compose up -d")

if __name__ == "__main__":
    main() 