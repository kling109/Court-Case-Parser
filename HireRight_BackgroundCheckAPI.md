# Hire Right - Background Check API
Tristan Chilvers, Trevor Kling, Miles Milosevich, Matt Raymond
<br/><br/><br/>

## OVERVIEW
### Approach and Structure
Our approach was to keep it simple, simulate how a human would grab background data on a candidate. This required us to break the challenge into two main categories: **Navigation** and **Parsing**. 
<br/><br/>
To navigate like a user, the program must recognize where the search bar is on the page and "click" key buttons that are necessary to reach the candidate's data. Since this program must also be flexible and applicable across many court sites, it must "walk through" the HTML tags, or text in the tags, to know where these key buttons are located in the website. This was possible through API's such as Selenium and Regex. Once the candidate's page has been reached, it must "read" the information off of the page. To continue our approach for this program as a human simulation, we took screenshots of the webpage so that the program could understand the page like a human reader. Available OCR's allowed the program do such that, and resulted in the program functioning very similarily to that of a human.
<br/><br/>
There were a couple initial approaches for parsing the data once we have found the candidate's background information (e.g., via HTML source code). However, we decided that the best approach was to have screenshots taken of the page for the program to "read" through. OpenCV and Pytesseract OCR's were crucial in implementing this approach. Using them, the program can then box key words within the screenshot (e.g., Name, address, etc.) and, like a person, record the data that is within a reasonable range of the key word. This approach to record data based on the context of its location allows the program to be flexible across multiple web designs.
<br/><br/><br/>
### Constraints
program cant classify words correctly
There were a number of constraints our approach faced. Regarding navigation, not every website is similar in design. This results in a decent number of Regex formulas being implemented that will only function for a limited number of websites. Furthermore, websites with additional pages to pass through to reach the candidate's information may not work with our navigation process. This also applies towards websites with Captcha's.
