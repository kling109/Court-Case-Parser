# Breaks the data received from the image recognition software into pieces,
# then processes it to produce a JSON of the relevant information.

import imagerecognition as ir
import re as regx
import nltk
import spacy
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
                data[(x, y)] = word
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

if __name__ == "__main__":
    rawText = ir.basicReading('HireRightImages/wisconsin.png')
    print(rawText)
    toMatrix(rawText)
