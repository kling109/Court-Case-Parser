#!/usr/bin/env python
# coding: utf-8
​
# <center> <h1> Python Web Navigation </center> </h1>
# <center> <h3> HireRite Grand Challege </center> </h3>
# <center> <h5> Matt Raymond </center> </h5>
​
# # Imports
​
# In[1]:
​
​
# Web driver for comtroling chrome
from selenium import webdriver
​
# Regex for parsing website navigation
import re as regx
​
# Thread sleeping
from time import sleep
​
# Import for dates
from datetime import datetime
​
# Import keys so we can press enter
from selenium.webdriver.common.keys import Keys
​
​
# # Browser
​
# In[2]:
​
​
# Sets of the path of the chrome driver
# ToDO: Fix the chrome driver path so it doesn't need to be set automatically inside python
__BROWSER__ = webdriver.Chrome(executable_path='/Users/matthewraymond/chromedriver')
​
# Set the implicit wait time so that webpages don't flip out when they can't fontrol things right away
__BROWSER__.implicitly_wait(5)
​
​
# # Global Testing Variables
​
# In[3]:
​
​
# The websites that we're supposed to use
__TESTINGWEBSITES__ = ["https://www.sccourts.org/casesearch/", # agreement says no crawlers
                       "https://wcca.wicourts.gov/case.html",
                       "https://www.oscn.net/dockets/search.aspx",
                       "https://www.civitekflorida.com/ocrs/county/", # recapcha
                       "https://apps.supremecourt.az.gov/publicaccess/caselookup.aspx", # captcha
                       "https://www.superiorcourt.maricopa.gov/docket/CriminalCourtCases/caseSearch.asp",
                       "http://justicecourts.maricopa.gov/FindACase/casehistory.aspx",
                       "https://casesearch.epcounty.com/PublicAccess/default.aspx"]
​
# the websites that are actually LEGAL to use
__LEGALWEBSITES__ = __TESTINGWEBSITES__[1:3] + __TESTINGWEBSITES__[-3:]
​
# Testing variables for name and date of birth
__TESTING_FNAME__ = "John"
__TESTING_LNAME__ = "Smith"
__TESTING_MNAME__ = "Herbert"
​
__TESTING_DOB__ = datetime(2001, 9, 11)
​
​
# In[4]:
​
​
# Removes one of the legal websites because there's extra navigation and I don't want to deal with that right now
__LEGALWEBSITES__ = __LEGALWEBSITES__[:-1]
​
​
# # Regex
​
# In[5]:
​
​
# Regex for different searches
__FIRSTNAME__ = "=\"[^\"]*[Ff][A-Za-z]*[Nn]ame[A-Za-z]*\""
__LASTNAME__ = "=\"[^\"]*[Ll][A-Za-z]*[Nn]ame[A-Za-z]*\""
__MIDDLENAME__ = "=\"[^\"]*[Mm][A-Za-z]*[Nn]ame[A-Za-z]*\""
__BIRTHDATE__ = "=\"[^\"]*?(?!\bre\b)(search)[^\"]*?\""
__DATEFORMAT__ = "[MD\d]{2}[./-][MD\d]{2}[./-][Y\d]{4}"
__REACTFORMAT__ = "\"[^\"]*?(react)[^\"]\"><\/div>"
__SEARCHBUTTON__ = "=\"[^\"]*?((?<!menu)(?<!re)(?<!box)search)[^\"]*?\""
​
​
# # Function Declaration
​
# ## Scraping Info from Webpage
​
# In[6]:
​
​
# Scrape the HTML source from a webpage
def getSource(strURL):
    __BROWSER__.get(strURL)
    print("Scraping website source code...")
    html = __BROWSER__.page_source
    
    # Makes sure that webpages that use react are fully loaded before starting
    while regx.search(__REACTFORMAT__, html, regx.IGNORECASE) is not None:
        sleep(1)
        html = __BROWSER__.page_source
          
    return html
​
# Search for the name of an element given a regex description
def regSearchName(ws, re):
    _result = regx.search("name" + re, ws, regx.IGNORECASE)
    if(_result is None):
        return "";
    else:
        return _result[0][6:-1]
​
# Search for the ID of an element given a regex description
def regSearchID(ws, re):
    _result = regx.search("id" + re, ws, regx.IGNORECASE)
    if(_result is None):
        return "";
    else:
        return _result[0][4:-1]
​
# Return a tuple of an elements ID and name given a regex description
def getIDandName(ws, re):
    return (regSearchID(ws, re), regSearchName(ws, re))
