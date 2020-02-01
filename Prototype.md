# Background Check Documentation
Tristan Chilvers, Trevor Kling, Miles Milosevich, Matt Raymond
<br/><br/><br/><br/>

## OVERVIEW
### Approach and Structure
Our approach was to keep it simple, simulate how a human would grab background data on a candidate. This required us to break the challenge into two main categories: **Navigation** and **Parsing**. 
<br/><br/>
To navigate like a user, the program must recognize where the search bar is on the page and "click" key buttons that are necessary to reach the candidate's data. Since this program must also be flexible and applicable across many court sites, it must "walk through" the HTML tags, or text in the tags, to know where these key buttons are located in the website. This was possible through API's such as Selenium and Regex. Once the candidate's page has been reached, it must "read" the information off of the page. To continue our approach for this program as a human simulation, we took screenshots of the webpage so that the program could understand the page like a human reader. Available OCR's allowed the program do such that, and resulted in the program functioning very similarily to that of a human.
<br/><br/>
There were a couple initial approaches for parsing the data once we have found the candidate's background information (e.g., via HTML source code). However, we decided that the best approach was to have screenshots taken of the page for the program to "read" through. OpenCV and Pytesseract OCR's were crucial in implementing this approach. Using them, the program can then box key words within the screenshot (e.g., Name, address, etc.) and, like a person, record the data that is within a reasonable range of the key word. This approach to record data based on the context of its location allows the program to be flexible across multiple web designs.
<br/><br/>
### Constraints
There were a number of constraints our approach faced. Regarding navigation, not every website is similar in design. This results in a decent number of Regex formulas being implemented that will only function for a limited number of websites. Furthermore, websites with additional pages to pass through to reach the candidate's information may not work with our navigation process. This applies towards websites with Captcha's as well. Additionally, there are times when the program may not accurately classify a word correctly when looking at a page.
<br/><br/><br/><br/>

# Court Case Parser
## Navigation Component

## Web Page Formatting Component

## Text Parsing Component

### 1.  Introduction
The text parsing component of the court case parsing library consists of two pieces: the image recognition module and the data aquisition module.  The two components function in tandem, with a single call to the main driver method.  

#### 1.1 Basic Usage
To run the module, simply instantiate an instance of the parser with  
```python
p = parse()
```
, then call the function 
```python
p.parseData(path='path_to_image', county=[list_of_counties])
```
.  The `path` variable is given a path to the image of the court case, and the `county` variable is given a list of counties, as returned by the navigation component.

### 2. Image Recognition
The `imagerecognition.py` module provides the capacity for the program to recognize text in a given image.  While this module is primarily intended to be used within the `parse.py` module, it can none the less be used for standalone text recognition.
#### 2.1 Basic Usage
To use the image recognition module, call the function 
```python
basicReading(filename='path_to_image')
```
to extract text from the given image.  The program will then return a block of text; each entry of data takes the form of the following table:

| Index | Value              | | Description                         |
|-------|--------------------|-|-------------------------------------|
| 0     | level              | | Indicates the visual level on which the text is found. |
| 1     | page_num           | | The page on the document on which the given text appears. |
| 2     | block_num          | | The number of the general region of text in the document which contians the parsed string. |
| 3     | par_num            | | The number of the paragraph which contians the parsed string. |
| 4     | line_num           | | The number of the line which contians the parsed string. |
| 5     | word_num           | | The number of words seen in the document as of the parsed text. |
| 6     | left               | | The x-coordinate of the bounding box, measured from the top-left corner of the screen.                               |
| 7     | top                | | The y-coordinate of the bounding box, measured from the top-left corner of the screen. |
| 8     | width              | | The width of the bounding box containing the text element. |
| 9     | height             | | The height of the bounding box containing the text element. |
| 10    | conf               | | The program's certainty that it is correct. |
| 11    | text               | | The actual parsed string. |

The output of this function is a tab-separated value text.  The image recognition module also provides a method which converts this large string into a list of lists, maintaining the `block_num`, `word_num`, `left`, `top`, `width`, `height`, `conf`, and `text` fields.  This can be performed by calling
```python
list_of_values = buildText(filename='path_to_image')
```
#### 2.2 Implementation
This module makes use of OpenCV for the production of bounding boxes, and pyTesseract for optical character recognition.  The image is read in as an image file using the OpenCV python library `cv2`.  This image is then given to pyTesseract's `image_to_data` method, to return the parsed data as a tab separated value string.  For the pyTesseract method, the flags `-l eng -c preserve_interword_spaces=1` are used.  The first flag `-l eng` sets the expected language for identification of words to english.  The second flag `-c preserve_interword_spaces=1` instructs the pyTesseract method to account for whitespace when determining the `left` and `top` values for a string.  All of this data is returned in a 2-dimensional list format, to be used by the text parsing library.

