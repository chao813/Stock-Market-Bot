import requests
import os
import json
import sqlite3 as sql
import config

from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from stocks.stocks import get_stock_quote, calculate_percent_change, validate_stock_symbol, insert_stock_tracker, filter_tracked_stocks_details

load_dotenv()

api_bp = Blueprint("api_bp", __name__)

@api_bp.route("/")
def index():
    return "This is an example api app"


@api_bp.route("/stocks/difference", methods=["POST"])
def check_stock_difference():
    """
    POST request Body
        {
            "symbol": "F",
            "average cost": 5.00,
            "percent": 5,
        }
    """
    data = request.get_json()

    symbol = data["symbol"]
    average_cost = data["average cost"] 
    percent = data["percent"]

    response = get_stock_quote(symbol)
    if not response:
        return jsonify({}), 404
    percent_difference = calculate_percent_change(response, average_cost)

    resp = jsonify({"status": "success", "data": {"symbol": symbol, "percent_difference": percent_difference}})
    resp.status_code = 200 
    return resp


@api_bp.route("/stocks/tracked", methods=["GET"])
def get_tracked_stocks(): 
    """
    Show me all the stocks im tracking, filter by params
    Params: symbol, detailed = True/False 
    If "detailed" = True, show percent difference and last modified date
    """
    symbol = request.args['symbol']
    detailed = request.args['detailed']
    
    tracked_stocks_list = filter_tracked_stocks_details(symbol, detailed)
    if not tracked_stocks_list:
        return jsonify({}), 404

    resp = jsonify({"status": "success", "data": tracked_stocks_list})
    resp.status_code = 200 
    return resp

    
@api_bp.route("/stocks/tracker", methods=["POST"])
def post_data_save_db():
    """
    POST request Body
        {
            "symbol": "F",
            "average cost": 6.00,
            "percent": 5,
            "increase": false,
            "decrease": true
        }
    Save values to database
    """
    if request.method == 'POST':
        data = request.get_json()

        symbol = data["symbol"]
        average_cost = data["average cost"] 
        percent = data["percent"]  
        increase = 1 if data["increase"] else 0
        decrease = 1 if data["decrease"] else 0

        name = validate_stock_symbol(symbol)
        if not name:
            return jsonify({"Error": "You entered an invalid stock symbol: {symbol}".format(symbol=symbol)}), 404
        
        with sql.connect(config.DATABASE) as con: 
            cur = con.cursor()
            cur.execute("INSERT OR IGNORE INTO stock (symbol,name) VALUES (?,?)",(symbol, name))
            con.commit()
            cur.execute("SELECT id FROM stock WHERE symbol=? AND name=?", [symbol, name,])
            stock_id = cur.fetchone()[0]
            insert_stock_tracker(stock_id, average_cost, percent, increase, decrease)
            
            resp = jsonify({"status": "success"})
            resp.status_code = 200
            return resp
            con.close()


    