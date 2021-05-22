# %%
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# %%
driver = webdriver.Chrome()
driver.set_window_position(0, 0)
driver.set_window_size(300, 768)
driver.get('https://selma.io/login')
e = driver.find_element(By.ID, 'user_email')
print(e)
e.send_keys(os.environ['EMAIL'])
e = driver.find_element(By.ID, 'user_password')
print(e)
e.send_keys(os.environ['PASSWORD'])
e = driver.find_element(By.NAME, 'commit')
e.send_keys(Keys.RETURN)
driver.get('https://www.selma.io/app/investment_portfolio')
# basic
print('BASIC')
portfolio = WebDriverWait(driver, 3).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.show-for-small-only')))
cards = portfolio.find_elements_by_css_selector('div.portfolio-card')
for card in cards:
    investment_type = card.get_attribute('data-label')
    isin = card.get_attribute('data-isin')
    money_stuff = card.find_element(By.CSS_SELECTOR, 'div.card-caption')
    card_sum = money_stuff.find_element(
        By.CSS_SELECTOR, 'span.card-sum').text.replace('’', '').replace("'", '').replace(' ', '')

    try:
        card_change = money_stuff.find_element(
            By.CSS_SELECTOR, 'span.card-change').text.replace('(', '').replace('%)', '')
    except:
        card_change = None
    print(investment_type, card_sum, card_change)
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

    try:
        card_change = money_stuff.find_element(
            By.CSS_SELECTOR, 'span.card-change').text.replace('(', '').replace('%)', '')
    except:
        card_change = None
    text_stuff = card.find_element(By.CSS_SELECTOR, 'div.card-description')
    try:
        name = text_stuff.find_element(By.TAG_NAME, 'h3').text
    except:
        name = None
    try:
        tags = text_stuff.find_element(By.CSS_SELECTOR, 'div.card-tags').text
        [shares, avg] = tags.split('\n')
        shares = shares.split(' ')[0]
        avg = avg.split(' ')[0].replace(
            '’', '').replace("'", '').replace(' ', '')
    except:
        shares = None
        avg = None
    print(investment_type, isin, card_sum, card_change, name, shares, avg)
time.sleep(5)
driver.quit()
