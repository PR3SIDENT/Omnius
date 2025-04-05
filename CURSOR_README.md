# Omnius Discord Bot - Cursor AI Guide

This guide will help you get started with the Omnius Discord bot in Cursor AI.

## Project Overview

Omnius is an intelligent Discord bot themed around the Dune universe, designed to enhance community engagement for a game launch. The bot is capable of responding to user queries, categorizing information, and learning from interactions.

## Getting Started

1. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Configure the Bot**
   Run the setup script to configure the bot:
   ```bash
   python3 setup.py
   ```
   This will prompt you to enter your Discord bot token and OpenAI API key.

3. **Run the Bot**
   ```bash
   python3 src/main.py
   ```

## Project Structure

- `src/`: Contains the main bot code
  - `main.py`: Entry point for the bot
  - `cogs/`: Contains the bot's cogs (modules)
    - `llm_handler.py`: Handles LLM integration
    - `message_handler.py`: Handles message storage and retrieval
    - `nlp.py`: Handles natural language processing
    - `vector_store.py`: Handles vector embeddings and semantic search
- `config/`: Contains configuration files
  - `config.py`: Contains bot configuration settings
- `data/`: Contains data files
  - `knowledge/`: Contains message data and vector embeddings
- `logs/`: Contains log files
- `Dockerfile`: Contains instructions for building the Docker image
- `docker-compose.yml`: Contains instructions for running the bot with Docker
- `.env`: Contains environment variables (created from .env.example)
- `requirements.txt`: Contains Python dependencies
- `setup.py`: Helps configure the bot

## Available Commands

- `!spice`: Share wisdom about the spice
- `!prescience`: Share a vision of the future
- `!ask [question]`: Ask Omnius a question
- `!analyze [limit]`: Analyze channel activity (requires manage_messages permission)
- `!messages [limit] [include_deleted]`: View recent messages (requires manage_messages permission)
- `!stats`: View message statistics (requires manage_messages permission)
- `!search [query]`: Search for messages containing the query (requires manage_messages permission)
- `!history [message_id]`: View the edit history of a specific message (requires manage_messages permission)
- `!similar [query]`: Find messages similar to the query using semantic search (requires manage_messages permission)
- `!context [query]`: Get relevant context for a query using semantic search

## Docker Deployment

If you prefer to use Docker, you can build and run the bot using:

```bash
docker-compose up -d
```

## Troubleshooting

- **ModuleNotFoundError**: Make sure you have installed all dependencies using `pip3 install -r requirements.txt`
- **Discord Token Error**: Make sure you have set the `DISCORD_TOKEN` environment variable in the `.env` file
- **OpenAI API Error**: Make sure you have set the `OPENAI_API_KEY` environment variable in the `.env` file

## Next Steps

- Customize the bot's responses by modifying the `config.py` file
- Add new commands by creating new methods in the appropriate cog
- Integrate with a different LLM provider by modifying the `llm_handler.py` file 