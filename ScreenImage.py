# Test main file
import os
import platform
import glob
from selenium import webdriver
from pyautogui import press, typewrite, hotkey, write
import time


class ScreenImage:
    ScreenshotLocation = os.getcwd()+'/Screenshots/'
    CreatedScreenshots = []

    def __init__(self,sc_location = 'default'):
        if(sc_location != 'default'):
            ScreenshotLocation = sc_location

    def ConfigDriver(self,options: webdriver.ChromeOptions):
        if(not os.path.isdir(self.ScreenshotLocation)):
            os.mkdir(self.ScreenshotLocation)
        #options = driver.ChromeOptions()

        # ToDO: this line doesnt seem to work
        options.add_experimental_option("prefs",{'download.default_directory': self.ScreenshotLocation+'/',"directory_upgrade": True})
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return options

    def getSource(self,browser: webdriver.Chrome, strURL):

        browser.get(strURL)
        return browser.page_source

    def ClearSession(self):
        for path in self.CreatedScreenshots:
            if(not os.path.isfile(path)):
                continue
            os.remove(path)

    def Screenshot(self, driver: webdriver.Chrome, strURL = 'current') -> None:
        if(strURL != 'current'):
            driver.get(strURL)
        if(platform.system() == 'Darwin'):
            #OpenDeveloper = Keys.ALT+Keys.COMMAND+"i"
            #OpenConsole = Keys.COMMAND+Keys.SHIFT+"p"
            hotkey('option', 'command', 'i')
            time.sleep(1.5)
            hotkey('command', 'shift', 'p')

        elif(platform.system() == 'Windows' or platform.system() == 'Linux'):
            #OpenDeveloper = Keys.CTRL+Keys.SHIFT+"i"
            #OpenConsole = Keys.CTRL+Keys.SHIFT+"p"
            hotkey('ctrl', 'shift', 'i')
            time.sleep(1.5)
            hotkey('ctrl', 'shift', 'p')

        time.sleep(1.5)
        write("screenshot")
        time.sleep(0.1)
        press("down")
        time.sleep(0.1)
        press("enter")
        time.sleep(0.1)

        filefilter = driver.current_url.replace("https://","").strip()
        filefilter = filefilter.replace("www.","").strip()
        filefilter = filefilter.replace('?','_')
        filefilter = filefilter.replace('/','_')

        #print(filefilter)
        time.sleep(2.0)

        matchedfiles = []

        for filename in os.listdir(self.ScreenshotLocation):
            path = os.path.join(self.ScreenshotLocation,filename)
            if(not os.path.isfile(path)):
                continue
            if(filefilter in filename):
                matchedfiles.append(path)
        latest_file = max(matchedfiles, key=os.path.getctime) #uses glob

        now = time.time()
        oneminute_ago = now - 60
        if(os.path.getctime(latest_file) > oneminute_ago):
            self.CreatedScreenshots.append(latest_file)
            return latest_file
        else:
            raise RuntimeError('Screenshot not taken.')
            return None



if __name__ == "__main__":
    #ChromeOptions.addArguments("--kiosk");
    #options.add_argument('headless')
    #options.add_argument('--auto-open-devtools-for-tabs')

    base_url = 'https://wcca.wicourts.gov/caseDetail.html?caseNo=2020SC000301&countyNo=40&index=0'

    si = ScreenImage()

    options = si.ConfigDriver(webdriver.ChromeOptions())
    driver = webdriver.Chrome(options=options, executable_path=r'/Users/i530455/chromedriver')
    driver.get(base_url)
    time.sleep(1.5)
    print(si.Screenshot(driver=driver))
    #print(getSource("https://wcca.wicourts.gov/case.html"))
