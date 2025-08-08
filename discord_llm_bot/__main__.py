import logging
import os

from .client import ChatBotClient
from .lib.pydantic_ai_service import create_cloudflare_agent, create_openai_agent, check_cloudflare_api_access
from .config import BOT_CONFIG

# Set up logging
logging.basicConfig(level=getattr(logging, BOT_CONFIG.logging_level))


def main():
    # Initialize AI agent based on configuration
    if BOT_CONFIG.ai_provider == "openai" and BOT_CONFIG.openai:
        ai_agent = create_openai_agent(config=BOT_CONFIG.openai)
    else:
        # Default to Cloudflare
        # Check API access for Cloudflare
        check_cloudflare_api_access(BOT_CONFIG.cloudflare)
        ai_agent = create_cloudflare_agent(config=BOT_CONFIG.cloudflare)
    
    # Initialize Discord client
    chatbot_client = ChatBotClient(ai_agent=ai_agent)
    
    # Run the bot
    chatbot_client.run(BOT_CONFIG.discord.token, log_handler=None)


if __name__ == "__main__":
    main()
