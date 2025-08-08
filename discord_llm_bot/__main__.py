import logging
import os

from .client import ChatBotClient
from .lib.pydantic_ai_service import create_ai_agent, check_cloudflare_api_access
from .config import BOT_CONFIG

# Set up logging
logging.basicConfig(level=getattr(logging, BOT_CONFIG.logging_level))


def main():
    # Check API access for Cloudflare if using it
    if BOT_CONFIG.ai_provider != "openai":
        check_cloudflare_api_access(BOT_CONFIG.cloudflare)
    
    # Initialize AI agent based on configuration
    ai_agent = create_ai_agent(BOT_CONFIG)
    
    # Initialize Discord client
    chatbot_client = ChatBotClient(ai_agent=ai_agent)
    
    # Run the bot
    chatbot_client.run(BOT_CONFIG.discord.token, log_handler=None)


if __name__ == "__main__":
    main()
