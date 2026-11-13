import os
PREFIX = os.getenv("COMMAND_PREFIX", "!")
OWNER_IDS = {x.strip() for x in os.getenv("OWNER_IDS", "").split(",") if x.strip()}
