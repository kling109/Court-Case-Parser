# Test main file

# imports
from selenium import webdriver


# function that get's the html from a web url
def getSource(strURL):
    browser = webdriver.Chrome()
    browser.get(strURL)
    return browser.page_source

print(getSource("http://google.com"))
