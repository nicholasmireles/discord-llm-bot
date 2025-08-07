import logging
import re
from typing import List
from discord import Client, Intents, Message

from .models import ConversationContext, Message as BotMessage, AIResponse
from .lib.pydantic_ai_service import AIService

logger = logging.getLogger(__name__)


class ChatBotClient(Client):
    def __init__(self, ai_service: AIService, *args, **kwargs):
        self.listening_channel = None
        self.ai_service = ai_service
        self.conversation_context = ConversationContext()

        intents = Intents.default()
        intents.message_content = True
        super().__init__(*args, intents=intents, **kwargs)

    def add_message_to_context(self, discord_message: Message) -> BotMessage:
        """
        Add a Discord message to the conversation context.
        Args:
            discord_message (discord.Message): The Discord message to add to the context.
        Returns:
            BotMessage: The converted bot message
        """
        # Clean the message content
        cleaned_content = re.sub(r"<.*>", "", discord_message.content)
        
        # Create bot message
        bot_message = BotMessage(
            author_name=discord_message.author.global_name or discord_message.author.name,
            author_username=discord_message.author.name,
            content=cleaned_content,
            channel_id=discord_message.channel.id,
            is_bot=discord_message.author == self.user
        )
        
        self.conversation_context.add_message(bot_message)
        return bot_message

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
                    discord_message.content = cleaned_content
                    
                    self.listening_channel = discord_message.channel
                    self.conversation_context.current_channel_id = discord_message.channel.id
                    
                    bot_message = self.add_message_to_context(discord_message)
                    response = await self.ai_service.generate_response(
                        self.conversation_context, bot_message
                    )
                    
                case Message(channel=self.listening_channel) if (
                    self.listening_channel is not None
                ):
                    # Message in listening channel
                    bot_message = self.add_message_to_context(discord_message)
                    
                    if discord_message.content.startswith("$stop"):
                        await self.listening_channel.send("Shutting up :zipper_mouth:")
                        self.listening_channel = None
                        self.conversation_context.clear()
                        return
                    else:
                        response = await self.ai_service.generate_response(
                            self.conversation_context, bot_message
                        )
                        
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
                self.conversation_context.clear()
