from flask import Flask, jsonify
from apartment_checker import check_availability  # your function

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    count = check_availability()
    return jsonify({"available": count}), 200
