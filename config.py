import os

from dotenv import load_dotenv

LOG_KEYWORDS = ["[UNBANNED]", "[COMMAND]", "[BAN]", "[WARNING]", "[KICK]", "[COLOR]"]
LOG_CHANNEL_ID = 1315700405430128730
LOG_FILE = '/factorio/logs/console.log'

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')