​
​
# ## Input Filling
​
# In[11]:
​
​
# Fills out the person's name
def fillOutName(html, fn, ln, mn):
    # Finds the ID and Name for first, middle, and last names
    fnID, fnName = getIDandName(html, __FIRSTNAME__)
    mnID, mnName = getIDandName(html, __MIDDLENAME__)
    lnID, lnName = getIDandName(html, __LASTNAME__)
​
    sendInput(fnName, fn)
    sendInput(mnName, mn)
    sendInput(lnName, ln)
​
# Send the input string (s) to the element (e) specified
def sendInput(e, s):
    try:
        # Breaks out if there's no element sent
        if str(e) is "":
            return
        
        # Find the element based on the name and send input
        item = __BROWSER__.find_element_by_name(e)
        item.click()
        item.clear()
        item.send_keys(s)
        
    except:
        print("Input failed. Attempted to enter \"{0}\" to \"{1}\" and failed.".format(s, e))
    
# Fill out the date of birth
# Returns a bool denoting whether it was successful or not
def fillOutDOB(html, dob):
    try:
        # If there is a dob sent
        if dob is not None:
            dID, dName = getIDandName(html, __BIRTHDATE__)
#             print("dID: {0} -- dName: {1}".format(dID, dName))
            # Sometimes need to send by id instead of name
            # ToDo: Create function to try both name and id and return the result
            if dName is not "":
                item = __BROWSER__.find_element_by_name(dName)
            else:
                item = __BROWSER__.find_element_by_id(dID)
            
            # If the item is locked then there's no poin in trying to edit it
            if not item.is_enabled():
                return False
            
            # Enter information
            item.click()
            item.clear()
            
            # Find the delimiter desired
            _delin = findDateFormat(html)
            
            # Create a date based on the american standard, using the specified delimiters
            _date = "{1}{0}{2}{0}{3}".format(_delin, str(dob.month).zfill(2), str(dob.day).zfill(2), dob.year)
            
            # Enter date
            item.send_keys(_date)
        return True
    
    except:
        print("Input failed. Attempted to enter \"{0}\" as a date and failed.".format(dob))
        return False
        
# Find the delimiters used in the example (if one exists) and returns them
def findDateFormat(html):
    # Find the example
    result = regx.search(__DATEFORMAT__, html, regx.IGNORECASE)
    
    # Return either the result or use a random one
    if result is not None:
        return result[0][2]
    else:
        return '-'
​
# Initialize the search
def search(html):
    # Find the id/name of the elemnts
    sID, sName = getIDandName(html, __SEARCHBUTTON__)
#     print("sID:{0}  - sName: {1}".format(sID, sName))
​
    # If there is a search button within a reasonable distance
    if sID is not "" or sName is not "":
        # Click the button
        item = __BROWSER__.find_element_by_name(sName)
        item.click()
        
    else:
        # Press enter to initialize the search
        __BROWSER__.switch_to.active_element.send_keys(Keys.ENTER)
    
# Function that fills out all of the information given
def fillOutInformation(html, fn, ln, mn = "", dob = None):
    # NOTE: You have to fill them out in this order or sometimes
    # the open date selector messes with the submission
    
    # Variable that checks whether the dob was filled out correctly
    dobFilled = fillOutDOB(html, dob)
    fillOutName(html, fn, ln, mn)
    
    print(dobFilled)
    # Sometimes the dob section is locked until you enter a name
    if not dobFilled:
        fillOutDOB(html, dob)
​
​
# # Testing
​
# In[8]:
​
​
# Variable that holds all of the website HTMLs so that I don't have to re-scraping it again and again
__WEBSITEHTML__ = []
​
# Scrape all
for site in __LEGALWEBSITES__:
    __WEBSITEHTML__.append(getSource(site))
​
​
# In[9]:
​
​
# Temp variable for the current website
# Only for debugging purposes
curSite = 3
​
​
# In[12]:
​
​
# The html for the site currently being operated on
html = __WEBSITEHTML__[curSite]
# The actual website being operated on
current = __LEGALWEBSITES__[curSite]
​
# Load the website
__BROWSER__.get(current)
​
# Testing information filling out
fillOutInformation(html, __TESTING_FNAME__, __TESTING_LNAME__, __TESTING_MNAME__, __TESTING_DOB__)
​
# NOTE: Currently being debugged
# search(html)
​
​
# In[391]:
​
​
# For debugging purposes
print(__WEBSITEHTML__[curSite])
​
​
# # ToDo
# - Finish setting up date input
# - Finish enabling search
# 
# # Completed
# - Input for f/m/l name
# - Massive regex overhaul
#     - Input dates (sort of broken though)
#     - Press enter (sort of broken)
​
# In[ ]:

