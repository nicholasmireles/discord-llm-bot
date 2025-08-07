import logging
import os

from .client import ChatBotClient
from .lib.pydantic_ai_service import CloudflareAIService, OpenAIAIService
from .config import BOT_CONFIG

# Set up logging
logging.basicConfig(level=getattr(logging, BOT_CONFIG.logging_level))


def main():
    # Initialize AI service based on configuration
    if BOT_CONFIG.ai_provider == "openai" and BOT_CONFIG.openai:
        ai_service = OpenAIAIService(config=BOT_CONFIG.openai)
    else:
        # Default to Cloudflare
        ai_service = CloudflareAIService(config=BOT_CONFIG.cloudflare)
        # Check API access for Cloudflare
        ai_service.check_api_access()
    
    # Initialize Discord client
    chatbot_client = ChatBotClient(ai_service=ai_service)
    
    # Run the bot
    chatbot_client.run(BOT_CONFIG.discord.token, log_handler=None)


if __name__ == "__main__":
    main()
