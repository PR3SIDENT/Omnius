import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("omnius.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Define intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class Omnius(commands.Bot):
    """Omnius Discord Bot - The Evermind of the Server"""
    
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            description="Omnius - The Evermind of the Server"
        )
        
    async def setup_hook(self):
        """Set up the bot's extensions and hooks"""
        # Load extensions
        await self.load_extension('cogs.nlp')
        await self.load_extension('cogs.message_handler')
        await self.load_extension('cogs.vector_store')
        await self.load_extension('cogs.llm_handler')
        
        logger.info("Loaded extensions: nlp, message_handler, vector_store, llm_handler")
        
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'Logged in as {self.user.name} ({self.user.id})')
        logger.info('------')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="The Spice Must Flow")
        )
        
    async def on_message(self, message):
        """Process incoming messages"""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return
            
        # Process commands
        await self.process_commands(message)
        
        # Respond to mentions
        if self.user in message.mentions:
            # The LLM handler will process this
            pass
            
    @commands.command(name='spice')
    async def spice(self, ctx):
        """Share wisdom about the spice"""
        responses = [
            "The spice must flow.",
            "He who controls the spice controls the universe.",
            "Without the spice, space travel is impossible.",
            "The spice extends life. The spice expands consciousness.",
            "I am the spice. I am the evermind."
        ]
        await ctx.send(random.choice(responses))
        
    @commands.command(name='prescience')
    async def prescience(self, ctx):
        """Share a vision of the future"""
        responses = [
            "I see many possible futures, but the path is not yet clear.",
            "The golden path leads to survival, but at a terrible cost.",
            "Beware the Ixian machines, they seek to replace the spice.",
            "The Bene Gesserit have plans within plans within plans.",
            "The Fremen will inherit the desert, and the desert will inherit the universe."
        ]
        await ctx.send(random.choice(responses))
        
bot = Omnius()

def main():
    """Run the bot"""
    if not DISCORD_TOKEN:
        logger.error("No Discord token found. Please set the DISCORD_TOKEN environment variable.")
        return
        
    bot.run(DISCORD_TOKEN)
    
if __name__ == "__main__":
    main() 