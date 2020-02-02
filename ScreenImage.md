# ScreenImage.py
a class to simplify taking full page screenshots from within chrome driver using selenium, along with webpage preprocessing for improved OCR performance

## use:
```python
si = ScreenImage() #instantiate new screenimage
driver = webdriver.Chrome(options=si.ConfigDriver(webdriver.ChromeOptions()))
driver.get(base_url)
driver.nav.to.page.for.screenshot()
time.sleep(1.5) #ensure page is loaded
si.CleanPage(driver=driver) #remove background elements 
screenshot_path = si.Screenshot(driver=driver) #take screenshot
...
si.ClearSession() #delete all screenshots
driver.quit()
```

### customize chrome options:
```python
options = si.ConfigDriver(webdriver.ChromeOptions())
options.add_argument('no_girls_allowed')
options.add_argument('except_for_matt')
driver = webdriver.Chrome(options=options)
```
