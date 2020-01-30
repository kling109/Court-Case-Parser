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
        #options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--auto-open-devtools-for-tabs')
        #options.add_argument("--kiosk")
        #options.add_argument('headless')

        return options

    def getSource(self,browser: webdriver.Chrome, strURL):
        browser.get(strURL)
        return browser.page_source

    def ClearSession(self):
        for path in self.CreatedScreenshots:
            if(not os.path.isfile(path)):
                continue
            os.remove(path)

    def CleanPage(self, driver: webdriver.Chrome):
        #driver.execute_script("console.log('nice!!');")
        numElements = driver.execute_script("return document.getElementsByTagName('*').length;")
        for i in range(0,numElements):
            """print(driver.execute_script('''
                    var i = {};
                    var all = document.getElementsByTagName('*');
                    function isFooter(node, int){{
                        console.log(''+int+' | '+node.nodeName);
                        if(node.nodeName=="FOOTER"||node.nodeName=="footer"||node.id=="footer"||(node.nodeType==1&&node.classList.contains("footer"))){{
                            return true;
                        }}
                        else if(node.parentNode!=null){{
                            return isFooter(node.parentNode,int+1);
                        }}
                        else{{
                            return false;
                        }}
                    }}
                    return ''+i+' | '+all[i].nodeName+' | '+all[i].id+' | '+all[i].classList+' | '+isFooter(all[i],0)+' | '+all.length;'''.format(i)))
            """
            driver.execute_script("""
                    /*function isFooter(node){{
                        if(node.nodeName=="FOOTER"||node.nodeName=="footer"||node.id=="footer"||(node.nodeType==1&&node.classList.contains("footer"))){{
                            return true;
                        }}
                        else if(node.parentNode!=null){{
                            return isFooter(node.parentNode);
                        }}
                        else{{
                            return false;
                        }}
                    }}*/
                    var allElements = document.getElementsByTagName("*");
                    var i = {};
                    //console.log(allElements[i].nodeName);
                    //if(!isFooter(allElements[i])){{
                        if(allElements[i].nodeName=="IMG")
                        {{
                            allElements[i].style.visibility = "gone";
                        }}
                        else if(allElements[i].textContent!="")
                        {{
                            allElements[i].style.background = "none";
                            allElements[i].style.color = "#000";
                        }}
                        else
                        {{
                            allElements[i].style.background = "none";
                            allElements[i].style.color = "#FFF";
                    //    }}
                    }}
            """.format(i))
            time.sleep(0.001)

    def Screenshot(self,driver: webdriver.Chrome, strURL = 'current') -> None:
        existingFiles = []
        for filename in os.listdir(self.ScreenshotLocation):
            path = os.path.join(self.ScreenshotLocation,filename)
            if(not os.path.isfile(path)):
                continue
            existingFiles.append(path)

        if(strURL != 'current'):
            driver.get(strURL)

        readyState = driver.execute_script('return document.readyState')
        while(readyState!='complete'):
            readyState = driver.execute_script('return document.readyState')
            time.sleep(0.05)
            
        if(platform.system() == 'Darwin'):
            #OpenDeveloper = Keys.ALT+Keys.COMMAND+"i"
            #OpenConsole = Keys.COMMAND+Keys.SHIFT+"p"
            #hotkey('alt', 'command', 'i')
            #time.sleep(1.5)
            hotkey('command', 'shift', 'p')

        elif(platform.system() == 'Windows' or platform.system() == 'Linux'):
            #OpenDeveloper = Keys.CTRL+Keys.SHIFT+"i"
            #OpenConsole = Keys.CTRL+Keys.SHIFT+"p"
            #hotkey('ctrl', 'shift', 'i')
            #time.sleep(1.5)
            hotkey('ctrl', 'shift', 'p')

        time.sleep(1)
        write("screenshot")
        time.sleep(0.1)
        press("down")
        time.sleep(0.1)
        press("enter")
        time.sleep(0.1)

        file = ''
        attempts = 0
        while(file == ''):
            for filename in os.listdir(self.ScreenshotLocation):
                path = os.path.join(self.ScreenshotLocation,filename)
                if(not os.path.isfile(path) or path in existingFiles):
                    continue
                file = path
            attempts += 1
            time.sleep(0.5)
            if(attempts>30):
                file = 'ERR'
                raise RuntimeError('Screenshot Timeout: No new files in directory. [{}]'.format(driver.current_url))
                return None

        if(file == 'ERR'):
            filefilter = driver.current_url.replace("https://","").strip()
            filefilter = filefilter.replace("http://","").strip()
            filefilter = filefilter.replace("www.","").strip()

            filefilter = filefilter.replace('?','_')
            filefilter = filefilter.replace('/','_')

            matchedfiles = []

            for filename in os.listdir(self.ScreenshotLocation):
                path = os.path.join(self.ScreenshotLocation,filename)
                if(not os.path.isfile(path)):
                    continue
                if(filefilter in filename):
                    matchedfiles.append(path)
            if(len(matchedfiles) == 0):
                raise RuntimeError('Screenshot not taken: No files matched. [filefilter: {}]'.format(filefilter))

            latest_file = max(matchedfiles, key=os.path.getctime) #uses glob

            now = time.time()
            oneminute_ago = now - 60
            if(os.path.getctime(latest_file) > oneminute_ago):
                self.CreatedScreenshots.append(latest_file)
                return latest_file
            else:
                raise RuntimeError('Screenshot not taken: No matched files are recent. [filefilter: {}, matchedfiles: {}]'.format(filefilter,matchedfiles))
                return None
        else:
            self.CreatedScreenshots.append(file)
            return file


def test1():
    base_url = 'https://www.w3schools.com/'#'https://www.oscn.net/dockets/GetCaseInformation.aspx?db=blaine&number=CV-2017-00046&cmid=15958'#'https://wcca.wicourts.gov/caseDetail.html?caseNo=2020SC000301&countyNo=40&index=0'

    si = ScreenImage()
    options = si.ConfigDriver(webdriver.ChromeOptions())
    driver = webdriver.Chrome(options=options, executable_path=r'/Users/i530455/chromedriver')
    driver.get(base_url)
    time.sleep(1.5)
    print(si.Screenshot(driver=driver))
    time.sleep(10)
    si.ClearSession()

def test2():
    base_url = 'https://stackoverflow.com/questions/10244280/selenium-tests-crash-randomly-while-executing-javascript'#'https://www.w3schools.com/'#'https://www.oscn.net/dockets/GetCaseInformation.aspx?db=blaine&number=CV-2017-00046&cmid=15958'#'https://wcca.wicourts.gov/caseDetail.html?caseNo=2020SC000301&countyNo=40&index=0'
    si = ScreenImage()
    options = si.ConfigDriver(webdriver.ChromeOptions())
    driver = webdriver.Chrome(options=options, executable_path=r'/Users/i530455/chromedriver')
    driver.get(base_url)
    time.sleep(3.5)
    si.CleanPage(driver=driver)


if __name__ == "__main__":
    test2()

    time.sleep(10)
    #print(getSource("https://wcca.wicourts.gov/case.html"))
