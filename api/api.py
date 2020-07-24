import os
import json
import sqlite3 as sql
import config

from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from marshmallow import ValidationError
from stocks.stocks import get_stock_quote, calculate_percent_change, get_stock_name, insert_stock_tracker, get_tracked_stocks_details
from database.database import Database
from api.schema import StockDifferenceSchema, AddStocksSchema
from logger import configure_logger, get_logger_with_context

load_dotenv()
logger = configure_logger()

api_bp = Blueprint("api_bp", __name__)

@api_bp.route("/healthcheck")
def healthcheck():
    logger = get_logger_with_context("")
    logger.info("Health check status: OK")
    return jsonify({"status": "ok"}), 200


@api_bp.route("/stocks/difference", methods=["POST"])
def check_stock_difference():
    """
    POST request Body
        {
            "symbol": "F",
            "avg_purchase_cost": 5.00,
            "percent": 5,
        }
    """
    try:
        data = StockDifferenceSchema().load(request.get_json())
        symbol = data["symbol"].upper()
        avg_purchase_cost = float(data["avg_purchase_cost"])
        percent = data["percent"]

        response = get_stock_quote(symbol)
        if not response:
            return jsonify({"error": f"You entered an invalid stock symbol: {symbol}"}), 404
        percent_difference = calculate_percent_change(response, avg_purchase_cost)

        resp = jsonify({"status": "success", "data": {"symbol": symbol, 
                        "percent_difference": percent_difference}})
        resp.status_code = 200 
        logger = get_logger_with_context("")
        logger.info("Check Stock Difference - status: 200 OK, Symbol: {symbol}, Percent Difference: {percent_difference}".format(symbol=symbol, percent_difference=percent_difference))
        return resp
    except ValidationError as error:
        resp = jsonify({"error": error.messages}), 400
        logger = get_logger_with_context("")
        logger.info("Check Stock Difference - error: 400 Bad Request")
        return resp



@api_bp.route("/stocks/track", methods=["GET"])
def get_tracked_stocks(): 
    """
    Show me all the stocks im tracking, filter by params
    Params: symbol, detailed = True/False 
    If "detailed" = True, show percent difference and last modified date
    """
    symbol = request.args["symbol"].upper()
    detailed = request.args["detailed"]
    
    tracked_stocks_list = get_tracked_stocks_details(detailed, symbol)
    if not tracked_stocks_list:
        logger = get_logger_with_context("")
        logger.info("Get Tracked Stocks - error: 404 Not Found")
        return jsonify({}), 404

    resp = jsonify({"status": "success", "data": tracked_stocks_list})
    resp.status_code = 200 
    logger = get_logger_with_context("")
    logger.info("Get Tracked Stocks - status: 200 OK, Tracked Stocks: {tracked_stocks_list}".format(tracked_stocks_list=tracked_stocks_list))
    return resp

    
@api_bp.route("/stocks/tracker", methods=["POST"])
def store_new_stock():
    """
    POST request Body, list of stocks to store
        {
            "stocks": [
                {
                    "symbol": "SNAP",
                    "avg_purchase_cost": 1,
                    "percent": 5,
                    "increase": true,
                    "decrease": true
                },
                {
                    "symbol": "TWTR",
                    "avg_purchase_cost": 1,
                    "percent": 2,
                    "increase": false,
                    "decrease": false
                }
            ]
        }
    Save values to database
    """
    try:
        stock_list = AddStocksSchema().load(request.get_json())
        for stock in stock_list["stocks"]:
            symbol = stock["symbol"].upper()
            avg_purchase_cost = float(stock["avg_purchase_cost"])
            percent = stock["percent"]  
            increase = 1 if stock["increase"] else 0
            decrease = 1 if stock["decrease"] else 0

            name = get_stock_name(symbol)
            if not name:
                return jsonify({"error": f"You entered an invalid stock symbol: {symbol}"}), 404
            
            with Database(config.DATABASE) as db:
                db.execute("INSERT IGNORE INTO stock (symbol,name) VALUES (%s, %s)",(symbol, name))
                db.execute("SELECT id FROM stock WHERE symbol=%s AND name=%s", [symbol, name,])
                stock_id = db.fetchone()
            insert_stock_tracker(stock_id.get("id"), avg_purchase_cost, percent, increase, decrease)
                        
        resp = jsonify({"status": "success"})
        resp.status_code = 200
        return resp
    except ValidationError as error:
        resp = jsonify({"error": error.messages}), 400
        return resp
    