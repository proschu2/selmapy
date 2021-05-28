import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from flask import Flask, request, jsonify
from selenium.webdriver.chrome.options import Options
import psycopg2
import os
from helpers import add_basics, selma, add_amounts, execute_query, get_connection
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    [amount, perc, change] = selma()
    return f"<b>Amount: {amount}; Change: {change}; Perc: {perc}</b>"


@app.route('/test', methods=['GET'])
def test():
    selma()
    connection = get_connection()
    previous = execute_query(
        connection, 'select change from selma order by id DESC limit 1', True)
    connection.close()
    return f"previous was {str(previous)}"


@app.route('/add', methods=['GET'])
def add():
    [amount, perc, change] = selma()
    resp = add_amounts(amount, perc, change)
    return app.response_class(**resp)


@app.route('/detailed', methods=['GET'])
def details():
    resp = add_basics()
    return app.response_class(**resp)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
