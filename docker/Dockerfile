# Omnius Discord Bot
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Use build arguments to control parallelism and verbosity
ARG PIP_PROGRESS_BAR=on
ARG PIP_TIMEOUT=100
ARG PIP_RETRIES=3
ARG PIP_VERBOSE=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for CPU-only installation
ENV FORCE_CPU_ONLY=1 \
    NO_CUDA=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1

# Copy requirements
COPY requirements.txt ./

# Set progress messages for each step
RUN echo "=== Installing base setup tools (1/6) ===" && \
    pip install --no-cache-dir setuptools wheel

# Install Python dependencies with clear progress messages
# These are split to allow better caching and clearer progress
RUN echo "=== Installing base dependencies (2/6) ===" && \
    grep -v "sentence-transformers\|chromadb\|spacy\|torch\|llama-cpp-python" requirements.txt > base_requirements.txt && \
    pip install --no-cache-dir -r base_requirements.txt

RUN echo "=== Installing embedding model (3/6) ===" && \
    pip install --no-cache-dir sentence-transformers>=2.2.0

RUN echo "=== Installing vector database (4/6) ===" && \
    pip install --no-cache-dir chromadb>=0.3.0 && \
    pip install --no-cache-dir spacy>=3.5.0

RUN echo "=== Installing torch (5/6) ===" && \
    pip install --no-cache-dir torch>=2.0.0 --extra-index-url https://download.pytorch.org/whl/cpu

RUN echo "=== Installing LLM inference (6/6) ===" && \
    pip install --no-cache-dir llama-cpp-python==0.2.20

# Copy application code
COPY src/ /app/src/
COPY scripts/ /app/scripts/
COPY config/ /app/config/

# Create necessary directories
RUN mkdir -p /app/models /app/data/knowledge /app/logs
RUN touch /app/.env

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    KNOWLEDGE_BASE_PATH=/app/data/knowledge

# Create non-root user for better security
RUN useradd -m -r omnius
RUN chown -R omnius:omnius /app
USER omnius

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the bot
CMD ["python", "-m", "src.main"] 