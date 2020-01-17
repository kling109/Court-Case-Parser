# Breaks the data received from the image recognition software into pieces,
# then processes it to produce a JSON of the relevant information.

import imagerecognition as ir
import re as regx
import nltk
import spacy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
nlp = spacy.load("en_core_web_sm")
import en_core_web_sm
nlp = en_core_web_sm.load()


def toMatrix(rawText):
    '''
    Breaks the raw, formatted text from the image recognition software
    down into a list of lists.

    Keyword Arguments:
    rawText (str): the raw text obtained from the image recognition.

    Returns:
    data (dict): The data, placed in a sensible dictionary. The keys are
      the locations and the values are the contained words.
    '''
    lines = regx.split(r'\n', rawText)
    data = {}
    for y in range(len(lines)):
        elements = regx.split(r'\s{2,}', lines[y])
        if elements[0] != "":
            for word in elements:
                x = lines[y].find(word)
                # When adding data, it may be preferred to rescale the axes
                # to add more weight to a specific kind of spacing.
                label = makeAssociation(word)
                data[(x, y)] = word.lower()
                print("At {}, {} is found with type {}.".format((x,y), word, label))
    return data

def makeAssociation(input):
    '''
    Makes a classification of an object using the spaCy Named Entity
    Recognition module.

    Keyword Arguments:
    input (str): The text to be classified.

    Returns:
    classif (string): The classification of the object.
    '''
    doc = [w.label_ for w in nlp(input).ents]
    classif = 'NONE'
    if len(doc) > 0:
        classif = max(set(doc), key = doc.count)
    return classif

def findIdentifier(iden, data):
    '''
    Searches through the document for the item which matches the identifier
    the best.

    Keyword Arguments:
    iden (str): The regex pattern of the identifier to search for.
    data (dict): The data dictionary with all text and their locations.

    Returns:
    similar (list(tuple(int, int))): The (x,y) coordinate pair of the matched text.
        There could potentially be multiple matches, so these are accounted for
        by producing a list.
    '''
    similar = []
    similarLimit = 0
    for loc, term in data.items():
        val = fuzz.ratio(iden, term)
        if val > similarLimit:
            similarLimit = val
            similar = [loc]
        elif val == similarLimit:
            similar.append(loc)
    return similar

def removeIdentifier(iden, text):
    '''
    Removes the identifier from a given piece of text.

    Keyword Arguments:
    iden (str): The regex pattern of the identifier to remove.
    text (str): The item to remove the identifier from.

    Returns:
    filtered (str): The remaining string.
    '''
    filtered = regx.sub(iden, '', text)
    return filtered

def getItem(data, iden, type):
    '''
    Gets the given identifier-value pair for a given identifier
    and dataset.

    Keyword Arguments:
    data (dict): The words found in the document, indexed by their location.
    iden (str): The keyword to search for and make an association to.
    '''
    loc = findIdentifier(, dat)
    print("Found Defendant keyword at {}".format(loc))
    excess = [removeIdentifier("defendant", dat[x]) for x in loc]
    print("After removing identifiers: {}".format(excess))
    if len(excess) > 0:
        label = makeAssociation(excess)

def getText(img):
    '''
    Driver method for the module.  Takes an input of the
    path to the image, then extracts all relevant information
    from the image.

    Keyword Arguments:
    img (str): The path to the image.
    '''
    # Starting with just parsing for the defendant name.
    rawText = ir.basicReading(img)
    print(rawText)
    dat = toMatrix(rawText)
    pair = getItem(dat, "defendant name")

if __name__ == "__main__":
    getText('HireRightImages/wisconsin_official.png')
