# Omnius Discord Bot

Omnius is an intelligent Discord bot themed around the Dune universe, designed to enhance community engagement for a game launch. The bot is capable of responding to user queries, categorizing information, and learning from interactions.

## Features

### Core Functionality
- **Dune-themed Commands**: Commands like `!spice` and `!prescience` provide thematic responses
- **Intelligent Responses**: The bot can respond to mentions and direct questions
- **Message Analysis**: Analyze channel activity and generate insights

### Message Management
- **Hybrid Storage Approach**: 
  - Recent messages (7 days) stored individually in SQLite
  - Older messages processed into vector embeddings for efficient retrieval
  - Semantic search capabilities for finding relevant context
- **Message Lifecycle Tracking**: 
  - Track message edits with full history
  - Mark deleted messages while preserving their content
  - View message statistics and history

### Commands
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

## Technical Implementation

### Database
- **SQLite Database**: Stores recent messages (last 7 days)
- **Vector Database (ChromaDB)**: Stores embeddings of older messages
- **Message Batching**: Processes messages in batches for improved performance
- **Tracks Message Lifecycle**: Creation, edits, deletions

### Vector Embeddings
- **Sentence Transformers**: Uses the lightweight `all-MiniLM-L6-v2` model
- **Semantic Search**: Enables finding similar messages based on meaning, not just keywords
- **Efficient Storage**: Embeddings are much smaller than full messages
- **Background Processing**: Automatically processes old messages into embeddings

### LLM Integration
- **Context-Aware Responses**: Uses both recent messages and semantic search for context
- **Placeholder Implementation**: Ready to integrate with various LLM providers
- **Configurable Parameters**: Adjust context window, response delay, confidence threshold

### Scalability
- **Hybrid Storage**: Balances immediate access with long-term efficiency
- **Background Processing**: Dedicated threads for message processing
- **Optimized Queries**: Indexed database and vector search for fast retrieval

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Discord token:
   ```
   DISCORD_TOKEN=your_discord_token_here
   ```
4. Run the bot:
   ```
   python src/main.py
   ```

## Docker Deployment

Build and run using Docker:

```
docker build -t omnius .
docker run -d --name omnius -v $(pwd)/data:/app/data omnius
```

## Configuration

The bot can be configured through environment variables and the `config.py` file:

- `DISCORD_TOKEN`: Your Discord bot token
- `KNOWLEDGE_BASE_PATH`: Path to store message data
- `RETENTION_DAYS`: Number of days to keep individual messages (default: 7)
- `BATCH_SIZE`: Number of messages to process in a batch (default: 100)
- `CONTEXT_WINDOW`: Number of messages to include for context
- `RESPONSE_DELAY`: Delay in seconds before responding
- `MIN_CONFIDENCE`: Minimum confidence threshold for responses

## Extending the Bot

### Adding New Commands
Add new commands by creating methods in the appropriate cog or in the main bot class:

```python
@commands.command(name='command_name')
async def command_method(self, ctx, *args):
    # Command implementation
    await ctx.send("Response")
```

### Integrating with LLMs
To integrate with a specific LLM provider:

1. Modify the `_init_llm` method in `llm_handler.py`
2. Implement the `_generate_response` method to use your chosen LLM
3. Configure the necessary API keys and parameters

## License

This project is licensed under the MIT License - see the LICENSE file for details. 