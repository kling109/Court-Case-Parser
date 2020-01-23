# Breaks the data received from the image recognition software into pieces,
# then processes it to produce a JSON of the relevant information.

import imagerecognition as ir
import re as regx
import nltk
import spacy
import pyap
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
nlp = spacy.load("en_core_web_sm")
import en_core_web_sm
nlp = en_core_web_sm.load()

def manhattan(t1 : tuple, t2 : tuple):
    '''
    Computes the Manhattan distance between two
    x-y coordinate pairs.

    Keyword Arguments:
    t1 (tuple): the first point
    t2 (tuple): the second point

    Returns:
    d (int): the distance
    '''
    d = abs(t1[0] - t2[0]) + abs(t1[1] - t2[1])
    return d


def getRawData(imagePath : str):
    '''
    Gets the raw text from an image given its location.

    Keyword Arguments:
    imagePath (str): the path to the image, starting from the directory
        running the python script.

    Returns:
    rawData (str): the total set of information from the image.
    '''
    rawData = ir.buildText(imagePath)
    return rawData


def getFullText(data : dict):
    '''
    Obtains the full text of the document as a single string, with all values
    separated by spaces.

    Keyword Arguments:
    data (dict): The processed data grid.  The keys are the locations
        in the grid, while the values are the words contained there.
    '''
    text = ""
    for v in data.values():
        text += str(v) + " "
    return text


def assembleData(rawData : list):
    '''
    Constructs the data given by the image recognition
    function into a dictionary, where the location is the
    key and the word is the value

    Keyword Arguments:
    rawData (list): The data, as given by the image recognition.
        The data comes in as a list of lists, where each entry in
        the outer list corresponds to a word, with a variety of
        information encoded.  Specifically, this method makes use
        of the location and text values.

    Returns:
    data (dict): The words in the document, indexed by their
        locations.
    '''
    data = {}
    for wordInfo in rawData:
        if len(wordInfo[-1]) > 0 and not (wordInfo[-1].isspace()):
            x = int(wordInfo[3])
            y = int(wordInfo[4])
            data[(x, 5*y)] = (wordInfo[-1].lower(), int(wordInfo[-4]))
    return data

def makeAssociation(input : str):
    '''
    Makes a classification of an object using the spaCy Named Entity
    Recognition module.

    Keyword Arguments:
    input (str): The text to be classified.

    Returns:
    classif (string): The classification of the object.
    '''
    doc = [w.label_ for w in nlp(str(input)).ents]
    classif = 'NONE'
    if len(doc) > 0:
        classif = max(set(doc), key = doc.count)
    return classif


def extendTerm(loc : tuple, data : dict):
    '''
    Uses spacial concerns to determine if a given location can have other
    components attached to it.
    '''
    result = extendTermLeft(loc, data) + " " +  data[loc][0] + " " + extendTermRight(loc, data)
    return result

def extendTermLeft(loc : tuple, data : dict):
    '''
    Uses spacial concerns to determine if a given location can have other
    components attached to it.  Helper method for extendTerm.
    '''
    width = data[loc][1]
    x_0 = loc[0]
    y_0 = loc[1]
    dist_l = x_0 - 15
    result = ""
    for k in data.keys():
        if k[1] > y_0 - 15 and k[1] < y_0 + 15 and k[0] + data[k][1] > dist_l and k[0] < x_0:
            result =  extendTermLeft(k, data) + " " + data[k][0]
            break
    return result

def extendTermRight(loc : tuple, data : dict):
    '''
    Uses spacial concerns to determine if a given location can have other
    components attached to it.  Helper method for extendTerm.
    '''
    width = data[loc][1]
    x_0 = loc[0]
    y_0 = loc[1]
    dist_r = x_0 + width + 15
    result = ""
    for k in data.keys():
        if k[1] > y_0 - 15 and k[1] < y_0 + 15 and k[0] < dist_r and k[0] > x_0:
            result = data[k][0] + " " + extendTermRight(k, data)
            break
    return result


