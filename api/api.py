from flask import Blueprint

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/')
def index():
    return "This is an example api app"