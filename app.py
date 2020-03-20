import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from flask import Flask, request, jsonify
from selenium.webdriver.chrome.options import Options
import psycopg2
import os
app = Flask(__name__)
GOOGLE_CHROME_PATH = os.environ['GOOGLE_CHROME_BIN'] if 'GOOGLE_CHROME_BIN' in os.environ else '/app/.apt/usr/bin/google-chrome'
CHROMEDRIVER_PATH = os.environ['CHROMEDRIVER_PATH'] if 'CHROMEDRIVER_PATH' in os.environ else '/app/.chromedriver/bin/chromedriver'


def selma():
    chrome_options = Options()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.binary_location = GOOGLE_CHROME_PATH
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)
    driver.get('https://selma.io/login')
    e = driver.find_element(By.ID, 'user_email')
    print(e)
    e.send_keys(os.environ['EMAIL'])
    e = driver.find_element(By.ID, 'user_password')
    print(e)
    e.send_keys(os.environ['PASSWORD'])
    e = driver.find_element(By.NAME, 'commit')
    e.send_keys(Keys.RETURN)
    time.sleep(5)
    e = driver.find_element(
        By.CSS_SELECTOR, 'div.active-investments > div.account-card-contents div.account-card-content-row-value')
    amount = e.text
    amount = amount.replace('CHF', '')
    amount = amount.replace("'", '')
    amount = amount.replace('’', '')
    amount = amount.replace(' ', '')
    #print(f'amount is {amount}')
    e = driver.find_element(By.CSS_SELECTOR, 'span.change-figure')
    change = e.text
    change = change.replace('+', '')
    change = change.replace('CHF', '')
    change = change.replace(' ', '')
    #print(f'change is {change}')
    e = driver.find_element(
        By.CSS_SELECTOR, 'span.change-figure.normal-weight')
    perc = e.text
    perc = perc.replace('+', '')
    perc = perc.replace('%', '')
    perc = perc.replace(' ', '')
    #print(f'perc is {perc}')
    driver.close()
    return [amount, perc, change]


@app.route('/', methods=['GET'])
def index():
    [amount, perc, change] = selma()
    return f"<b>Amount: {amount}; Change: {change}; Perc: {perc}</b>"


@app.route('/test', methods=['GET'])
def test():
    [amount, perc, change] = selma()
    connection = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = connection.cursor()
    cursor.execute('select change from selma order by id DESC limit 1')
    previous = cursor.fetchone()[0]

    # ", later is {amount}, {perc}, {change}"
    return f"previous was {str(previous)}"


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
