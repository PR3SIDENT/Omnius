#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p data/knowledge/{messages,vector_store} logs
chmod 755 data logs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cp .env.example .env
    print_warning "Please edit .env file with your Discord token and OpenAI API key"
else
    print_warning ".env file already exists. Skipping..."
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root is not recommended. Please run as a regular user."
fi

# Build the Docker image
print_status "Building Docker image..."
docker-compose build

# Print success message
print_status "Setup completed successfully!"
echo
echo "Next steps:"
echo "1. Edit the .env file with your Discord token and OpenAI API key"
echo "2. Run 'docker-compose up -d' to start the bot"
echo "3. Check the logs with 'docker-compose logs -f'"
echo
print_warning "Make sure to keep your .env file secure and never commit it to version control!" 