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

PARSEERRORS = ['rn)']

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
        text += str(v[0]) + " "
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
            if wordInfo[-1] not in PARSEERRORS:
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
    dist_l = x_0 - 20
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
    dist_r = x_0 + width + 20
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
    maxDist = 500
    for k in data.keys():
        dist = manhattan(k, idLoc)
        if k != idLoc and dist < maxDist:
            fullTerm = extendTerm(k, data).replace(data[idLoc][0], '').strip()
            fullType = makeAssociation(fullTerm)
            if fullType in expectedType and fullTerm not in seenTerms:
                seenTerms.append(fullTerm)
                matches.append(k)
    return [matches, seenTerms]


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
    maxDist = 500
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
    similarLimit = 80
    for loc, term in data.items():
        val = fuzz.ratio(itemName, term[0])
        if val > similarLimit:
            itemLocs.append(loc)
    return itemLocs

def matchItemStrict(itemName : str, data : dict):
    '''
    Finds all occurances of an existing known item in the document.
    '''
    itemLocs = []
    similarLimit = 90
    for loc, term in data.items():
        val = fuzz.token_sort_ratio(itemName, extendTerm(loc, data))
        if val > similarLimit:
            itemLocs.append(loc)
    return itemLocs


def getNames(idens : list, data : dict):
    '''
    Extracts names of individuals from the document based on their identifiers.

    Keyword Arguments:
    idens (list): The set of identifiers that one wishes to search for.  Includes
        both the literal identifiers and the contexts.
    data (dict): The data set to search.

    Returns:
    nameDict (dict): A dictionary of the names found, sorted by the keyword.
    '''
    nameDict = {}
    for id in idens:
        idMatch = checkContext(id[1], id[2], data)
        items = []
        locs = []
        for m in idMatch:
            termMatch = makeMatch(m, ["PERSON", "ORG", "NORP"], data)
            for i in range(len(termMatch[1])):
                if termMatch[1][i] not in items:
                    locs.append(termMatch[0][i])
                    items.append(termMatch[1][i])
        minDist = 500
        for match in idMatch:
            for it in locs:
                dist = manhattan(match, it)
                if dist < minDist:
                    minDist = dist
        for match in idMatch:
            for i in range(len(locs)):
                if manhattan(match, locs[i]) < minDist + 15:
                    if id[0] not in nameDict:
                        nameDict[id[0]] = [items[i]]
                    else:
                        nameDict[id[0]].append(items[i])
    return nameDict


def getDefendantInfo(data : dict):
    '''
    Finds all the defendants in the document, and returns them along with their
    relevant information: sex and date of birth.
    '''
    names = getNames([["Defendant Name(s)", ["defendant", "name", "defendant name"],["defendant"]]], data)
    dobLocs = findItem("date of birth", data)
    sKeyLocs = findItem("sex", data)
    nameList = names["Defendant Name(s)"]
    defendantDict = {}
    for n in nameList:
        defendantDict[n] = {}
        minDistDate = 500
        dateChoice = ""
        # Make this function choose the date of birth that is closest to the
        # name first
        for dob in dobLocs:
            dates = makeMatch(dob, ["DATE", "CARDINAL"], data)
            for d in range(len(dates[0])):
                dist = manhattan(dates[0][d], dob)
                if dist < minDistDate:
                    minDistDate = dist
                    dateChoice = dates[1][d]

    return defendantDict


def isList(keyword : str, expected : list, data : dict):
    '''
    Checks if the data is in a list.
    '''
    keywordLocs = findItem(keyword, data)
    for k in keywordLocs:
        # Find the elements below the keyword
        x_0 = k[0]
        y_0 = k[1]
        x_1 = k[0] + data[k][1]
        for item in data.keys():
            x_t = item[0]
            y_t = item[1]
            if x_t > x_0 - 15 and x_t < x_1 + 15 and y_t > y_0 and data[item][0] in expected:
                # Found a list
                return True
    return False


if __name__ == "__main__":
    data = getRawData("HireRightImages/wisconsin.png")
    grid = assembleData(data)
    if (isList("relationship", ["plaintiff", "defendant"], grid)):
        print(True)
    else:
        samplematch = checkContext(["defendant", "name", "defendant name"], ["defendant"], grid)
        print(samplematch)
        for m in samplematch:
            print(makeMatch(m, ["PERSON", "ORG", "NORP"], grid))
        # for key, val in grid.items():
        #     assoc = makeAssociation(val[0])
        #     print("Key: {} Word: {} NER: {}".format(key, val, assoc))
        print(getNames([["Defendant Name(s)", ["defendant", "name", "defendant name"],["defendant"]]], grid))
        # print(getFullText(grid))
        print(getDefendantInfo(grid))
        print(False)
