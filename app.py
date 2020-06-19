from flask import Flask
from stocks.stocks import stocks_bp
from api.api import api_bp


app = Flask(__name__)
app.config.from_object("config")
app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(stocks_bp, url_prefix="/stocks")

@app.route("/")
def index():
    return "This is an example app"



if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"])