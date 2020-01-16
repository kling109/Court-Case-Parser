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
    custom_oem_psm_config = r'-l eng -c preserve_interword_spaces=1'
    text = pytesseract.image_to_string(img, config=custom_oem_psm_config)
    return text

if __name__ == "__main__":
    rawtext = basicReading('HireRightImages/wisconsin.png')
    print(rawtext)
