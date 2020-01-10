# File parsing module for the HireRight Challenge.
# Uses the OpenCV and PyTesseract modules to parse
# information from an image of the web page.

import cv2
import pytesseract

def basicReading(filename : str):
    '''
    Reads in text from an image file.

    Keyword Arguments:
    filename (string): the path to the intended image

    Returns:
    text (string): A block of raw text from the image.
    '''
    img = cv2.imread(filename)
    text = pytesseract.image_to_string(img)
    return text

def textParsing(rawtext : str):
    '''
    Handles parsing out elements from the raw text received.

    Keyword Arguments:
    rawtext (string): a raw block of text obtained from the image

    Returns:
    info (dict): returns a dictionary of values, with key of the field name
                 and value of the given value.
    '''
    

if __name__ == "__main__":
    rawtext = basicReading('johnJohnTestCaseParties.png')
    textParsing(rawtext);
