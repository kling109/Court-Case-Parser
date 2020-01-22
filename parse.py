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

TO_FIND = [("defendant name", ["PERSON", "ORG"], "defendant"),
           ("sex", ["NONE"], "defendant"),
           ("date of birth", ["DATE"], "defendant")]

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
                data[(x, 3*y)] = (word.lower(), label)
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
    doc = [w.label_ for w in nlp(str(input)).ents]
    classif = 'NONE'
    if len(doc) > 0:
        classif = max(set(doc), key = doc.count)
    return classif

def findIdentifier(data, iden):
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
        val = fuzz.ratio(iden, term[0])
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

def handleList(items, full):
    '''
    Handles potential lists.

    Keyword Arguments:
    items (list(tuple)): A list of locations of items to check for being lists.
    full (list(tuple)): A list of the locations of all potential list candidates.

    Returns:
    items (list(tuple)): An in-place modification of the original set of items.  If
        a list was found, the matched location will now be a list containing all the
        prescribed values.
    '''
    for i in range(len(items)):
        # A row of items should have a common x value
        if items[i][0][1] == items[i][1][1]:
            row = list(filter(lambda r : r[1] == items[i][1][1], full))
            if len(row) > 1:
                # The object may be a row list
                for x in range(len(row)-1):
                    if abs(row[x][0] - row[x+1][0]) > items[i][2]:
                        row = row[:x]
                        break
            if (len(row) > 1):
                items[i][1] = row
        # A column of items should have a common x value
        elif items[i][0][0] == items[i][1][0]:
            col = list(filter(lambda r : r[0] == items[i][1][0], full))
            if len(col) > 1:
                # The object may be a column list
                for y in range(len(col)-1):
                    if abs(col[y][1] - col[y+1][1]) > items[i][2]:
                        col = col[:y]
                        break
            if (len(col) > 1):
                items[i][1] = col
    return items


def getItem(data, iden, type, qualif = ""):
    '''
    Gets the given identifier-value pair for a given identifier
    and dataset.

    Keyword Arguments:
    data (dict): The words found in the document, indexed by their location.
    iden (str): The keyword to search for and make an association to.
    type (str): The expected classifications of the object.

    Returns:
    items (list(list(tuple(int, int), tuple(int, int), int))): The location of the identifier followed
        by the location of the value.  The separation distance then follows that.
    '''
    loc = findContext(data, qualif, iden)
    if loc == [(-1, -1)]:
        return [(-1, -1), (-1, -1), 0]
    print("Found {} keyword at {}".format(iden, loc))
    if (type != ["NONE"]):
        excess = [removeIdentifier(iden, data[x][0]) for x in loc]
        print("After removing identifiers: {}".format(excess))
        for x in excess:
            if len(x) > 0:
                label = makeAssociation(excess)
                if label == type:
                    return (loc, loc, 0)
    toCheck = list(filter(lambda r : data[r][1] in type, [k for k in data.keys()]))
    print(toCheck)
    itemLoc = [min(set(toCheck), key = lambda r : abs(c[0] - r[0]) + abs(c[1] - r[1])) for c in loc]
    items = []
    for i in range(len(loc)):
        items.append([loc[i], itemLoc[i], abs(loc[i][0] - itemLoc[i][0]) + abs(loc[i][1] - itemLoc[i][1])])
        print("Found item {} for identifier {} at {}, with a distance of {}".format(data[itemLoc[i]],
            data[loc[i]], itemLoc[i], abs(loc[i][0] - itemLoc[i][0]) + abs(loc[i][1] - itemLoc[i][1])))
    # Each proper identifier has been found a match.  Now, to determine if the values fall in a list
    items = handleList(items, toCheck)
    return items


def findContext(data, qualif, iden):
    '''
    For identifiers with multiple possible instances, we may want to
    find a contextual identifier.

    Keyword Arguments:
    data (dict): The words found in the document, indexed by their location.
    qualif (str): The qualifier the system wants to find
    iden (str): The identifier we want to find the correct context for

    Returns:
    loc (tuple(int, int)): The location of the correct identifier.
    '''
    qualifLoc = findIdentifier(data, qualif)
    idenLoc = findIdentifier(data, iden)
    print(qualifLoc)
    print(idenLoc)
    minDist = 50
    match = [(-1, -1)]
    for q in qualifLoc:
        for id in idenLoc:
            dist = abs(q[0] - id[0]) + abs(q[1] - id[1])
            if dist < minDist:
                minDist = dist
                match = [id]
            elif dist == minDist:
                match.append(id)
    return match

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
    for item in TO_FIND:
        pair = getItem(dat, item[0], item[1], item[2])

if __name__ == "__main__":
    #getText('HireRightImages/wisconsin_official.png')
    getText('HireRightImages/maricopa.png')
