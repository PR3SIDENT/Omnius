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

logger = logging.getLogger(__name__)

class VectorStore(commands.Cog):
    """Handles vector embeddings and storage for efficient message processing"""
    
    def __init__(self, bot):
        self.bot = bot
        self.message_store_path = os.path.join(KNOWLEDGE_BASE_PATH, 'messages')
        self.db_path = os.path.join(self.message_store_path, 'messages.db')
        self.vector_store_path = os.path.join(KNOWLEDGE_BASE_PATH, 'vector_store')
        os.makedirs(self.vector_store_path, exist_ok=True)
        
        # Initialize vector database
        self._init_vector_db()
        
        # Initialize embedding model
        self._init_embedding_model()
        
        # Configuration
        self.retention_days = 7  # Keep individual messages for 7 days
        self.batch_size = 100  # Process messages in batches of 100
        
        # Start background thread for processing old messages
        self.processing_thread = threading.Thread(target=self._process_old_messages, daemon=True)
        self.processing_thread.start()
        
    def _init_vector_db(self):
        """Initialize the vector database"""
        try:
            # Initialize ChromaDB with persistent storage
            self.vector_db = chromadb.PersistentClient(
                path=self.vector_store_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get the messages collection
            self.collection = self.vector_db.get_or_create_collection(
                name="messages",
                metadata={"description": "Discord message embeddings"}
            )
            
            logger.info("Vector database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector database: {e}")
            # Fallback to in-memory database if persistent storage fails
            self.vector_db = chromadb.Client()
            self.collection = self.vector_db.create_collection(name="messages")
            logger.warning("Using in-memory vector database as fallback")
            
    def _init_embedding_model(self):
        """Initialize the embedding model"""
        try:
            # Use a lightweight model suitable for embeddings
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            self.model = None
            
    def _get_embedding(self, text):
        """Generate embedding for a text"""
        if self.model is None:
            return None
            
        try:
            # Generate embedding
            embedding = self.model.encode(text)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
            
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
            query_embedding = self._get_embedding(query)
            
            if query_embedding is None:
                return []
                
            # Search vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
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
    async def find_similar_messages(self, ctx, *, query: str):
        """Find messages similar to the query"""
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
        """Get context for a query using vector similarity"""
        try:
            # Search for similar messages
            similar_messages = self._search_similar_messages(query, limit=3)
            
            if not similar_messages:
                await ctx.send("No relevant context found.")
                return
                
            # Create context string
            context = "Here is some relevant context:\n\n"
            
            for msg in similar_messages:
                metadata = msg['metadata']
                context += f"**{metadata['author']}** ({datetime.fromisoformat(metadata['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}):\n"
                context += f"{msg['content']}\n\n"
                
            # Send context
            await ctx.send(context)
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            await ctx.send("The path to context is unclear. Let us try again.")
            
async def setup(bot):
    """Add the VectorStore cog to the bot"""
    await bot.add_cog(VectorStore(bot)) 