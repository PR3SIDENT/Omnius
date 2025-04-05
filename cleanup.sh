#!/bin/bash
# Cleanup script for Omnius project

echo "This script will remove redundant files after reorganization."
echo "Make sure you've backed up anything important before proceeding."
read -p "Continue? (y/n): " confirm

if [[ "$confirm" != "y" ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Remove redundant Docker files (now moved to docker/ directory)
echo "Removing redundant Docker files..."
rm -f Dockerfile.ml Dockerfile.simple
rm -f docker-compose.ml.yml docker-compose.simple.yml docker-compose.dev.yml

# Remove redundant requirements files
echo "Removing redundant requirements files..."
rm -f requirements.ml.embeddings.txt
rm -f requirements.ml.vectordb.txt
rm -f requirements.ml.llm.txt

# Remove redundant documentation (now consolidated)
echo "Removing redundant documentation files..."
rm -f BUILD_INFO.md PREBUILT.md ML_BUILD_GUIDE.md DOCKER_OPTIMIZATION.md

# Remove redundant build script
echo "Removing redundant build script..."
rm -f build_ml.ps1

# Remove original Docker files (now in docker/ directory)
echo "Removing original Docker files (copied to docker/ directory)..."
rm -f Dockerfile docker-compose.yml docker-compose.build.yml

echo "Cleanup complete! The project structure is now more organized."
echo "All essential files are preserved in their appropriate locations." 