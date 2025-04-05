# Omnius Discord Bot

A powerful Discord bot with ML capabilities for intelligent conversations and knowledge management.

## ⚠️ Build Time Expectations ⚠️

**First-time builds will take 5-20 minutes** depending on your system resources. This is normal and expected for ML-based applications!

- The build progresses through 6 stages with clear progress indicators
- Each ML component must be compiled for your specific system
- Subsequent builds will be much faster thanks to Docker caching

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Discord Bot Token
- 8GB+ RAM recommended (12GB+ ideal)
- 5GB+ free disk space
- A stable internet connection

### Recommended: Use the Build Script for Faster Results

```bash
# For Linux/macOS
chmod +x build.sh
./build.sh

# For Windows (PowerShell)
.\build.ps1
```

These scripts will guide you through the build process with optimal settings.

### Alternative: Standard Deployment
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/omnius.git
cd omnius

# 2. Configure your Discord token in the .env file
echo "DISCORD_TOKEN=your_token_here" > .env

# 3. Start the bot (be patient during first build!)
docker-compose up -d
```

## Build Process Explained

The Docker build completes these steps:
1. Installing base setup tools
2. Installing base Discord dependencies
3. Installing embedding model (sentence-transformers)
4. Installing vector database (chromadb and spacy)
5. Installing deep learning framework (PyTorch)
6. Installing LLM inference engine (llama-cpp-python)

You can monitor detailed progress with:
```bash
docker-compose -f docker-compose.build.yml build --progress=plain
```

## Features

### Core Features (All Require ML)
- Message History & Search
- Vector Knowledge Base
- Natural Language Processing
- Local LLM Integration

### Basic Discord Commands
- Help and Status Commands
- Fun Themed Responses
- Administration Tools

## Configuration

All configuration is done through the `.env` file:

```
# Discord Bot Configuration
DISCORD_TOKEN=your_token_here

# LLM Configuration (required for AI responses)
LLM_MODEL_PATH=models/mistral-7b-v0.1.gguf

# Vector Store Configuration
VECTOR_STORE_PATH=data/vector_store
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Available Commands

### Basic Commands
- `!help_omnius` - Show help information
- `!spice` - Get a quote about spice
- `!prescience` - Receive a vision of the future

### ML-Powered Commands
- `!history` - Search through message history
- `!search` - Search the knowledge base
- `!ask <question>` - Ask the LLM a question

## Troubleshooting

### Build Taking Too Long
- This is normal! ML dependencies require compilation
- We allocate 12GB RAM and 8 CPUs during build for optimal performance
- Try using our build script: `./build.sh` or `.\build.ps1`
- First build: 5-20 minutes, later builds: 1-5 minutes

### Memory Issues During Build
- Increase Docker's memory allocation (12GB recommended for optimal performance)
- If using resource-constrained hardware, see `PREBUILT.md` for alternatives
- On low memory systems, you might need to increase Docker swap space

### Limited Docker Resources
- On Docker Desktop, go to Settings → Resources and increase memory (8GB minimum)
- Increase CPU allocation to at least 4 cores (8+ recommended)
- For detailed information, see BUILD_INFO.md

### LLM Model Issues
- Make sure you've downloaded the model file to the models directory
- Run `python scripts/download_model.py` to get the default model

### Limited Disk Space
- ML dependencies and models require about 5GB of space
- Try running `docker system prune` to clear unused Docker data

## Resources
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Bot Invitation Guide](https://discordjs.guide/preparations/adding-your-bot-to-servers.html)

## 🌟 Features

- **Local LLM Integration**: Powered by Mistral 7B in GGUF format
- **Dune Theme**: Responses styled after the Bene Gesserit
- **Message Storage**: Efficient SQLite-based message storage
- **Vector Search**: Semantic search using ChromaDB
- **Docker Support**: Easy deployment with Docker
- **Health Monitoring**: Built-in health checks and monitoring
- **Resource Efficient**: Optimized for CPU-only operation

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- 4GB RAM minimum
- 4GB disk space
- Discord Bot Token

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/omnius.git
cd omnius
```

2. Run the setup script:
```bash
./setup.sh
```

3. Edit the `.env` file with your Discord token:
```env
DISCORD_TOKEN=your_discord_token_here
```

4. Start the bot:
```bash
docker-compose up -d
```

## 🛠️ Configuration

### Environment Variables

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token_here

# LLM Configuration
LLM_MODEL_PATH=models/mistral-7b-v0.1.gguf
LLM_CONTEXT_SIZE=4096
LLM_THREADS=4

# Vector Store Configuration
VECTOR_STORE_PATH=data/vector_store
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/omnius.log

# Resource Limits
MAX_MEMORY_MB=4096
MAX_CPU_PERCENT=80

# Backup Configuration
BACKUP_DIR=data/backups
BACKUP_RETENTION_DAYS=7
```

### Docker Configuration

The bot is containerized using Docker with the following specifications:

- Base image: Python 3.11-slim
- Multi-stage build for optimization
- Non-root user for security
- Volume mounts for data persistence
- Health checks enabled

## 💬 Commands

### Basic Commands

- `!spice` - Get a random Dune-themed wisdom
- `!prescience` - Receive a vision of the future
- `!ask <question>` - Ask Omnius a question

### Message Management

- `!messages [limit]` - View recent messages (requires manage_messages permission)
- `!stats` - View message statistics (requires manage_messages permission)

## 🔧 Development

### Project Structure

```
omnius/
├── src/
│   ├── cogs/
│   │   ├── llm_handler.py    # LLM integration
│   │   ├── message_handler.py # Message storage
│   │   ├── nlp.py           # NLP processing
│   │   └── vector_store.py  # Vector database
│   ├── main.py              # Bot entry point
│   └── health.py            # Health monitoring
├── models/                  # LLM model storage
├── data/                    # Data storage
├── logs/                    # Log files
├── scripts/                 # Utility scripts
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose config
└── requirements.txt        # Python dependencies
```

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the bot:
```bash
python -m src.main
```

## 📊 Monitoring

### Health Checks

The bot includes built-in health monitoring:

- Memory usage tracking
- Disk space monitoring
- Response time tracking
- Error rate monitoring

Access health status via:
```bash
docker exec omnius python -c "from src.health import check_health; check_health()"
```

### Logging

Logs are stored in `logs/omnius.log` and can be viewed with:
```bash
docker logs omnius
```

## 🔄 Maintenance

### Backups

Create a backup:
```bash
make backup
```

Restore from backup:
```bash
make restore BACKUP_FILE=backups/omnius_2024-04-05.tar.gz
```

### Updates

Update the bot:
```bash
make update
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Mistral AI for the base model
- The GGUF team for the efficient model format
- The Discord.py team for the excellent library
- The Dune universe for inspiration

## 📚 Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Mistral 7B Documentation](https://mistral.ai/models/)
- [Docker Documentation](https://docs.docker.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/) 