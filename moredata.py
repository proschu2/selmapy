# %%
import time
import os
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2
# %%
name_map = {
    'International companies': 'international', 'Swiss companies': 'swiss'
}


def get_category_name(x):
    if x in name_map.keys():
        return name_map[x]
    return x.lower().replace(' ', '_')

# %%


# %%
driver = webdriver.Chrome()
driver.set_window_position(0, 0)
driver.set_window_size(300, 768)
driver.get('https://selma.io/login')
e = driver.find_element(By.ID, 'user_email')
e.send_keys(os.environ['EMAIL'])
e = driver.find_element(By.ID, 'user_password')
e.send_keys(os.environ['PASSWORD'])
e = driver.find_element(By.NAME, 'commit')
e.send_keys(Keys.RETURN)
driver.get('https://www.selma.io/app/investment_portfolio')
data = {}
# stats
print('STATS')
planet_stats = WebDriverWait(driver, 3).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.my-planet-stats')))
amount = planet_stats.find_element_by_css_selector('div.stat-figure').text
amount = amount.replace('CHF', '').replace(
    "'", '').replace('’', '').replace(' ', '')
change = planet_stats.find_element(By.CSS_SELECTOR, 'span.change-figure').text
change = change.replace('+', '').replace('CHF',
                                         '').replace(' ', '').replace("'", '').replace('’', '')
perc = planet_stats.find_element(
    By.CSS_SELECTOR, 'span.change-figure.normal-weight').text
perc = perc.replace('+', '').replace('%', '').replace(' ', '')
stats = {
    'amount': amount, 'change': change, 'perc': perc
}
data['stats'] = stats
print(amount, change, perc)
# basic
print('BASIC')
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
    print(investment_type, card_sum, card_change, card_percentage, category)
'''
# detailed
print('DETAIL')
WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, 'div.selma-switch'))).click()
portfolio = WebDriverWait(driver, 3).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.show-for-small-only')))
cards = portfolio.find_elements_by_css_selector('div.portfolio-card')
for card in cards:
    investment_type = card.get_attribute('data-label')
    isin = card.get_attribute('data-isin')
    money_stuff = card.find_element(By.CSS_SELECTOR, 'div.card-caption')
    card_sum = money_stuff.find_element(
        By.CSS_SELECTOR, 'span.card-sum').text.replace('’', '').replace("'", '').replace(' ', '')
    if investment_type != 'Cash':
        card_change = money_stuff.find_element(
            By.CSS_SELECTOR, 'span.card-change').text.replace('(', '').replace('%)', '')
        text_stuff = card.find_element(By.CSS_SELECTOR, 'div.card-description')
        name = text_stuff.find_element(By.TAG_NAME, 'h3').text
        tags = text_stuff.find_element(By.CSS_SELECTOR, 'div.card-tags').text
        [shares, avg] = tags.split('\n')
        shares = shares.split(' ')[0]
        avg = avg.split(' ')[0].replace(
            '’', '').replace("'", '').replace(' ', '')
    else:
        card_change = name = shares = avg = None
    print(investment_type, isin, card_sum, card_change, name, shares, avg)
'''
time.sleep(5)
driver.quit()

# %%
def add_details():
    try:
        connection = psycopg2.connect(os.environ['DATABASE_URL'])
        cursor = connection.cursor()
        cursor.execute('select change from selma order by id DESC limit 1')
        previous = cursor.fetchone()[0]
        cursor.close()
        if float(previous) == float(change):
            print('no need to add as still the same change')
            response = app.response_class(
                response="No need to add: still the same",
                status=200,
                mimetype='application/json'
            )
            return response
        else:
            print(f'they are different: {previous} vs {change}')
            query = f'''INSERT INTO SELMA(date, amount, percentage, change) VALUES(now(), {int(amount)}, {float(perc)}, {float(change)});'''
            try:
                cursor2 = connection.cursor()
                cursor2.execute(query)
                connection.commit()
                cursor2.close()
                connection.close()
                return app.response_class(
                    response="New row added",
                    status=200,
                    mimetype='application/json'
                )
    except Exception as e:
        return app.response_class(
            response=f"Error: {e}",
            status=400,
            mimetype='application/json'
        )

