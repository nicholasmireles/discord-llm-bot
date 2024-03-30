import re
from typing import List

import requests
import yaml
from discord import Client, Intents, Message

INTENTS: Intents = Intents.default()
INTENTS.message_content = True
CONFIG: dict = {}

with open("config.yaml") as f:
    CONFIG = yaml.load(f, Loader=yaml.FullLoader)

class ChatBotClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listening_channel = None
        self.current_conversation: List = []

    async def message_to_context(self, message: Message) -> dict:
        transcript = "\n".join(
            [
                f"\"{m.author.global_name if m.author.global_name else m.author.name}\"({m.author.name}): {re.sub(r"<.*>", "", m.content)}"
                for m in self.current_conversation
            ]
        )
        context = f"""{CONFIG["cloudflare"]["context"]} The following transcript will give you context for the conversation. The messages are in the format "Name"(username): message. Reply with just your message.\n{transcript}"""
        return {
            "messages": [
                {"role": "system", "content": context},
                {"role": "user", "content": message.content},
            ]
        }

    async def query_model(self, message: Message):
        """Query the LLM Model with the provided prompt.

        Args:
            message (discord.Message): The Discord message to respond to.

        Returns:
            str: The model's response stripped of any metadata.
        """

        prompt = await self.message_to_context(message)

        request = {
            "url": CONFIG["cloudflare"]["api_url"],
            "headers": CONFIG["cloudflare"]["headers"],
            "json": prompt,
        }

        print(request)

        server_response = requests.post(**request)

        if server_response.status_code == 200:
            inference = server_response.json()
            response = inference["result"]["response"]
            print(server_response.text)
            await message.channel.send(response)
        else:
            print(server_response)
            await message.channel.send(
                "I'm sorry, I'm having a hard time thinking right now. :pensive:"
            )

    async def on_ready(self):
        print(f"We have logged in as {self.user}")

    async def on_message(self, message: Message):
        try:
            match message:
                case Message(author=self.user):
                    return
                case Message(mentions=[self.user]):
                    message.content = re.sub(r"<@.*>", "@NickBot", message.content)
                    self.listening_channel = message.channel
                    await self.query_model(message)
                case Message(channel=self.listening_channel) if self.listening_channel is not None:
                    self.current_conversation.append(message)
                    if message.content.startswith("$stop"):
                        await self.listening_channel.send("Shutting up :zipper_mouth:")
                        self.listening_channel = None
                    else:
                        await self.query_model(message)
                case _:
                    return
        except Exception as e:
            print(e)
            await message.channel.send(
                "I've got a bug in my brain."
            )



def check_api_access():
    test_request = {
        "url": "https://api.cloudflare.com/client/v4/user/tokens/verify",
        "headers": CONFIG["cloudflare"]["headers"],
    }
    response = requests.get(**test_request, timeout=30)
    response.raise_for_status()


if __name__ == "__main__":
    if CONFIG["env"] == "dev":
        check_api_access()
    client = ChatBotClient(intents=INTENTS)
    client.run(CONFIG["discord"]["token"])
