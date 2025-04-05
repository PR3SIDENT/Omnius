import discord
from discord.ext import commands
import spacy
from transformers import pipeline
import logging
from config.config import NLP_MODEL, TEMPERATURE

logger = logging.getLogger(__name__)

class NLP(commands.Cog):
    """Natural Language Processing capabilities for Omnius"""
    
    def __init__(self, bot):
        self.bot = bot
        self.nlp = spacy.load(NLP_MODEL)
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.text_generator = pipeline("text-generation", model="gpt2")
        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Process incoming messages for NLP tasks"""
        if message.author == self.bot.user:
            return
            
        # Basic message processing
        doc = self.nlp(message.content)
        
        # Extract named entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Analyze sentiment
        sentiment = self.sentiment_analyzer(message.content)[0]
        
        # Log the analysis (for development)
        logger.debug(f"Message: {message.content}")
        logger.debug(f"Entities: {entities}")
        logger.debug(f"Sentiment: {sentiment}")
        
    @commands.command(name='analyze')
    async def analyze(self, ctx, *, text: str):
        """Analyze the given text using NLP"""
        doc = self.nlp(text)
        
        # Create an embed for the analysis
        embed = discord.Embed(
            title="NLP Analysis",
            description="Analysis of your text using the power of the evermind",
            color=discord.Color.blue()
        )
        
        # Add entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        if entities:
            embed.add_field(
                name="Named Entities",
                value="\n".join([f"{ent[0]} ({ent[1]})" for ent in entities]),
                inline=False
            )
            
        # Add sentiment
        sentiment = self.sentiment_analyzer(text)[0]
        embed.add_field(
            name="Sentiment",
            value=f"{sentiment['label']}: {sentiment['score']:.2f}",
            inline=False
        )
        
        # Add key phrases
        key_phrases = [token.text for token in doc if token.pos_ in ['NOUN', 'VERB']]
        if key_phrases:
            embed.add_field(
                name="Key Phrases",
                value=", ".join(key_phrases[:5]),
                inline=False
            )
            
        await ctx.send(embed=embed)
        
    @commands.command(name='generate')
    async def generate(self, ctx, *, prompt: str):
        """Generate text based on the given prompt"""
        try:
            # Generate text
            generated = self.text_generator(
                prompt,
                max_length=100,
                temperature=TEMPERATURE,
                num_return_sequences=1
            )[0]['generated_text']
            
            # Create an embed for the generated text
            embed = discord.Embed(
                title="Text Generation",
                description="The evermind's vision of your prompt",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Prompt",
                value=prompt,
                inline=False
            )
            
            embed.add_field(
                name="Generated Text",
                value=generated,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in text generation: {e}")
            await ctx.send("The path of generation is unclear. Let us try again.")
            
async def setup(bot):
    """Add the NLP cog to the bot"""
    await bot.add_cog(NLP(bot)) 