def makeMatch(idLoc : tuple, expectedType : list, data : dict):
    '''
    Matches a given identifier to an item near it which satisfies its given
    expected type.

    Keyword Arguments:
    idLoc (tuple): The location of the identfier in the text.
    expectedType (list): The expected Named Entity Recognition value for a
        value to fill the identifier.
    data (dict): The processed data grid.  The keys are the locations
        in the grid, while the values are the words contained there.

    Returns:
    matches (list): A list of all best-matching pairs.
    seenTerms (list): The set of satisfactory values
    '''
    matches = []
    seenTerms = []
    maxDist = 450
    for k in data.keys():
        dist = manhattan(k, idLoc)
        if k != idLoc and dist < maxDist+50:
            fullTerm = extendTerm(k, data).replace(data[idLoc][0], '').strip()
            fullType = makeAssociation(fullTerm)
            if fullType in expectedType and fullTerm not in seenTerms:
                seenTerms.append(fullTerm)
                maxDist = dist
    return seenTerms


def checkContext(idNames : list, expectedContx : list, data : dict):
    '''
    Looks through the grid to find the contextual relation between a
    overarching type (such as a "defendant") and a keyword (such as "name").

    Keyword Arguments:
    idNames (list): A list of the possible identifier names.
    expectedContx (list): A list of the possible context names.
    data (dict): data (dict): The processed data grid.  The keys are the locations
        in the grid, while the values are the words contained there.

    Returns:
    matchingContx (list): A reduced list of identifier locations which match the
        expected context.
    '''
    matchingContx = []
    maxDist = 300
    for id in idNames:
        for cont in expectedContx:
            contxLocs = findItem(cont, data)
            idLocs = findItem(id, data)
            for c in contxLocs:
                for i in idLocs:
                    if manhattan(c, i) < maxDist and i not in matchingContx:
                        matchingContx.append(i)
    return matchingContx


def findItem(itemName : str, data : dict):
    '''
    Finds a verbatim item in the grid based on its fuzzy matching
    ratio.  Returns all instances with a sufficent matching percentage.

    Keyword Arguments:
    itemName (str): The text to search for.
    data (dict): The processed data grid.  The keys are the locations
        in the grid, while the values are the words contained there.

    Returns:
    itemLocs (list): A list of the sufficiently matching locations.
    '''
    itemLocs = []
    similarLimit = 50
    for loc, term in data.items():
        val = fuzz.ratio(itemName, term[0])
        if val > similarLimit:
            itemLocs.append(loc)
    return itemLocs


def getNames(idens : list, data : dict):
    '''
    Extracts names of individuals from the document based on their identifiers.

    Keyword Arguments:
    idNames (list): The set of identifiers that one wishes to search for.  Includes
        both the literal identifiers and the contexts.
    data (dict): The data set to search.

    Returns:
    nameDict (dict): A dictionary of the names found, sorted by the keyword.
    '''
    nameDict = {}
    for id in idens:
        idMatch = checkContext(id[1], id[2], data)
        items = []
        bestFit = 500
        for m in idMatch:
            termMatch = makeMatch(m, ["PERSON", "ORG", "NORP"], data)
            for i in range(len(termMatch)):
                if termMatch[i] not in items:
                    items.append(termMatch[i])
            nameDict[id[0]] = items
    return nameDict


if __name__ == "__main__":
    data = getRawData("HireRightImages/maricopa.png")
    grid = assembleData(data)
    samplematch = checkContext(["defendant", "name", "defendant name"], ["defendant"], grid)
    print(samplematch)
    for m in samplematch:
        print(makeMatch(m, ["PERSON", "ORG", "NORP"], grid))
    # for key, val in grid.items():
    #     assoc = makeAssociation(val[0])
    #     print("Key: {} Word: {} NER: {}".format(key, val, assoc))
    print(getNames([["Defendant Name(s)", ["defendant", "name", "defendant name"],["defendant"]]], grid))
