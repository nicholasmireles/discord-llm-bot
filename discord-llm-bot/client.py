import logging
import re
from typing import List
from discord import Client, Intents, Message

from .lib.cloudflare import CloudFlareWorker

logger = logging.getLogger(__name__)


class ChatBotClient(Client):
    def __init__(self, cloudflare_worker: CloudFlareWorker, *args, **kwargs):
        self.listening_channel = None
        self.cloudflare_worker = cloudflare_worker
        self.transcript: List[str] = []

        intents = Intents.default()
        intents.message_content = True
        super().__init__(*args, intents=intents, **kwargs)

    def add_message_to_transcript(self, message: Message) -> None:
        """
        Add a message to the transcript.
        Args:
            message (discord.Message): The Discord message to add to the transcript.
        """
        self.transcript.append(
            f'"{message.author.global_name if message.author.global_name else message.author.name}"({message.author.name}): {re.sub(r"<.*>", "", message.content)}'
        )

    async def on_ready(self) -> None:
        """
        Event handler for when the bot is ready.
        """

        logger.info(f"We have logged in as {self.user}")

    async def on_message(self, message: Message) -> None:
        """
        Event handler for when a message is received.

        Args:
            message (discord.Message): The Discord message that was received.
        """

        self.add_message_to_transcript(message)
        response = None
        try:
            match message:
                case Message(author=self.user):
                    pass
                case Message(mentions=[self.user]):
                    message.content = re.sub(r"<@.*>", "@NickBot", message.content)
                    self.listening_channel = message.channel
                    self.add_message_to_transcript(message)
                    response = await self.cloudflare_worker.query_model(
                        message, self.transcript
                    )
                case Message(channel=self.listening_channel) if (
                    self.listening_channel is not None
                ):
                    self.add_message_to_transcript(message)
                    if message.content.startswith("$stop"):
                        await self.listening_channel.send("Shutting up :zipper_mouth:")
                        self.listening_channel = None
                        self.transcript.clear()
                    else:
                        response = await self.cloudflare_worker.query_model(
                            message, self.transcript
                        )
                case _:
                    return
        except Exception as e:
            logger.error(e)
            response = "I've got a bug in my brain."
        if response is not None:
            await message.channel.send(response)
