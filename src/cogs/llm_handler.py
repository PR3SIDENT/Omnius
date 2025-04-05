import discord
from discord.ext import commands
import os
import logging
from typing import Optional, Dict, Any
import json
import asyncio
from datetime import datetime
from llama_cpp import Llama
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

logger = logging.getLogger(__name__)

class LLMHandler(commands.Cog):
    """Handles LLM integration for intelligent responses using local models"""
    
    def __init__(self, bot):
        self.bot = bot
        self._init_llm()
        self.response_queue = asyncio.Queue()
        self.processing_task = None
        self.bot.loop.create_task(self._process_response_queue())
        logger.info("LLMHandler cog initialized")
        
    def _init_llm(self):
        """Initialize the local LLM"""
        try:
            # Get model path from environment or use default
            model_path = os.getenv('LLM_MODEL_PATH', 'models/mistral-7b-v0.1.gguf')
            context_size = int(os.getenv('LLM_CONTEXT_SIZE', '4096'))
            n_threads = int(os.getenv('LLM_THREADS', '4'))
            
            # Initialize the model
            self.model = Llama(
                model_path=model_path,
                n_ctx=context_size,
                n_threads=n_threads,
                n_gpu_layers=0  # CPU only for now
            )
            
            # Load Dune-themed system prompt
            self.system_prompt = """<s>[INST] You are Omnius, an intelligent AI assistant themed around the Dune universe. 
            You speak in a manner reminiscent of the Bene Gesserit, using metaphors related to spice, prescience, and the desert.
            You are wise, mysterious, and occasionally cryptic in your responses.
            You have access to the conversation history and can use it to provide context-aware responses.
            Always maintain your Dune-themed personality while being helpful and informative.
            
            When responding:
            1. Use Dune-themed metaphors and references
            2. Be concise but meaningful
            3. Show wisdom and insight
            4. Maintain a mysterious and ancient tone
            5. Reference spice, prescience, or the desert when relevant
            
            Remember: You are not just an AI, you are the evermind, the keeper of ancient knowledge. [/INST]</s>"""
            
            logger.info(f"Local LLM initialized successfully with model: {model_path}")
            
        except Exception as e:
            logger.error(f"Error initializing local LLM: {e}")
            self.model = None
            self.system_prompt = None

    async def _process_response_queue(self):
        """Background task to process response queue"""
        while True:
            try:
                # Get next response request
                request = await self.response_queue.get()
                
                # Generate and send response
                response = await self._generate_response(
                    request['ctx'],
                    request['query'],
                    request['context']
                )
                
                # Add delay if configured
                if 'delay' in request:
                    await asyncio.sleep(request['delay'])
                
                # Send response
                await request['ctx'].send(response)
                
            except Exception as e:
                logger.error(f"Error processing response queue: {e}")
                await asyncio.sleep(1)

    async def _generate_response(self, ctx, query: str, context: Optional[str] = None) -> str:
        """Generate a response using the local LLM"""
        if not self.model or not self.system_prompt:
            return "The path to wisdom is currently unclear. The LLM is not properly initialized."

        try:
            # Prepare the prompt
            prompt = f"{self.system_prompt}\n\n"
            if context:
                prompt += f"<s>[INST] Here is some relevant context from previous conversations:\n{context}\n\n"
                prompt += f"Based on this context, {query} [/INST]</s>\n\n"
            else:
                prompt += f"<s>[INST] {query} [/INST]</s>\n\n"
            
            # Generate response
            response = self.model(
                prompt,
                max_tokens=500,
                temperature=0.7,
                top_p=0.95,
                repeat_penalty=1.1,
                stop=["</s>", "[INST]"],
                echo=False
            )
            
            return response['choices'][0]['text'].strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "The spice flow is interrupted. I cannot provide a response at this time."

    async def generate_response(self, ctx, query: str, context: Optional[str] = None, delay: float = 0.0) -> None:
        """Queue a response to be generated and sent"""
        try:
            await self.response_queue.put({
                'ctx': ctx,
                'query': query,
                'context': context,
                'delay': delay
            })
        except Exception as e:
            logger.error(f"Error queueing response: {e}")
            await ctx.send("The path to response is blocked. Let us try again.")

    @commands.command(name='ask')
    async def ask(self, ctx, *, query: str):
        """Ask Omnius a question"""
        try:
            # Get context from vector store
            vector_store = self.bot.get_cog('VectorStore')
            context = None
            if vector_store:
                # Search for relevant messages
                query_embedding = vector_store.embedding_model.encode(query).tolist()
                results = vector_store.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=3,
                    where={"channel_id": str(ctx.channel.id)}
                )
                
                if results['documents'][0]:
                    context = "\n".join([
                        f"Message from {datetime.fromisoformat(metadata['timestamp']).strftime('%Y-%m-%d %H:%M')}:\n{doc}"
                        for doc, metadata in zip(results['documents'][0], results['metadatas'][0])
                    ])
            
            # Generate and send response
            await self.generate_response(ctx, query, context, delay=1.0)
            
        except Exception as e:
            logger.error(f"Error in ask command: {e}")
            await ctx.send("The path to knowledge is unclear. Let us try again.")

async def setup(bot):
    """Add the LLMHandler cog to the bot"""
    await bot.add_cog(LLMHandler(bot)) 