import logging

from .client import ChatBotClient
from .lib.agent import create_ai_agent
from .config import CONFIG

# Set up logging
logging.basicConfig(level=getattr(logging, CONFIG.logging_level))


def main():
    # Initialize AI agent based on configuration
    ai_agent = create_ai_agent(CONFIG.agent)

    # Initialize Discord client
    chatbot_client = ChatBotClient(ai_agent=ai_agent)

    # Run the bot
    chatbot_client.run(CONFIG.discord.token, log_handler=None)


if __name__ == "__main__":
    main()
