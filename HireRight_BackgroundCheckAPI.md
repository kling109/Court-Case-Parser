# Hire Right - Background Check API
Tristan Chilvers, Trevor Kling, Miles Milosevich, Matt Raymond
<br/><br/><br/>

## OVERVIEW
### Approach
Our approach was to keep it simple, simulate how a human would grab background data on a candidate. This required us to break the challenge into two main categories: **Navigation** and **Parsing**. 
<br/><br/>
Like a user, the program must recognize where the search bar is on the page and "click" key buttons that are necessary to reach the candidate's data. Since this program must also be flexible and applicable across many court sites, it must "walk through" the HTML tags, or text in the tags, to know where these key buttons are located in the website. This was possible through API's, such as Selenium and Regex, and allowed the program to function very similarily to a human user.
<br/><br/>
There were a couple initial approaches for parsing the data once we have found the candidate's background information (e.g., via HTML source code).

