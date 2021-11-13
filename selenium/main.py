#!usr/bin/python


from selenium import webdriver
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH = "".join([BASE_DIR, '/chromedriver'])
driver = webdriver.Firefox(PATH)

driver.get("http://damilareagba.com")