#### 2.3 Dependencies
1. python 3
2. OpenCV
3. pyTesseract

#### 2.4 Future Improvements
* Re-training pyTesseract on exclusively court document images would likely improve recognition for those cases.
* Tesseract offers the ability to check for multiple languages; this may be helpful for finding names, which may have more in common with other languages than English.

### 3. Data Aquisition
The data aquisition module `parse.py` makes use of the list returned by the image recognition module to produce JSON files containing the relevant case information.
#### 3.1 Basic Usage
The module can be run on a given image using the command
```python
p.parseData(path='path_to_image', county=[list_of_counties])
```
Note that the county of the case must be provided in advance.  This module is primarily designed to take inputs from the navigation module, which does a better job of finding the county than the text parser.  The program then returns a python dictionary, with a variety of values from the case details.

The first entry in the dictionary is the `Filing Date`, which indicates on what date the court case was filed.  The dictionarr also contains the `Jurisdiction` and `Case Number` fields, which contain the county the case was found in and the number of the case respectively.

The dictionary contains a variety of sub-dictionaries for more complex objects.  The first of these is the `Defendant Name(s)` dictionary, which contains dictionaries containing to the `Birth Date`, `Sex`, and `Address` of each defendant indexed by their name.  There is also a subdictionary `Offense #` for each offense found in the document.  This includes values like `Offense Date`, `Arrest Date`, `Disposition Date`, `Jail Time`, `Prison Time`, `Probation Time`, and `Fines`.

#### 3.2 Implementation
The data aquisition module makes use of a variety of techniques to determine the respective values from a document.

The first important characteristic of the implementation is the use of a special Manhattan distance metric.  In a document like a court case that must simply list out values, we can be reasonably sure that the data will follow a rough key-value format; a keyword will tell the reader what the value is, then the associated bit of text will fill in the details.  The modified Manhattan distance metric only allows the user to move in cardinal directions when determining distances; up, down, left, or right.  In addition, this metric arbitrarily sets any object which appears more than 300 units above the starting point to the maximum distance.  This is done to ensure the parser finds the correct values for each keyword; it follows logically that the value for the keyword will be located either to the side or below the keyword, so the module prefers to find elements from those regions.

However, to use this method, the module first must find the keywords.  This is done by using fuzzy matching with representative keywords.  In the court documents, it is not necessarily guarenteed that a label for a value will have a specific string representation, so the module simply searches the document for the best match to a keyword, with a minimum certainty of 80 percent.  This partial matching is accomplished using three functions from the python module `fuzzywuzzy`: `ratio`, `partial_ratio`, and `token_sort_ratio`.  The `ratio` method is the strictest of the options, requiring values to fall in the same order as the expected term and be the same length.  The `partial_ratio` term allows for terms to be matched if they contain the whole expected term and more.  Finally, the `token_sort_ratio` allows values to be permuted; it sees no difference between "John Smith" and "Smith John".   The parser uses these methods to determine what it best believes to be the keywords for each field in the output JSON.

Once the keywords are established, the program moves on to filling the fields.  This is done by using natural language processing and expectation values.  For a kewyord containing "date", one would expect the value to take the form of a date.  Thus, the module uses spaCy's Named Entity Recognition to classify the type of text elements near the given keyword.  If the class matches the expected value, the program marks the given text element as a possibility.  Once all possibilities are found, the program selects the option with the lowest modified Manhattan distance from the keyword.  These key-value pairs are then added to the JSON file.

#### 3.3 Dependencies
1. python 3
2. imagerecognition.py
3. nltk
4. spaCy
5. Fuzzywuzzy

#### 3.4 Future Improvements
* The natural language processor often mis-identifies the objects it is given.  This could be improved by using reinforement learning along with the partially trained models offered by spaCy.
* The program would ideally be able to get data from fields like the `Offense Literal`, `Disposition Text`, and other long-form text.  To accomplish this, the model could include a natural language processor trained to identify legal text.  Subsequently, legal text objects could be assigned to the respective keywords using the usual Manhattan distance method.

## Data Serialization Component
