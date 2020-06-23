import requests
import os
import json
import sqlite3 as sql
import config

from flask import Blueprint, request
from dotenv import load_dotenv


load_dotenv()

FINNHUB_TOKEN = os.getenv("FINNHUB_TOKEN")

STOCK_QUOTE_URL = "https://finnhub.io/api/v1/quote?token={token}&symbol={symbol}"
STOCK_PROFILE_URL = "https://finnhub.io/api/v1/stock/profile2?token={token}&symbol={symbol}"

stocks_bp = Blueprint("stocks_bp", __name__)

@stocks_bp.route("/example")
def index():
    return "This is an example stock app"

def get_stock_quote(symbol):
    """
    Get real-time quote data for a given stock symbol
    response = {
        "c": 261.74,
        "h": 263.31,
        "l": 260.68,
        "o": 261.07,
        "pc": 259.45,
        "t": 1582641000 
    }
    """
    r = requests.get(STOCK_QUOTE_URL.format(token=FINNHUB_TOKEN, symbol=symbol))
    response = r.json()
    return response


def get_stock_name(symbol):
    """
    Make sure symbol is trackable
    """
    r = requests.get(STOCK_PROFILE_URL.format(token=FINNHUB_TOKEN, symbol=symbol))
    response = r.json()
    if response: 
        return response.get("name")
    return 



def calculate_percent_change(response, average_cost):
    """
    Calculate percent change in stock compared to average cost
    """
    current_price = response["c"]
    difference = current_price - average_cost
    percent_difference = round(difference / average_cost * 100, 2)
    return percent_difference
    

def insert_stock_tracker(stock_id, average_cost, percent, increase, decrease):
    """
    Insert tracked stock average cost, percent, increase, decrease into database
    """
    con = sql.connect(config.DATABASE) 
    cur = con.cursor()
    
    cur.execute("SELECT id FROM stock_tracker WHERE stock_id=?", [stock_id]) 
    if cur.fetchone():
        cur.execute("DELETE FROM stock_tracker WHERE stock_id=?", [stock_id])
        con.commit()
    cur.execute("INSERT INTO stock_tracker (average_cost, percent, increase, decrease, stock_id) VALUES(?,?,?,?,?)", (average_cost, percent, increase, decrease, stock_id))
    con.commit()


def get_tracked_stocks_details(detailed, symbol=None):
    con = sql.connect(config.DATABASE) 
    cur = con.cursor()
        
    if symbol:
        cur.execute("SELECT * FROM stock_tracker JOIN stock ON (stock.id = stock_tracker.stock_id) WHERE stock.symbol=?", [symbol]) 
        tracked_stocks = [cur.fetchone()]
    else:
        cur.execute("SELECT * FROM stock_tracker")
        tracked_stocks = cur.fetchall()

    if any(stock is None for stock in tracked_stocks):
        return 

    tracked_stocks_list = []
    for stock_details in tracked_stocks:
        cur.execute("SELECT symbol, name FROM stock WHERE id=?", [stock_details[6]]) 
        stock_profile = cur.fetchone()
        symbol = stock_profile[0]
        name = stock_profile[1]
        average_cost = stock_details[1]
        percent = stock_details[2]
        increase = bool(stock_details[3])
        decrease = bool(stock_details[4])
        last_modified = stock_details[5]

        if detailed:
            response = get_stock_quote(symbol)
            if not response:
                return jsonify({"error": f"You are tracking an invalid stock symbol: {symbol}"}), 404        
            percent_difference = calculate_percent_change(response, average_cost)
            tracked_stocks_list.append({"symbol": symbol, "name": name, "percent_difference": percent_difference,
                                        "last_modified": last_modified, "alert_on_increase": increase, 
                                        "alert_on_decrease": decrease, "average_cost": average_cost, 
                                        "percent_to_track_threshold": percent})
        else:
            tracked_stocks_list.append({"symbol": symbol, "name": name})

    return tracked_stocks_list


def trigger_alert(stocks_increased, stocks_decreased):
    """
    Trigger alert given tracked stocks that increased or decreased
    """
    increase_alert_message = ""
    decrease_alert_message = ""

    if stocks_increased:    
        increase_alert_message = "Stocks increased: \n"
        for stock in stocks_increased:
            increase_alert_message = (increase_alert_message + 
                                    "[{symbol}]{name} went up {emoji}{percent_increase}% \n".format(
                                    symbol=stock.get("symbol"), name=stock.get("name"), emoji=u'\u2191', 
                                    percent_increase=str(stock.get("percent_increase"))))

    if stocks_decreased:
        decrease_alert_message = "Stocks decreased: \n"
        for stock in stocks_decreased:
            decrease_alert_message = (decrease_alert_message + 
                                    "[{symbol}]{name} went down {emoji}{percent_increase}% \n".format(
                                    symbol=stock.get("symbol"), name=stock.get("name"), emoji=u'\u2193', 
                                    percent_increase=str(stock.get("percent_decrease"))))
    
    return increase_alert_message + "\n" + decrease_alert_message 


def get_tracked_stocks():
    """
    Run calculation of percent change for each tracked stock
    Trigger alert if increase or decrease is enabled and percent threshold is met
    Cron will call this function
    """
    tracked_stocks_list = get_tracked_stocks_details(detailed=True)
    
    stocks_increased = []
    stocks_decreased = []
    for stock_detail in tracked_stocks_list:
        if stock_detail.get("alert_on_increase") and stock_detail.get("percent_difference") >= stock_detail.get("percent_to_track_threshold") and stock_detail.get("percent_difference") > 0:
            stocks_increased.append({"symbol": stock_detail.get("symbol"), "name": stock_detail.get("name"), "percent_increase": stock_detail.get("percent_difference")})
        if stock_detail.get("alert_on_decrease") and abs(stock_detail.get("percent_difference")) >= stock_detail.get("percent_to_track_threshold") and stock_detail.get("percent_difference") < 0:
            stocks_decreased.append({"symbol": stock_detail.get("symbol"), "name": stock_detail.get("name"), "percent_decrease": stock_detail.get("percent_difference")})

    return trigger_alert(stocks_increased, stocks_decreased)