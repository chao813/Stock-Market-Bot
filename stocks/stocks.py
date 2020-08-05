import requests
import os
import json
import config
import datetime

from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from database.database import Database
from api.adapters import TimeoutHTTPAdapter, retries

load_dotenv()

FINNHUB_TOKEN = os.getenv("FINNHUB_TOKEN")

STOCK_QUOTE_URL = "https://finnhub.io/api/v1/quote?token={token}&symbol={symbol}"
STOCK_PROFILE_URL = "https://finnhub.io/api/v1/stock/profile2?token={token}&symbol={symbol}"
STOCK_NEWS_URL = "https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={token}"

http = requests.Session()
http.mount("https://", TimeoutHTTPAdapter(max_retries=retries))

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
    r = http.get(STOCK_QUOTE_URL.format(token=FINNHUB_TOKEN, symbol=symbol))
    response = r.json()
    return response


def get_stock_name(symbol):
    """
    Make sure symbol is trackable
    """
    r = http.get(STOCK_PROFILE_URL.format(token=FINNHUB_TOKEN, symbol=symbol))
    response = r.json()
    return response.get("name")


def get_stock_related_news(symbol, from_date, to_date):
    """
    Get company news for a given stock symbol
    response = [
        {
        "category": News category.,
        "datetime": Published time in UNIX timestamp.,
        "headline": News headline,
        "id": News ID,
        "image": Thumbnail image URL,
        "related": Related stocks and companies mentioned in the article,
        "source": News source,
        "summary": News summary,
        "url": URL of the original article
        }
    ] 
    """
    r = http.get(STOCK_NEWS_URL.format(token=FINNHUB_TOKEN, symbol=symbol, from_date=from_date, to_date=to_date))
    response = r.json()
    return response


def calculate_percent_change(response, avg_purchase_cost):
    """
    Calculate percent change in stock compared to average cost
    """
    current_price = response["c"]
    difference = current_price - avg_purchase_cost
    percent_difference = round(difference / avg_purchase_cost * 100, 2)
    return percent_difference
    

def insert_stock_tracker(stock_id, avg_purchase_cost, percent, increase, decrease):
    """
    Insert tracked stock average cost, percent, increase, decrease into database
    """
    with Database(config.DATABASE) as db:
        db.execute("REPLACE INTO stock_tracker (avg_purchase_cost, percent, increase, decrease, stock_id) VALUES(%s,%s,%s,%s,%s)", (avg_purchase_cost, percent, increase, decrease, stock_id))


def get_list_of_tracked_stocks(symbol):
    with Database(config.DATABASE) as db:
        if symbol:
            db.execute("SELECT * FROM stock_tracker JOIN stock ON stock.id = stock_tracker.stock_id WHERE stock.symbol=%s", [symbol]) 
            tracked_stocks = [db.fetchone()]
        else:
            db.execute("SELECT * FROM stock_tracker")
            tracked_stocks = db.fetchall()
    
    return tracked_stocks


def construct_tracked_stocks_news(tracked_stocks, detailed, from_date, to_date):
    if any(stock is None for stock in tracked_stocks):
        return 

    tracked_stocks_news_list = []
    for stock_details in tracked_stocks:
        with Database(config.DATABASE) as db:
            db.execute("SELECT symbol, name FROM stock WHERE id=%s", [stock_details.get("stock_id")]) 
            stock_profile = db.fetchone()

        symbol = stock_profile.get("symbol")
        name = stock_profile.get("name")
        
        stock_related_news = get_stock_related_news(symbol, from_date, to_date)
        specific_stock_news = []
        for news in stock_related_news:
            current_news_dict = {"headline": news.get("headline"), "url": news.get("url")}
        
            if detailed:
                current_news_dict["datetime"] = datetime.datetime.fromtimestamp(int(news.get("datetime")).strftime('%Y-%m-%d %H:%M:%S')
                current_news_dict["source"] = news.get("source")
                current_news_dict["summary"] = news.get("summary")
                current_news_dict["related"] = news.get("related")
            specific_stock_news.append(current_news_dict)

        tracked_stock_news_dict = {"symbol": symbol, "name": name, "news_articles": specific_stock_news}
        tracked_stocks_news_list.append(tracked_stock_news_dict)

    return tracked_stocks_news_list


def construct_tracked_stocks_response(tracked_stocks, detailed):
    if any(stock is None for stock in tracked_stocks):
        return 

    tracked_stocks_list = []
    for stock_details in tracked_stocks:
        with Database(config.DATABASE) as db:
            db.execute("SELECT symbol, name FROM stock WHERE id=%s", [stock_details.get("stock_id")]) 
            stock_profile = db.fetchone()

        symbol = stock_profile.get("symbol")
        name = stock_profile.get("name")
        avg_purchase_cost = stock_details.get("avg_purchase_cost")
        percent = stock_details.get("percent")
        increase = bool(stock_details.get("increase"))
        decrease = bool(stock_details.get("decrease"))
        last_modified = stock_details.get("last_modified")

        response = get_stock_quote(symbol)
        tracked_stock_dict = {"symbol": symbol, "name": name}
        
        if detailed:
            percent_difference = calculate_percent_change(response, avg_purchase_cost)
            tracked_stock_dict["percent_difference"] = percent_difference
            tracked_stock_dict["last_modified"] = last_modified
            tracked_stock_dict["alert_on_increase"] = increase
            tracked_stock_dict["alert_on_decrease"] = decrease
            tracked_stock_dict["avg_purchase_cost"] = avg_purchase_cost
            tracked_stock_dict["percent_to_track_threshold"] = percent

        tracked_stocks_list.append(tracked_stock_dict)

    return tracked_stocks_list


def get_tracked_stocks_details(detailed, symbol=None):
    tracked_stocks = get_list_of_tracked_stocks(symbol)
    tracked_stocks_response = construct_tracked_stocks_response(tracked_stocks, detailed)
    return tracked_stocks_response

def get_tracked_stocks_news_details(detailed, symbol=None, from_date, to_date):
    tracked_stocks = get_list_of_tracked_stocks(symbol)
    tracked_stocks_list_news = construct_tracked_stocks_news(tracked_stocks, detailed, from_date, to_date)
    return tracked_stocks_news_response


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
        if stock_detail.get("alert_on_increase"):
            if stock_detail.get("percent_difference") >= stock_detail.get("percent_to_track_threshold") and stock_detail.get("percent_difference") > 0:
                stocks_increased.append({"symbol": stock_detail.get("symbol"), "name": stock_detail.get("name"), "percent_increase": stock_detail.get("percent_difference")})
        if stock_detail.get("alert_on_decrease"):
            if abs(stock_detail.get("percent_difference")) >= stock_detail.get("percent_to_track_threshold") and stock_detail.get("percent_difference") < 0:
                stocks_decreased.append({"symbol": stock_detail.get("symbol"), "name": stock_detail.get("name"), "percent_decrease": stock_detail.get("percent_difference")})

    return trigger_alert(stocks_increased, stocks_decreased)