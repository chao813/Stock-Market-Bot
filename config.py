import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = True
PATH = os.path.dirname(os.path.realpath(__file__))
DATABASE = PATH + "/stocks.db"


