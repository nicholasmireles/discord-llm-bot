import logging

from .client import ChatBotClient
from .lib.agent import create_ai_agent
from .lib.utils import check_cloudflare_api_access
from .config import CONFIG

# Set up logging
logging.basicConfig(level=getattr(logging, CONFIG.logging_level))


def main():
    # Check API access for Cloudflare if using it
    if CONFIG.agent.ai_provider == "cloudflare":
        check_cloudflare_api_access(CONFIG.agent)

    # Initialize AI agent based on configuration
    ai_agent = create_ai_agent(CONFIG.agent)

    # Initialize Discord client
    chatbot_client = ChatBotClient(ai_agent=ai_agent)

    # Run the bot
    chatbot_client.run(CONFIG.discord.token, log_handler=None)


if __name__ == "__main__":
    main()
