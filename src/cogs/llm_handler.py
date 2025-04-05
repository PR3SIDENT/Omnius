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
from config.config import KNOWLEDGE_BASE_PATH

logger = logging.getLogger(__name__)

class LLMHandler(commands.Cog):
    """Handles LLM integration for intelligent responses"""
    
    def __init__(self, bot):
        self.bot = bot
        self.message_store_path = os.path.join(KNOWLEDGE_BASE_PATH, 'messages')
        self.db_path = os.path.join(self.message_store_path, 'messages.db')
        
        # LLM configuration
        self.context_window = 10  # Number of messages to include for context
        self.response_delay = 1.0  # Delay in seconds before responding
        self.min_confidence = 0.7  # Minimum confidence threshold for responses
        
        # Initialize LLM (placeholder for actual LLM integration)
        self._init_llm()
        
        # Start background thread for processing message queue
        self.message_queue = []
        self.queue_lock = threading.Lock()
        self.processing_thread = threading.Thread(target=self._process_message_queue, daemon=True)
        self.processing_thread.start()
        
    def _init_llm(self):
        """Initialize the LLM (placeholder for actual implementation)"""
        # This is a placeholder for actual LLM initialization
        # In a real implementation, you would initialize your chosen LLM here
        # For example: OpenAI, Hugging Face, or a local model
        logger.info("Initializing LLM handler (placeholder)")
        
    def _get_context_messages(self, channel_id, message_id, limit=10):
        """Get context messages for a given message"""
        try:
            # First, try to get recent messages from the database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get the timestamp of the target message
            cursor.execute('SELECT timestamp FROM messages WHERE id = ?', (message_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return []
                
            target_timestamp = result[0]
            
            # Get messages before the target message
            cursor.execute(
                '''SELECT * FROM messages 
                   WHERE channel_id = ? AND is_deleted = 0 AND timestamp <= ?
                   ORDER BY timestamp DESC 
                   LIMIT ?''',
                (channel_id, target_timestamp, limit)
            )
            
            messages = [dict(row) for row in cursor.fetchall()]
            
            # Parse JSON fields
            for msg in messages:
                msg['attachments'] = json.loads(msg['attachments'])
                msg['embeds'] = json.loads(msg['embeds'])
                msg['edit_history'] = json.loads(msg['edit_history'])
                
            conn.close()
            
            # Reverse to get chronological order
            return list(reversed(messages))
            
        except Exception as e:
            logger.error(f"Error getting context messages: {e}")
            return []
            
    def _get_semantic_context(self, query, limit=5):
        """Get semantically relevant context using the vector store"""
        try:
            # Get the vector store cog
            vector_store = self.bot.get_cog('VectorStore')
            
            if vector_store is None:
                logger.warning("VectorStore cog not found")
                return []
                
            # Search for similar messages
            similar_messages = vector_store._search_similar_messages(query, limit=limit)
            
            return similar_messages
            
        except Exception as e:
            logger.error(f"Error getting semantic context: {e}")
            return []
            
    def _generate_response(self, context_messages, semantic_context, query):
        """Generate a response using the LLM (placeholder implementation)"""
        # This is a placeholder for actual LLM response generation
        # In a real implementation, you would call your chosen LLM here
        
        # For now, we'll return a simple response based on the query
        if "hello" in query.lower() or "hi" in query.lower():
            return "Greetings, human. I am Omnius, the evermind of this server."
        elif "help" in query.lower():
            return "I can assist you with various tasks. Try commands like !spice, !prescience, or !analyze."
        elif "dune" in query.lower():
            return "The spice must flow. Arrakis is the only source of melange in the known universe."
        else:
            # If we have semantic context, mention it
            if semantic_context:
                return f"I found some relevant information: '{semantic_context[0]['content'][:100]}...'"
            else:
                return "I am processing your query. The path is not yet clear."
            
    def _queue_message_for_processing(self, message):
        """Add a message to the processing queue"""
        with self.queue_lock:
            self.message_queue.append(message)
            
    def _process_message_queue(self):
        """Background thread to process queued messages"""
        while True:
            time.sleep(1)  # Check every second
            
            with self.queue_lock:
                if not self.message_queue:
                    continue
                    
                # Process the oldest message in the queue
                message = self.message_queue.pop(0)
                
            try:
                # Get context messages
                context_messages = self._get_context_messages(str(message.channel.id), str(message.id))
                
                # Get semantic context
                semantic_context = self._get_semantic_context(message.content)
                
                # Generate response
                response = self._generate_response(context_messages, semantic_context, message.content)
                
                # Send response after delay
                time.sleep(self.response_delay)
                asyncio.run_coroutine_threadsafe(
                    message.channel.send(response),
                    self.bot.loop
                )
                
            except Exception as e:
                logger.error(f"Error processing message {message.id}: {e}")
                
    @commands.Cog.listener()
    async def on_message(self, message):
        """Process messages for LLM responses"""
        if message.author.bot:
            return
            
        # Check if message is a mention of the bot
        if self.bot.user in message.mentions:
            # Queue message for processing
            self._queue_message_for_processing(message)
            
    @commands.command(name='ask')
    async def ask_omnius(self, ctx, *, question: str):
        """Ask Omnius a question"""
        try:
            # Get context messages
            context_messages = self._get_context_messages(str(ctx.channel.id), str(ctx.message.id))
            
            # Get semantic context
            semantic_context = self._get_semantic_context(question)
            
            # Generate response
            response = self._generate_response(context_messages, semantic_context, question)
            
            # Send response
            await ctx.send(response)
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            await ctx.send("The path to the answer is unclear. Let us try again.")
            
    @commands.command(name='analyze')
    @commands.has_permissions(manage_messages=True)
    async def analyze_channel(self, ctx, limit: int = 50):
        """Analyze channel activity and generate insights"""
        try:
            # Get recent messages
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                '''SELECT * FROM messages 
                   WHERE channel_id = ? AND is_deleted = 0
                   ORDER BY timestamp DESC 
                   LIMIT ?''',
                (str(ctx.channel.id), limit)
            )
            
            messages = [dict(row) for row in cursor.fetchall()]
            
            # Parse JSON fields
            for msg in messages:
                msg['attachments'] = json.loads(msg['attachments'])
                msg['embeds'] = json.loads(msg['embeds'])
                msg['edit_history'] = json.loads(msg['edit_history'])
                
            conn.close()
            
            if not messages:
                await ctx.send("No messages found to analyze in this channel.")
                return
                
            # Generate analysis (placeholder)
            # In a real implementation, you would use the LLM to analyze the messages
            analysis = "Channel Analysis:\n"
            analysis += f"- Total messages analyzed: {len(messages)}\n"
            analysis += f"- Time span: {datetime.fromisoformat(messages[-1]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')} to {datetime.fromisoformat(messages[0]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            # Count unique authors
            authors = set(msg['author_name'] for msg in messages)
            analysis += f"- Unique authors: {len(authors)}\n"
            
            # Count edited messages
            edited = sum(1 for msg in messages if msg['is_edited'])
            analysis += f"- Edited messages: {edited}\n"
            
            # Send analysis
            await ctx.send(f"```\n{analysis}\n```")
            
        except Exception as e:
            logger.error(f"Error analyzing channel: {e}")
            await ctx.send("The path to the analysis is unclear. Let us try again.")
            
async def setup(bot):
    """Add the LLMHandler cog to the bot"""
    await bot.add_cog(LLMHandler(bot)) 