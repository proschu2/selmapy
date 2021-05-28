import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from flask import Flask, request, jsonify
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2
from typing import List, Dict
import os

GOOGLE_CHROME_PATH = os.environ['GOOGLE_CHROME_BIN'] if 'GOOGLE_CHROME_BIN' in os.environ else '/app/.apt/usr/bin/google-chrome'
CHROMEDRIVER_PATH = os.environ['CHROMEDRIVER_PATH'] if 'CHROMEDRIVER_PATH' in os.environ else '/app/.chromedriver/bin/chromedriver'


def get_driver():
    if 'GOOGLE_CHROME_BIN' in os.environ:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.binary_location = GOOGLE_CHROME_PATH
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(
            CHROMEDRIVER_PATH, chrome_options=chrome_options)
    else:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(
            './chromedriver', chrome_options=chrome_options)
    driver.set_window_position(0, 0)
    driver.set_window_size(300, 768)
    return driver


def login(d):
    '''
    Log in selma.io
    @param d: driver
    '''
    d.get('https://selma.io/login')
    e = d.find_element(By.ID, 'user_email')
    e.send_keys(os.environ['EMAIL'])
    e = d.find_element(By.ID, 'user_password')
    e.send_keys(os.environ['PASSWORD'])
    e = d.find_element(By.NAME, 'commit')
    e.send_keys(Keys.RETURN)


def get_amounts(d, close: bool):
    '''
    Get the current amount, change, and change in percentage
    @param d: driver
    '''
    a = WebDriverWait(d, 3).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.active-investments > div.account-card-contents div.account-card-content-row-value')))
    amount = a.text.replace('CHF', '').replace(
        "'", '').replace('’', '').replace(' ', '')
    c = WebDriverWait(d, 3).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.change-figure')))
    change = c.text.replace(
        '+', '').replace('CHF', '').replace(' ', '').replace("'", '').replace('’', '')
    p = WebDriverWait(d, 3).until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR, 'span.change-figure.normal-weight')))
    perc = p.text.replace('+', '').replace('%', '').replace(' ', '')
    if close:
        d.close()
    return [amount, perc, change]


def selma():
    '''
    Return the minimal stats, used to add to the main table
    '''
    driver = get_driver()
    login(driver)
    time.sleep(5)
    return get_amounts(driver, True)


def get_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])


def execute_query(c, q: str, fetch: bool):
    '''
    Execute an SQL query in the DB
    @param c: connection
    @param q: query
    '''
    cursor = c.cursor()
    cursor.execute(q)
    if fetch:
        v = cursor.fetchone()[0]
        cursor.close()
        return v
    else:
        c.commit()


def add_amounts(a: str, c: str, p: str) -> Dict:
    '''
    Add the amounts to the selma table
    @param a: amount
    @param c: change
    @param p: percentage
    '''
    [amount, perc, change] = selma()
    try:
        connection = get_connection()
        previous = execute_query(
            connection, 'select change from selma order by id DESC limit 1', True)
        if float(previous) == float(change):
            return {'response': 'no need to add: still the same', 'status': 200}
        else:
            query = f'''INSERT INTO SELMA(date, amount, percentage, change) VALUES(now(), {int(amount)}, {float(perc)}, {float(change)});'''
            try:
                execute_query(c, query, False)
                connection.close()
                return {'response': "New row added", 'status': 200}
            except Exception as e:
                return {'response': f"Error: {e}", 'status': 400}
    except Exception as e:
        return {'response': f"Connection issues: {e}", 'status': 401}


name_map = {
    'International companies': 'international', 'Swiss companies': 'swiss'
}


def get_category_name(x):
    if x in name_map.keys():
        return name_map[x]
    return x.lower().replace(' ', '_')


def get_basics():
    driver = get_driver()
    login(driver)
    [amount, perc, change] = get_amounts(driver)
    driver.get('https://www.selma.io/app/investment_portfolio')
    data = {}
    stats = {
        'amount': amount, 'change': change, 'perc': perc
    }
    data['stats'] = stats
    portfolio = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.show-for-small-only')))
    cards = portfolio.find_elements_by_css_selector('div.portfolio-card')
    for card in cards:
        tmp_d = {}
        investment_type = card.get_attribute('data-label')
        category = get_category_name(investment_type)
        money_stuff = card.find_element(By.CSS_SELECTOR, 'div.card-caption')
        card_sum = money_stuff.find_element(
            By.CSS_SELECTOR, 'span.card-sum').text.replace('’', '').replace("'", '').replace(' ', '')
        tmp_d['amount'] = card_sum
        card_percentage = card.find_element(
            By.CSS_SELECTOR, 'div > div.chart-bar > div.chart-bar-number').text.replace('%', '')
        tmp_d['percentage'] = card_percentage
        try:
            card_change = money_stuff.find_element(
                By.CSS_SELECTOR, 'span.card-change').text.replace('(', '').replace('%)', '')
            tmp_d['change'] = card_change
        except:
            card_change = None

        data[category] = tmp_d
    return data


def add_basics():
    data = get_basics()
    try:
        connection = get_connection()
        previous = execute_query(
            connection, 'select change from basic order by id DESC limit 1', True)
        if float(previous) == float(data['stats']['change']):
            return {'response': 'no need to add: still the same', 'status': 200}
        q_ = 'international_percentage, international_amount, international_change, swiss_percentage, swiss_amount, swiss_change, private_equity_percentage, private_equity_amount, private_equity_change, company_loans_percentage, company_loans_amount, company_loans_change, country_loans_percentage, country_loans_amount, country_loans_change, real_estate_percentage, real_estate_amount, real_estate_change, precious_metals_percentage, precious_metals_amount, precious_metals_change, cash_percentage, cash_amount'
        ins = []
        q_fin = []
        for el in q_.split(', '):
            f = el.split('_')
            i, j = '_'.join(f[:-1]), f[-1]
            if (i in data.keys()):
                val = data[i][j]
                ins.append(val)
                q_fin.append(el)
        q_fin += ['date', 'amount', 'change', 'perc']
        ins += ['now()', data['stats']['amount'], data['stats']
                ['change'], data['stats']['perc']]
        query = f'''INSERT INTO basic({','.join(q_fin)}) VALUES({','.join(ins)});'''
        execute_query(connection, query, False)
        return {'response': 'Basic details were added', 'status': 200}
    except Exception as e:
        return {'response': f"Error: {e}", 'status': 400}
