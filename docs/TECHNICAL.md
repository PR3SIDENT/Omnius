# Technical Documentation

## Architecture Overview

### Components

1. **Discord Bot (main.py)**
   - Entry point for the bot
   - Handles command registration
   - Manages extensions/cogs
   - Processes messages and commands

2. **LLM Handler (cogs/llm_handler.py)**
   - Manages local LLM (Mistral 7B)
   - Handles response generation
   - Implements prompt engineering
   - Manages response queue

3. **Message Handler (cogs/message_handler.py)**
   - Stores messages in SQLite
   - Manages message lifecycle
   - Handles message retrieval
   - Implements message statistics

4. **Vector Store (cogs/vector_store.py)**
   - Manages ChromaDB integration
   - Handles vector embeddings
   - Implements semantic search
   - Manages context retrieval

5. **Health Monitor (health.py)**
   - Monitors system resources
   - Tracks performance metrics
   - Implements health checks
   - Manages logging

## Data Flow

1. **Message Processing**
   ```
   Discord Message
   → Message Handler (Store in SQLite)
   → Vector Store (Generate Embeddings)
   → LLM Handler (Generate Response)
   → Discord Channel
   ```

2. **Query Processing**
   ```
   User Query
   → Vector Store (Find Context)
   → LLM Handler (Generate Response)
   → Discord Channel
   ```

## Database Schema

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    channel_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    edited BOOLEAN DEFAULT FALSE,
    deleted BOOLEAN DEFAULT FALSE,
    attachments TEXT,
    embeds TEXT
);
```

### Vector Store
- Collection: `messages`
- Dimensions: 384 (MiniLM-L6-v2)
- Metadata: channel_id, timestamp, author_id

## Resource Management

### Memory Usage
- LLM Model: ~4GB
- Vector Store: ~1GB
- SQLite Database: ~100MB
- Python Runtime: ~200MB

### CPU Usage
- LLM Inference: 4 threads
- Vector Operations: 2 threads
- Database Operations: 1 thread
- Background Tasks: 1 thread

## Performance Optimization

### LLM Optimization
- Context window: 4096 tokens
- Temperature: 0.7
- Top-p: 0.95
- Repeat penalty: 1.1

### Vector Store Optimization
- Batch size: 100
- Index type: HNSW
- Distance metric: Cosine
- Cache size: 1000

### Database Optimization
- WAL mode enabled
- Indexed queries
- Batch inserts
- Regular vacuum

## Error Handling

### LLM Errors
- Model loading failures
- Inference errors
- Context window overflow
- Response generation timeouts

### Database Errors
- Connection failures
- Query timeouts
- Disk space issues
- Corruption detection

### Vector Store Errors
- Embedding generation failures
- Search timeouts
- Index corruption
- Memory pressure

## Monitoring

### Health Checks
- Memory usage threshold: 80%
- Disk usage threshold: 90%
- Response time threshold: 5s
- Error rate threshold: 5%

### Metrics
- Message processing rate
- Response generation time
- Vector search latency
- Database operation time

## Security

### Docker Security
- Non-root user
- Resource limits
- Read-only filesystem
- Network isolation

### Data Security
- Encrypted environment variables
- Secure volume mounts
- Regular backups
- Access controls

## Development Guidelines

### Code Style
- PEP 8 compliance
- Type hints
- Docstring format
- Error handling

### Testing
- Unit tests
- Integration tests
- Performance tests
- Security tests

### Deployment
- Docker best practices
- Environment configuration
- Backup procedures
- Update process

## Troubleshooting

### Common Issues
1. **High Memory Usage**
   - Check LLM context window
   - Monitor vector store size
   - Review batch sizes

2. **Slow Responses**
   - Check CPU usage
   - Monitor response queue
   - Review database queries

3. **Database Errors**
   - Check disk space
   - Verify permissions
   - Review WAL mode

4. **Vector Store Issues**
   - Check index health
   - Monitor embedding cache
   - Review search parameters

## API Reference

### LLM Handler
```python
class LLMHandler(commands.Cog):
    async def generate_response(self, ctx, query: str, context: Optional[str] = None)
    async def _process_response_queue(self)
    async def _generate_response(self, ctx, query: str, context: Optional[str] = None)
```

### Message Handler
```python
class MessageHandler(commands.Cog):
    async def store_message(self, message: discord.Message)
    async def get_messages(self, channel_id: str, limit: int = 10)
    async def get_stats(self, channel_id: str)
```

### Vector Store
```python
class VectorStore(commands.Cog):
    async def add_message(self, message: discord.Message)
    async def search(self, query: str, limit: int = 5)
    async def get_context(self, query: str, limit: int = 3)
```

## Future Improvements

1. **Performance**
   - Response caching
   - Batch processing
   - Query optimization
   - Resource scaling

2. **Features**
   - Multi-model support
   - Advanced analytics
   - Custom commands
   - Plugin system

3. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Alert system
   - Performance profiling

4. **Security**
   - Rate limiting
   - Input validation
   - Audit logging
   - Access control 