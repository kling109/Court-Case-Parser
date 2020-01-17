# ScreenImage.py
a class to simplify taking full page screenshots from within chrome driver using selenium.

## what works:
* takes screenshot on mac

## what might not work:
* taking screenshot on windows or linux
* try it tho

## use:
### simple:
```python
si = ScreenImage() #instantiate new screenimage
driver = webdriver.Chrome(options=si.ConfigDriver(webdriver.ChromeOptions()))
driver.get(base_url)
driver.nav.to.page.for.screenshot()
time.sleep(1.5) #ensure page is loaded
screenshot_path = si.Screenshot(driver=driver) #take screenshot
```

### customize chrome options:
```python
options = si.ConfigDriver(webdriver.ChromeOptions())
options.add_argument('no_girls_allowed')
options.add_argument('except_for_matt')
driver = webdriver.Chrome(options=options)
```

## future:
* function to clean website elements before screenshot for use in ocr applications
