import logging
import requests
from typing import List

from discord import Message

logger = logging.getLogger(__name__)


class CloudFlareWorker:
    def __init__(self, api_url: str, model: str, token: str, context: str) -> None:
        self.api_url = api_url
        self.model = model
        self.context = context
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def check_api_access(self) -> None:
        """
        Verify that the API access token is valid.
        """

        test_request = {
            "url": "https://api.cloudflare.com/client/v4/user/tokens/verify",
            "headers": self.headers,
        }
        response = requests.get(**test_request, timeout=30)
        response.raise_for_status()

    async def query_model(self, message: Message, transcript: List[str]) -> None:
        """
        Query the LLM Model with the provided prompt and reply.

        Args:
            message (discord.Message): The Discord message to respond to.
            transcript (List[str]): The transcript for the current conversation.
        """

        request = {
            "url": self.api_url + self.model,
            "headers": self.headers,
            "json": {
                "messages": [
                    {"role": "system", "content": self.context},
                    {"role": "system", "content": "\n".join(transcript)},
                    {"role": "user", "content": message.content},
                ]
            },
        }
        server_response = requests.post(**request)

        if server_response.status_code == 200:
            inference = server_response.json()
            response = inference["result"]["response"]
            logger.debug(server_response.text)
        else:
            logger.error(server_response)
            response = "I'm sorry, I'm having a hard time thinking right now. :pensive:"
        return response
