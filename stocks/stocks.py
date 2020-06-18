from flask import Blueprint

stocks_bp = Blueprint('stocks_bp', __name__)

@stocks_bp.route('/')
def index():
    return "This is an example stock app"