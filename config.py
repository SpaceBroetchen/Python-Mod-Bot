import os
import sys

from dotenv import load_dotenv


LOG_KEYWORDS = ["[UNBANNED]", "[COMMAND]", "[BAN]", "[WARNING]", "[KICK]", "[COLOR]"]
LOG_CHANNEL_ID = 1315700405430128730
LOG_FILE = '/factorio/logs/console.log'

FACTORIO_DATA = "path to the data directory of factorio, used to generate bp images"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
