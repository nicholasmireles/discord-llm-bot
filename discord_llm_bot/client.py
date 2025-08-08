import logging
import re
from typing import List
from discord import Client, Intents, Message

from pydantic_ai import agent
from .models import ConversationContext, Message as BotMessage, AIResponse

logger = logging.getLogger(__name__)


class ChatBotClient(Client):
    def __init__(self, ai_agent: agent.Agent, *args, **kwargs):
        self.listening_channel = None
        self.ai_agent = ai_agent
        self.message_history = []
        intents = Intents.default()
        intents.message_content = True
        super().__init__(*args, intents=intents, **kwargs)

    async def on_ready(self) -> None:
        """
        Event handler for when the bot is ready.
        """
        logger.info(f"We have logged in as {self.user}")

    async def on_message(self, discord_message: Message) -> None:
        """
        Event handler for when a message is received.

        Args:
            discord_message (discord.Message): The Discord message that was received.
        """
        response = None
        
        try:
            match discord_message:
                case Message(author=self.user):
                    # Ignore bot's own messages
                    return
                    
                case Message(mentions=[self.user]):
                    # Bot was mentioned - start listening
                    cleaned_content = re.sub(r"<@.*>", "@NickBot", discord_message.content)
                    
                    self.listening_channel = discord_message.channel
                    
                    response = await self._generate_response(cleaned_content)
                    
                case Message(channel=self.listening_channel) if (
                    self.listening_channel is not None
                ):
                    # Message in listening channel
                    response = await self._generate_response(discord_message.content)
                        
                case _:
                    # Message not relevant to bot
                    return
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            response = AIResponse(content="I've got a bug in my brain.")
            
        if response is not None:
            await discord_message.channel.send(response.content)
            
            # If AI wants to stop listening, clear the context
            if response.should_stop_listening:
                self.listening_channel = None

    async def _generate_response(self, user_content: str) -> AIResponse:
        """Generate a response using the AI agent."""
        try:
            # Generate response using Pydantic AI agent
            result: agent.AgentRunResult = await self.ai_agent.run(
                user_prompt=user_content,
                message_history=self.message_history
            )

            # Check if we should stop listening and clear history
            if result.output.should_stop_listening:
                self.message_history.clear()
            else:
                self.message_history.extend(result.new_messages())

            return result.output
            
        except Exception as e:
            logger.error(f"Error calling AI agent: {e}")
            return AIResponse(
                content="I'm sorry, I'm having a hard time thinking right now. :pensive:",
                should_stop_listening=False
            )
