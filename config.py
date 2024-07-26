import os

import aiohttp
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv(".env")

        self.API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
        self.ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID")

