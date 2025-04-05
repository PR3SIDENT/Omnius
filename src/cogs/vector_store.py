import discord
from discord.ext import commands
import os
import json
import logging
import sqlite3
import threading
import time
import asyncio
from datetime import datetime, timedelta
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from config.config import KNOWLEDGE_BASE_PATH
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class VectorStore(commands.Cog):
    """Handles vector embeddings and storage for efficient message processing"""
    
    def __init__(self, bot):
        self.bot = bot
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.Client(Settings(
            persist_directory=os.path.join(os.getenv('KNOWLEDGE_BASE_PATH', 'data/knowledge'), 'vector_store'),
            anonymized_telemetry=False
        ))
        self.collection = self.client.get_or_create_collection(
            name="messages",
            metadata={"hnsw:space": "cosine"}
        )
        self.processing_task = None
        self.message_queue = asyncio.Queue()
        self.bot.loop.create_task(self._process_message_queue())
        logger.info("VectorStore cog initialized")
        
        # Configuration
        self.retention_days = 7  # Keep individual messages for 7 days
        self.batch_size = 100  # Process messages in batches of 100
        
        # Start background thread for processing old messages
        self.processing_thread = threading.Thread(target=self._process_old_messages, daemon=True)
        self.processing_thread.start()
        
    async def _process_message_queue(self):
        """Background task to process messages into embeddings"""
        while True:
            try:
                # Process messages in batches
                batch = []
                try:
                    # Get up to 100 messages or wait for 5 seconds
                    for _ in range(100):
                        try:
                            message = await asyncio.wait_for(self.message_queue.get(), timeout=5.0)
                            batch.append(message)
                        except asyncio.TimeoutError:
                            break
                except Exception as e:
                    logger.error(f"Error getting message batch: {e}")
                    continue

                if batch:
                    await self._save_batch(batch)
                
                await asyncio.sleep(1)  # Prevent CPU overload
            except Exception as e:
                logger.error(f"Error in message processing loop: {e}")
                await asyncio.sleep(5)  # Wait longer on error

    async def _save_batch(self, messages: List[Dict[str, Any]]):
        """Save a batch of messages as embeddings"""
        try:
            # Generate embeddings for the batch
            texts = [msg['content'] for msg in messages]
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Prepare metadata
            metadatas = [{
                'channel_id': str(msg['channel_id']),
                'author_id': str(msg['author_id']),
                'timestamp': msg['timestamp'],
                'message_id': str(msg['message_id'])
            } for msg in messages]
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=[f"{msg['channel_id']}_{msg['message_id']}" for msg in messages]
            )
            
            logger.info(f"Saved {len(messages)} messages to vector store")
        except Exception as e:
            logger.error(f"Error saving batch to vector store: {e}")

    async def queue_message(self, message: discord.Message):
        """Queue a message for processing into embeddings"""
        try:
            formatted_message = {
                'content': message.content,
                'channel_id': str(message.channel.id),
                'author_id': str(message.author.id),
                'timestamp': message.created_at.isoformat(),
                'message_id': str(message.id)
            }
            await self.message_queue.put(formatted_message)
        except Exception as e:
            logger.error(f"Error queueing message: {e}")

    def _process_old_messages(self):
        """Background thread to process old messages into embeddings"""
        while True:
            try:
                # Sleep for 1 hour before checking for old messages
                time.sleep(3600)
                
                # Get messages older than retention period
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                cutoff_str = cutoff_date.isoformat()
                
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get messages that haven't been processed yet
                cursor.execute(
                    '''SELECT id, channel_id, author_name, content, timestamp 
                       FROM messages 
                       WHERE timestamp < ? AND is_deleted = 0
                       AND id NOT IN (SELECT id FROM processed_messages)
                       LIMIT ?''',
                    (cutoff_str, self.batch_size)
                )
                
                messages = [dict(row) for row in cursor.fetchall()]
                
                if not messages:
                    conn.close()
                    continue
                    
                # Process messages in batches
                ids = []
                texts = []
                metadatas = []
                
                for msg in messages:
                    # Skip empty messages
                    if not msg['content'].strip():
                        continue
                        
                    ids.append(msg['id'])
                    texts.append(msg['content'])
                    metadatas.append({
                        'channel_id': msg['channel_id'],
                        'author': msg['author_name'],
                        'timestamp': msg['timestamp']
                    })
                    
                # Generate embeddings
                embeddings = [self._get_embedding(text) for text in texts]
                
                # Filter out None embeddings
                valid_indices = [i for i, emb in enumerate(embeddings) if emb is not None]
                
                if valid_indices:
                    valid_ids = [ids[i] for i in valid_indices]
                    valid_texts = [texts[i] for i in valid_indices]
                    valid_metadatas = [metadatas[i] for i in valid_indices]
                    valid_embeddings = [embeddings[i] for i in valid_indices]
                    
                    # Add to vector database
                    self.collection.add(
                        ids=valid_ids,
                        documents=valid_texts,
                        metadatas=valid_metadatas,
                        embeddings=valid_embeddings
                    )
                    
                    # Mark messages as processed
                    cursor.execute(
                        '''INSERT OR IGNORE INTO processed_messages (id, processed_at)
                           VALUES (?, ?)''',
                        [(id, datetime.now().isoformat()) for id in valid_ids]
                    )
                    
                    conn.commit()
                    
                conn.close()
                
                logger.info(f"Processed {len(valid_indices)} old messages into embeddings")
                
            except Exception as e:
                logger.error(f"Error processing old messages: {e}")
                
    def _init_processed_table(self):
        """Initialize the processed_messages table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_messages (
                id TEXT PRIMARY KEY,
                processed_at TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Processed messages table initialized")
            
        except Exception as e:
            logger.error(f"Error initializing processed_messages table: {e}")
            
    def _search_similar_messages(self, query, limit=5):
        """Search for similar messages using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"channel_id": str(ctx.channel.id)}
            )
            
            # Format results
            similar_messages = []
            
            for i in range(len(results['ids'][0])):
                similar_messages.append({
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
                
            return similar_messages
            
        except Exception as e:
            logger.error(f"Error searching similar messages: {e}")
            return []
            
    @commands.command(name='similar')
    @commands.has_permissions(manage_messages=True)
    async def find_similar(self, ctx, *, query: str):
        """Find messages similar to the query using semantic search"""
        try:
            # Search for similar messages
            similar_messages = self._search_similar_messages(query)
            
            if not similar_messages:
                await ctx.send("No similar messages found.")
                return
                
            # Create embed for results
            embed = discord.Embed(
                title=f"Messages Similar to '{query}'",
                description=f"Found {len(similar_messages)} similar messages",
                color=discord.Color.blue()
            )
            
            for msg in similar_messages:
                metadata = msg['metadata']
                similarity = 1 - msg['distance'] if msg['distance'] is not None else None
                
                similarity_str = f" (Similarity: {similarity:.2f})" if similarity is not None else ""
                
                embed.add_field(
                    name=f"{metadata['author']} - {datetime.fromisoformat(metadata['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}{similarity_str}",
                    value=msg['content'][:1024] or "[No content]",
                    inline=False
                )
                
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error finding similar messages: {e}")
            await ctx.send("The path to similar messages is unclear. Let us try again.")
            
    @commands.command(name='context')
    async def get_context(self, ctx, *, query: str):
        """Get relevant context for a query using semantic search"""
        try:
            # Search for relevant messages
            similar_messages = self._search_similar_messages(query, limit=3)
            
            if not similar_messages:
                await ctx.send("No relevant context found.")
                return
                
            # Format context for LLM
            context = "\n".join([
                f"Message from {datetime.fromisoformat(metadata['timestamp']).strftime('%Y-%m-%d %H:%M')}:\n{doc}"
                for doc, metadata in zip(similar_messages, similar_messages['metadata'])
            ])
            
            # Get LLM response with context
            llm_handler = self.bot.get_cog('LLMHandler')
            if llm_handler:
                response = await llm_handler.generate_response(ctx, query, context)
                await ctx.send(response)
            else:
                await ctx.send("LLM handler not available.")
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            await ctx.send("The path to context is unclear. Let us try again.")
            
    @commands.Cog.listener()
    async def on_message(self, message):
        """Process new messages for vector storage"""
        if message.author.bot:
            return
            
        await self.queue_message(message)

async def setup(bot):
    """Add the VectorStore cog to the bot"""
    await bot.add_cog(VectorStore(bot)) 