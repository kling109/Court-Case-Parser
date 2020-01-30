# File parsing module for the HireRight Challenge.
# Uses the OpenCV and PyTesseract modules to parse
# information from an image of the web page.

import cv2
import pytesseract
from imutils.object_detection import non_max_suppression

def basicReading(filename : str):
    '''
    Reads in text from an image file.

    Keyword Arguments:
    filename (string): the path to the intended image

    Returns:
    text (string): A block of raw text from the image.
    '''
    img = cv2.imread(filename)
    print(filename)
    custom_oem_psm_config = r'-l eng -c preserve_interword_spaces=1'
    text = pytesseract.image_to_data(img, config=custom_oem_psm_config)
    return text

def buildText(filename: str):
    '''
    Gets text from an image, then formats the data into useable fassion.

    Keyword Arguments:
    filename (str): the path to the image to query text from.
    '''
    rawtext = basicReading(filename)
    doc = []
    processedText = rawtext.split('\n')
    for line in processedText:
        curr = line.split('\t')
        # print([curr[2]] + curr[4:])
        doc.append([curr[2]] + curr[4:])
    return doc[1:]

if __name__ == "__main__":
    buildText('HireRightImages/wisconsin_official.png')
