import time
#from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

#options = webdriver.ChromeOptions()
#options.binary_location = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
#chrome_driver_binary = r"C:/Users/Tristan\ Chilvers/Documents/Chapman/3rd\ Year/Interterm/MachineLearning/HireRight-Challenge"
#driver = webdriver.Chrome(executable_path=r'C:\\Users\\Tristan Chilvers\\AppData\\Local\\Programs\\Python\\Python37-32\\chromedriver.exe')  # Optional argument, if not specified will search path.
#driver = webdriver.Chrome(executable_path=r'C:\Users\Tristan Chilvers\Documents\Chapman\3rd Year\Interterm\MachineLearning\HireRight-Challenge\chromedriver.exe')
driver = webdriver.Chrome('./chromedriver.exe')
driver.get('http://www.google.com/');
time.sleep(5) # Let the user actually see something!
search_box = driver.find_element_by_name('q')
search_box.send_keys('ChromeDriver')
search_box.submit()
time.sleep(5) # Let the user actually see something!
driver.quit()
