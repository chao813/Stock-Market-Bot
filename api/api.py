import requests
import os
import json

from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from stocks.stocks import get_stock_quote, calculate_percent_change

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
            "average cost": 6.00,
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


#@api_bp.route("/stocks/tracker", methods=["GET"])
#def get_tracked_stocks() show me all the ones im tracking, dont show percent diff
    #if no param included = show all, if param included then filter


#@api_bp.route("/stocks/tracker", methods=["GET"])
#def get_tracked_stocks_differences() show me all the ones im tracking, show percent diff
    #if no param included = show all, if param included then filter

    
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
    data = request.get_json()

    symbol = data["symbol"]
    average_cost = data["average cost"] 
    percent = data["percent"]
    increase = data["increase"]
    decrease = data["decrease"]
    
    #save to db code here
    return 
