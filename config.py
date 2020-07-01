import os
import logging

from dotenv import load_dotenv

load_dotenv()

DEBUG = True
PATH = os.path.dirname(os.path.realpath(__file__))
DATABASE = PATH + "/stocks.db"
LOG_FILE_PATH = "/logs/stock_market_bot.log"
LOGGER_LEVEL = logging.DEBUG
