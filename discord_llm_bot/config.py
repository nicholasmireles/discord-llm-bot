import logging
import os
from typing import Dict, Any

import yaml
from .models import Config

ENV = os.getenv("ENV", "dev")
CONFIG: Dict[str, Any] = {}

logger = logging.getLogger(__name__)


def load_config() -> Config:
    """Load and validate configuration using Pydantic models."""
    global CONFIG

    # Load default config
    if os.path.exists("config/default.yaml"):
        logger.info("Loading config from default environment file.")
        with open("config/default.yaml") as f:
            CONFIG.update(yaml.load(f, Loader=yaml.FullLoader))

    # Load environment-specific config
    if os.path.exists(f"config/{ENV}.yaml"):
        logger.info(f"Loading config from {ENV} environment file.")
        with open(f"config/{ENV}.yaml") as f:
            CONFIG.update(yaml.load(f, Loader=yaml.FullLoader))

    # Add environment variables
    CONFIG["discord"] = CONFIG.get("discord", {})
    CONFIG["discord"]["token"] = os.getenv("DISCORD_TOKEN", "")

    CONFIG["agent"] = CONFIG.get("agent", {})
    CONFIG["agent"]["api_key"] = os.getenv("AGENT_API_KEY", "")

    # Validate and return Pydantic model
    return Config(**CONFIG)
