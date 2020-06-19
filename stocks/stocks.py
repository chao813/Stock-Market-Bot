import requests
import os
import json

from flask import Blueprint, request
from dotenv import load_dotenv

load_dotenv()

FINNHUB_TOKEN = os.getenv("FINNHUB_TOKEN")

STOCK_QUOTE_URL = "https://finnhub.io/api/v1/quote?token={token}&symbol={symbol}"

stocks_bp = Blueprint("stocks_bp", __name__)

@stocks_bp.route("/example")
def index():
    return "This is an example stock app"

def get_stock_quote(symbol):
    """
    Get real-time quote data for a stock given symbol
    """
    r = requests.get(STOCK_QUOTE_URL.format(token=FINNHUB_TOKEN, symbol=symbol))
    response = r.json()
    return response
    """{
        "c": 261.74,
        "h": 263.31,
        "l": 260.68,
        "o": 261.07,
        "pc": 259.45,
        "t": 1582641000 
    }"""


def calculate_percent_change(response, average_cost):
    """
    Calculate percent change in stock compared to average cost
    """
    current_price = response["c"]
    difference = current_price - average_cost
    percent_difference = round(difference / average_cost * 100, 2)
    return percent_difference


def trigger_alert(percent_difference, percent, increase, decrease):
    """
    Send alert if percent difference met
    """
    if abs(percent_difference) > percent:
        if increase and percent_difference > 0:
            return True, "Increase"
        if decrease and percent_difference < 0:
            return True, "Decrease"
    

#Cron will call a function in this file
#pull every single stock from db, run calculation of percent change, determine user increase/decrease for that stock then email alert?



