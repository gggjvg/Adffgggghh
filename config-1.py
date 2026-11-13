import os
from dotenv import load_dotenv

# Loads a local .env file if present. Railway Variables also work.
load_dotenv()

PREFIX = os.getenv("COMMAND_PREFIX", "!")
OWNER_IDS = {
    value.strip()
    for value in os.getenv("OWNER_IDS", "").split(",")
    if value.strip()
}
