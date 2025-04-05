import discord
from discord.ext import commands
import json
import os
import time
from datetime import datetime, timedelta
import logging
import sqlite3
import threading
from config.config import KNOWLEDGE_BASE_PATH

logger = logging.getLogger(__name__)

class MessageHandler(commands.Cog):
    """Handles message storage and processing for Omnius"""
    
    def __init__(self, bot):
        self.bot = bot
        self.message_store_path = os.path.join(KNOWLEDGE_BASE_PATH, 'messages')
        os.makedirs(self.message_store_path, exist_ok=True)
        
        # Initialize database
        self.db_path = os.path.join(self.message_store_path, 'messages.db')
        self._init_db()
        
        # Message batching
        self.message_queue = {}
        self.batch_lock = threading.Lock()
        self.batch_size = 50  # Number of messages to batch before saving
        self.batch_timeout = 60  # Seconds to wait before forcing a save
        
        # Start background thread for batch processing
        self.batch_thread = threading.Thread(target=self._process_batch_queue, daemon=True)
        self.batch_thread.start()
        
    def _init_db(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create messages table with additional fields for message lifecycle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            channel_id TEXT,
            author_id TEXT,
            author_name TEXT,
            content TEXT,
            timestamp TEXT,
            attachments TEXT,
            embeds TEXT,
            is_deleted INTEGER DEFAULT 0,
            is_edited INTEGER DEFAULT 0,
            edit_history TEXT,
            last_updated TEXT
        )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_channel_id ON messages(channel_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_deleted ON messages(is_deleted)')
        
        conn.commit()
        conn.close()
        
    def _format_message(self, message):
        """Format a message for storage"""
        return {
            'id': str(message.id),
            'channel_id': str(message.channel.id),
            'author_id': str(message.author.id),
            'author_name': message.author.name,
            'content': message.content,
            'timestamp': message.created_at.isoformat(),
            'attachments': json.dumps([a.url for a in message.attachments]),
            'embeds': json.dumps([e.to_dict() for e in message.embeds]),
            'is_deleted': 0,
            'is_edited': 0,
            'edit_history': json.dumps([]),
            'last_updated': datetime.now().isoformat()
        }
        
    def _queue_message(self, message_data):
        """Add a message to the batch queue"""
        channel_id = message_data['channel_id']
        
        with self.batch_lock:
            if channel_id not in self.message_queue:
                self.message_queue[channel_id] = []
            self.message_queue[channel_id].append(message_data)
            
            # If batch size reached, trigger save
            if len(self.message_queue[channel_id]) >= self.batch_size:
                self._save_batch(channel_id)
                
    def _save_batch(self, channel_id):
        """Save a batch of messages to the database"""
        with self.batch_lock:
            if channel_id not in self.message_queue or not self.message_queue[channel_id]:
                return
                
            messages = self.message_queue[channel_id]
            self.message_queue[channel_id] = []
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert messages in batch
            cursor.executemany(
                '''INSERT OR REPLACE INTO messages 
                   (id, channel_id, author_id, author_name, content, timestamp, attachments, embeds, 
                    is_deleted, is_edited, edit_history, last_updated)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                [(m['id'], m['channel_id'], m['author_id'], m['author_name'], 
                  m['content'], m['timestamp'], m['attachments'], m['embeds'],
                  m.get('is_deleted', 0), m.get('is_edited', 0), 
                  m.get('edit_history', json.dumps([])), m.get('last_updated', datetime.now().isoformat())) 
                 for m in messages]
            )
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Saved batch of {len(messages)} messages for channel {channel_id}")
            
        except Exception as e:
            logger.error(f"Error saving message batch: {e}")
            
    def _process_batch_queue(self):
        """Background thread to process message batches"""
        while True:
            time.sleep(10)  # Check every 10 seconds
            
            current_time = time.time()
            
            with self.batch_lock:
                for channel_id, messages in list(self.message_queue.items()):
                    if not messages:
                        continue
                        
                    # Save if batch is old enough
                    if current_time - messages[0].get('_queued_time', current_time) > self.batch_timeout:
                        self._save_batch(channel_id)
                        
    def _get_messages(self, channel_id, limit=100, offset=0, include_deleted=False):
        """Get messages from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        if include_deleted:
            cursor.execute(
                '''SELECT * FROM messages 
                   WHERE channel_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT ? OFFSET ?''',
                (channel_id, limit, offset)
            )
        else:
            cursor.execute(
                '''SELECT * FROM messages 
                   WHERE channel_id = ? AND is_deleted = 0
                   ORDER BY timestamp DESC 
                   LIMIT ? OFFSET ?''',
                (channel_id, limit, offset)
            )
        
        messages = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for msg in messages:
            msg['attachments'] = json.loads(msg['attachments'])
            msg['embeds'] = json.loads(msg['embeds'])
            msg['edit_history'] = json.loads(msg['edit_history'])
            
        conn.close()
        return messages
        
    def _get_message_stats(self, channel_id):
        """Get message statistics from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total messages (including deleted)
        cursor.execute(
            'SELECT COUNT(*) FROM messages WHERE channel_id = ?',
            (channel_id,)
        )
        total_messages = cursor.fetchone()[0]
        
        # Get active messages (not deleted)
        cursor.execute(
            'SELECT COUNT(*) FROM messages WHERE channel_id = ? AND is_deleted = 0',
            (channel_id,)
        )
        active_messages = cursor.fetchone()[0]
        
        # Get edited messages
        cursor.execute(
            'SELECT COUNT(*) FROM messages WHERE channel_id = ? AND is_edited = 1',
            (channel_id,)
        )
        edited_messages = cursor.fetchone()[0]
        
        # Get unique authors
        cursor.execute(
            'SELECT COUNT(DISTINCT author_id) FROM messages WHERE channel_id = ?',
            (channel_id,)
        )
        unique_authors = cursor.fetchone()[0]
        
        # Get time span
        cursor.execute(
            '''SELECT MIN(timestamp), MAX(timestamp) 
               FROM messages 
               WHERE channel_id = ?''',
            (channel_id,)
        )
        first_msg, last_msg = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_messages': total_messages,
            'active_messages': active_messages,
            'edited_messages': edited_messages,
            'unique_authors': unique_authors,
            'first_message': first_msg,
            'last_message': last_msg
        }
        
    def _update_message(self, message_id, update_data):
        """Update a message in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current message data
            cursor.execute('SELECT * FROM messages WHERE id = ?', (message_id,))
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"Attempted to update non-existent message: {message_id}")
                conn.close()
                return False
                
            # Convert row to dict
            current_data = dict(zip([col[0] for col in cursor.description], row))
            
            # Update fields
            for key, value in update_data.items():
                if key in current_data:
                    current_data[key] = value
                    
            # Update last_updated timestamp
            current_data['last_updated'] = datetime.now().isoformat()
            
            # Update database
            cursor.execute(
                '''UPDATE messages 
                   SET content = ?, attachments = ?, embeds = ?, 
                       is_deleted = ?, is_edited = ?, edit_history = ?, last_updated = ?
                   WHERE id = ?''',
                (current_data['content'], current_data['attachments'], current_data['embeds'],
                 current_data['is_deleted'], current_data['is_edited'], 
                 current_data['edit_history'], current_data['last_updated'],
                 message_id)
            )
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Updated message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating message {message_id}: {e}")
            return False
            
    def _record_edit(self, message_id, old_content, new_content):
        """Record a message edit in the edit history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current edit history
            cursor.execute('SELECT edit_history FROM messages WHERE id = ?', (message_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Attempted to record edit for non-existent message: {message_id}")
                conn.close()
                return False
                
            edit_history = json.loads(result[0])
            
            # Add new edit record
            edit_record = {
                'timestamp': datetime.now().isoformat(),
                'old_content': old_content,
                'new_content': new_content
            }
            edit_history.append(edit_record)
            
            # Update database
            cursor.execute(
                '''UPDATE messages 
                   SET content = ?, is_edited = 1, edit_history = ?, last_updated = ?
                   WHERE id = ?''',
                (new_content, json.dumps(edit_history), datetime.now().isoformat(), message_id)
            )
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Recorded edit for message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording edit for message {message_id}: {e}")
            return False
        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Store and process incoming messages"""
        if message.author.bot:
            return
            
        try:
            # Format and queue message
            message_data = self._format_message(message)
            message_data['_queued_time'] = time.time()
            self._queue_message(message_data)
            
            # Log message processing
            logger.debug(f"Queued message {message.id} from {message.author.name} in channel {message.channel.name}")
            
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}")
            
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Handle message edits"""
        if before.author.bot:
            return
            
        try:
            # Only process if content actually changed
            if before.content == after.content:
                return
                
            # Record the edit
            self._record_edit(str(before.id), before.content, after.content)
            
            # Log the edit
            logger.debug(f"Recorded edit for message {before.id} from {before.author.name}")
            
        except Exception as e:
            logger.error(f"Error processing message edit {before.id}: {e}")
            
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Handle message deletions"""
        if message.author.bot:
            return
            
        try:
            # Mark message as deleted
            self._update_message(str(message.id), {
                'is_deleted': 1,
                'last_updated': datetime.now().isoformat()
            })
            
            # Log the deletion
            logger.debug(f"Marked message {message.id} as deleted")
            
        except Exception as e:
            logger.error(f"Error processing message deletion {message.id}: {e}")
            
    @commands.command(name='messages')
    @commands.has_permissions(manage_messages=True)
    async def get_messages(self, ctx, limit: int = 10, include_deleted: bool = False):
        """Retrieve recent messages from the current channel"""
        try:
            messages = self._get_messages(str(ctx.channel.id), limit=limit, include_deleted=include_deleted)
            
            if not messages:
                await ctx.send("No messages found in this channel.")
                return
                
            # Create embed for message display
            embed = discord.Embed(
                title=f"Recent Messages in {ctx.channel.name}",
                description="The evermind's record of recent communications",
                color=discord.Color.blue()
            )
            
            for msg in messages:
                status = ""
                if msg['is_deleted']:
                    status = "🗑️ DELETED "
                elif msg['is_edited']:
                    status = "✏️ EDITED "
                    
                embed.add_field(
                    name=f"{status}{msg['author_name']} - {datetime.fromisoformat(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}",
                    value=msg['content'][:1024] or "[No content]",
                    inline=False
                )
                
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error retrieving messages: {e}")
            await ctx.send("The path to the messages is unclear. Let us try again.")
            
    @commands.command(name='stats')
    @commands.has_permissions(manage_messages=True)
    async def message_stats(self, ctx):
        """Display message statistics for the current channel"""
        try:
            stats = self._get_message_stats(str(ctx.channel.id))
            
            # Create embed for statistics
            embed = discord.Embed(
                title=f"Message Statistics for {ctx.channel.name}",
                description="The evermind's analysis of channel activity",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Total Messages",
                value=str(stats['total_messages']),
                inline=True
            )
            
            embed.add_field(
                name="Active Messages",
                value=str(stats['active_messages']),
                inline=True
            )
            
            embed.add_field(
                name="Edited Messages",
                value=str(stats['edited_messages']),
                inline=True
            )
            
            embed.add_field(
                name="Unique Authors",
                value=str(stats['unique_authors']),
                inline=True
            )
            
            if stats['total_messages'] > 0 and stats['first_message'] and stats['last_message']:
                first_message = datetime.fromisoformat(stats['first_message'])
                last_message = datetime.fromisoformat(stats['last_message'])
                time_span = last_message - first_message
                
                embed.add_field(
                    name="Time Span",
                    value=f"{time_span.days} days",
                    inline=True
                )
                
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error calculating message statistics: {e}")
            await ctx.send("The path to the statistics is unclear. Let us try again.")
            
    @commands.command(name='search')
    @commands.has_permissions(manage_messages=True)
    async def search_messages(self, ctx, *, query: str):
        """Search for messages containing the query"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Search for messages containing the query
            cursor.execute(
                '''SELECT * FROM messages 
                   WHERE channel_id = ? AND content LIKE ? 
                   ORDER BY timestamp DESC 
                   LIMIT 10''',
                (str(ctx.channel.id), f'%{query}%')
            )
            
            messages = [dict(row) for row in cursor.fetchall()]
            
            # Parse JSON fields
            for msg in messages:
                msg['attachments'] = json.loads(msg['attachments'])
                msg['embeds'] = json.loads(msg['embeds'])
                msg['edit_history'] = json.loads(msg['edit_history'])
                
            conn.close()
            
            if not messages:
                await ctx.send(f"No messages found containing '{query}'.")
                return
                
            # Create embed for search results
            embed = discord.Embed(
                title=f"Search Results for '{query}'",
                description=f"Found {len(messages)} messages in {ctx.channel.name}",
                color=discord.Color.blue()
            )
            
            for msg in messages:
                status = ""
                if msg['is_deleted']:
                    status = "🗑️ DELETED "
                elif msg['is_edited']:
                    status = "✏️ EDITED "
                    
                embed.add_field(
                    name=f"{status}{msg['author_name']} - {datetime.fromisoformat(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}",
                    value=msg['content'][:1024] or "[No content]",
                    inline=False
                )
                
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            await ctx.send("The path to the search results is unclear. Let us try again.")
            
    @commands.command(name='history')
    @commands.has_permissions(manage_messages=True)
    async def message_history(self, ctx, message_id: str):
        """View the edit history of a message"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get message data
            cursor.execute('SELECT * FROM messages WHERE id = ?', (message_id,))
            message = cursor.fetchone()
            
            if not message:
                await ctx.send(f"Message with ID {message_id} not found.")
                return
                
            message = dict(message)
            message['attachments'] = json.loads(message['attachments'])
            message['embeds'] = json.loads(message['embeds'])
            message['edit_history'] = json.loads(message['edit_history'])
            
            conn.close()
            
            # Create embed for message history
            embed = discord.Embed(
                title=f"Message History for {message_id}",
                description=f"Author: {message['author_name']}",
                color=discord.Color.blue()
            )
            
            # Add current content
            status = "Current"
            if message['is_deleted']:
                status = "🗑️ DELETED"
            elif message['is_edited']:
                status = "✏️ EDITED"
                
            embed.add_field(
                name=f"{status} Content",
                value=message['content'][:1024] or "[No content]",
                inline=False
            )
            
            # Add edit history
            if message['edit_history']:
                for i, edit in enumerate(reversed(message['edit_history'])):
                    embed.add_field(
                        name=f"Edit {len(message['edit_history']) - i} - {datetime.fromisoformat(edit['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}",
                        value=f"**Before:** {edit['old_content'][:500]}\n**After:** {edit['new_content'][:500]}",
                        inline=False
                    )
                    
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error retrieving message history: {e}")
            await ctx.send("The path to the message history is unclear. Let us try again.")
            
async def setup(bot):
    """Add the MessageHandler cog to the bot"""
    await bot.add_cog(MessageHandler(bot)) 