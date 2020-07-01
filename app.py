from flask import Flask, jsonify
from api.api import api_bp


app = Flask(__name__)
app.config.from_object("config")
app.register_blueprint(api_bp, url_prefix="/api")

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'Not Found',}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'Internal Server Error',}), 500

@app.route("/")
def index():
    return "This is an example app"



if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"])