import logging
from discord import Client, Intents, Message

from pydantic_ai import agent
from .models import AIResponse

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
        should_respond = False
        match discord_message:
            case Message(author=self.user):
                should_respond = False

            case Message(mentions=[self.user]):
                should_respond = True

            case Message(channel=self.listening_channel) if (
                self.listening_channel is not None
            ):
                should_respond = True

            case _:
                should_respond = False

        if should_respond:
            response = None
            try:
                agent_result = await self.ai_agent.run(
                    user_prompt=discord_message.content,
                    message_history=self.message_history,
                    output_type=AIResponse,
                )
                response = agent_result.output
            except Exception as e:
                logger.error(f"Error calling AI agent: {e}")
                response = AIResponse(
                    content="I'm sorry, I'm having a hard time thinking right now. :pensive:",
                    should_stop_listening=False,
                )

            await discord_message.channel.send(response.content)

            # If AI wants to stop listening, clear the context
            if response.should_stop_listening:
                self.listening_channel = None
                self.message_history.clear()
            else:
                self.message_history.extend(agent_result.new_messages())

        return
