# Deployment Guide for Omnius

This guide covers everything you need to know about deploying and building the Omnius Discord bot, including optimizations for different environments.

## Table of Contents

1. [Quick Deployment](#quick-deployment)
2. [Build Process Explained](#build-process-explained)
3. [Resource Requirements](#resource-requirements)
4. [Optimizing Build Performance](#optimizing-build-performance)
5. [Troubleshooting Common Issues](#troubleshooting-common-issues)
6. [Using Prebuilt Images](#using-prebuilt-images)
7. [Advanced Deployment Options](#advanced-deployment-options)

## Quick Deployment

The fastest way to deploy Omnius is using our build script:

```bash
# Linux/macOS
chmod +x build.sh
./build.sh

# Windows (PowerShell)
.\build.ps1
```

This script will:
1. Check system requirements
2. Set up necessary directories
3. Create configuration files
4. Build the Docker image with optimized settings
5. Start the bot

## Build Process Explained

The Docker build completes these steps:

1. **Base setup tools** (~10 seconds)
   - Installing pip, setuptools, wheel

2. **Base Discord dependencies** (1-2 minutes)
   - discord.py and supporting libraries
   - No ML components yet

3. **Embedding model** (3-6 minutes)
   - sentence-transformers for text embeddings
   - First major ML component

4. **Vector database** (3-7 minutes)
   - chromadb for vector storage
   - spacy for text processing

5. **Deep learning framework** (4-10 minutes)
   - PyTorch (CPU version)
   - Largest single dependency

6. **LLM inference engine** (2-6 minutes)
   - llama-cpp-python for running the language model
   - Requires compilation

## Resource Requirements

### Default Resource Allocation

For optimal performance, we set these resources by default:
- Standard runtime: 8GB RAM, 4 CPUs
- Build time: 12GB RAM, 8 CPUs 

These can be adjusted in `docker-compose.yml` and `docker-compose.build.yml` if needed.

### Expected Build Times by System

| System Specs | Expected Build Time | Notes |
|-------------|---------------------|-------|
| High-end (16GB+ RAM, 8+ cores, SSD) | 5-10 minutes | Optimal setup |
| Mid-range (8-12GB RAM, 4-6 cores, SSD) | 10-20 minutes | Recommended minimum |
| Low-end (4GB RAM, 2 cores, HDD) | 25-40+ minutes | May encounter issues |
| Cloud VM (4GB RAM, 2 vCPUs) | 15-30 minutes | Varies by provider |

## Optimizing Build Performance

### Docker Settings Optimization

1. **Resource recommendations**:
   - Memory: Set to 8GB minimum, 12GB+ recommended for best performance
   - CPUs: Provide at least 4 cores, 8+ cores for optimal builds
   - Disk: Ensure 10GB+ free space
   - Swap: Enable if low on memory

2. **BuildKit improvements**:
   ```bash
   # Enable BuildKit
   export DOCKER_BUILDKIT=1
   export COMPOSE_DOCKER_CLI_BUILD=1
   
   # Then build
   docker-compose build
   ```

### Hardware-Specific Tweaks

1. **Low memory systems** (< 8GB RAM):
   - Use the dedicated build script: `./build.sh` or `.\build.ps1`
   - Consider using a prebuilt image (see below)

2. **Slow network connections**:
   - Ensure stable connection during build
   - Consider downloading packages separately and using a local PyPI mirror

3. **Limited Disk Space**:
   ```bash
   # Clean Docker system
   docker system prune -a --volumes
   ```

## Troubleshooting Common Issues

### Build Freezes or Crashes

If a build freezes during a specific stage:

1. Identify which component is causing issues
2. Check Docker logs for errors
3. Try increasing memory/timeout values

Example:
```yaml
# in docker-compose.yml
services:
  omnius:
    build:
      args:
        - PIP_TIMEOUT=600  # Increase timeout to 10 minutes
        - PIP_RETRIES=3    # Allow more retries
```

### "No space left on device"

1. Clear Docker build cache:
   ```bash
   docker builder prune -a
   ```

2. Increase Docker storage in Docker Desktop settings

### "Killed" Message During Build

This usually indicates an out-of-memory condition:

1. Increase Docker memory allocation to at least 8GB, preferably 12GB
2. Try building with higher resource limits:
   ```bash
   docker-compose -f docker-compose.build.yml build
   ```

## Using Prebuilt Images

If you're experiencing issues with building the ML components or need a faster deployment, you can use a prebuilt ML image approach.

### Option 1: Using the Prebuilt Docker Image

We provide a prebuilt Docker image with all ML dependencies already installed. This can save significant build time.

```yaml
# Add this to your docker-compose.yml instead of the build section:
services:
  omnius:
    image: yourusername/omnius:latest  # Replace with your image name
    # ... rest of your configuration remains the same
```

### Option 2: Building a Custom Image for Reuse

You can build the image once and reuse it across multiple deployments:

```bash
# Build the image once (this will take time)
docker build -t yourusername/omnius:latest .

# Push to Docker Hub (optional, for sharing)
docker push yourusername/omnius:latest

# Then in your deployments, use the image instead of building
```

### Option 3: Staged Build Approach

If you want more control, you can build the image in stages:

1. Create a `docker-compose.build.yml`:
2. Build once:
   ```bash
   docker-compose -f docker-compose.build.yml build
   ```
3. Use the image in your deployment

### Tradeoffs of Using Prebuilt Images

**Advantages**:
- Much faster deployment
- No need to build dependencies on deployment machine
- Consistent environment across deployments

**Disadvantages**:
- Less customization flexibility
- Need to rebuild and redistribute when dependencies change
- Larger initial download (though not larger than building)

## Advanced Deployment Options

### Running Without ML Features

While the ML features are core to Omnius's functionality, you can run a minimal version for testing by setting:

```
ENABLE_ML=false
```

in your `.env` file or as an environment variable in docker-compose.yml.

### Using Custom Models

To use your own LLM model instead of Mistral 7B:

1. Place your model file in the `models/` directory
2. Update your `.env` file:
   ```
   LLM_MODEL_PATH=models/your-model-file.gguf
   ```

### Scaling for Multiple Users

For larger Discord servers:

1. Increase container resources in docker-compose.yml
2. Consider using a more powerful LLM model
3. Monitor memory usage and adjust as needed 