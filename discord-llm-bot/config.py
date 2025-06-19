import logging
import os

import yaml

ENV = os.getenv("ENV", "dev")
CONFIG = {}

logger = logging.getLogger(__name__)
if os.path.exists(f"config/{ENV}.yaml"):
    logger.info("Loading config from {ENV} environment file.")
    with open(f"config/{ENV}.yaml") as f:
        CONFIG = yaml.load(f, Loader=yaml.FullLoader)

if os.path.exists("config/default.yaml"):
    logger.info("Loading config from default environment file.")
    with open("config/default.yaml") as f:
        CONFIG.update(yaml.load(f, Loader=yaml.FullLoader))
