from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time, random

url = 'https://replit.com/login?goto=/@mklin95/botdb'
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
page = driver.get(url)

while 1:
    try:
        Q = driver.find_element(By.CLASS_NAME, 'css-11iypm2')
        Q.click()
        # print("Element exists")

    except NoSuchElementException:
        ;
        
    r = 60
    time.sleep(r)