import os
from dotenv import load_dotenv
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = "!"
STARTERS = ["i", "you", "he", "she", "it", "the", "a", "this", "that", "they"]
