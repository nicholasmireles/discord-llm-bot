import logging
import os

from .client import ChatBotClient
from .lib.cloudflare import CloudFlareWorker
from .config import CONFIG

logging.basicConfig(level=CONFIG["logging_level"])


def main():
    cloudflare_worker = CloudFlareWorker(
        token=os.environ["CLOUDFLARE_TOKEN"], **CONFIG["cloudflare"]
    )
    cloudflare_worker.check_api_access()

    chatbot_client = ChatBotClient(cloudflare_worker=cloudflare_worker)
    chatbot_client.run(os.getenv("DISCORD_TOKEN"), log_handler=None)


if __name__ == "__main__":
    main()
