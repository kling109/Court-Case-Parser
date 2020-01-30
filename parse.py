# Breaks the data received from the image recognition software into pieces,
# then processes it to produce a JSON of the relevant information.

import imagerecognition as ir
import re as regx
import nltk
import spacy
import pyap
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import en_core_web_sm


class ImageParsing:
    PARSEERRORS = ['rn)']
    nlp = spacy.load("en_core_web_sm")
    nlp = en_core_web_sm.load()

    def __init__(self):
        pass


    def manhattan(self, t1 : tuple, t2 : tuple):
        '''
        Computes the Manhattan distance between two
        x-y coordinate pairs.

        Keyword Arguments:
        t1 (tuple): the first point
        t2 (tuple): the second point

        Returns:
        d (int): the distance
        '''
        if t1[1] - 200 < t2[1]:
            d = abs(t1[0] - t2[0]) + abs(t1[1] - t2[1])
        else:
            d = 10000
        return d


    def getRawData(self, imagePath : str):
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


    def getFullText(self, data : dict):
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


    def assembleData(self, rawData : list):
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
                if wordInfo[-1] not in self.PARSEERRORS:
                    x = int(wordInfo[3])
                    y = int(wordInfo[4])
                    data[(x, 5*y)] = (wordInfo[-1].lower(), int(wordInfo[-4]))
        return data

    def makeAssociation(self, input : str):
        '''
        Makes a classification of an object using the spaCy Named Entity
        Recognition module.

        Keyword Arguments:
        input (str): The text to be classified.

        Returns:
        classif (string): The classification of the object.
        '''
        doc = [w.label_ for w in self.nlp(str(input)).ents]
        classif = 'NONE'
        if len(doc) > 0:
            classif = max(set(doc), key = doc.count)
        return classif


    def extendTerm(self, loc : tuple, data : dict):
        '''
        Uses spacial concerns to determine if a given location can have other
        components attached to it.

        Keyword Arguments:
        loc (tuple): The location of the element to extend.
        data (dict): The set of data to search.

        Returns:
        result (str): The extended term.
        '''
        result = self.extendTermLeft(loc, data) + " " +  data[loc][0] + " " + self.extendTermRight(loc, data)
        return result

    def extendTermLeft(self, loc : tuple, data : dict):
        '''
        Uses spacial concerns to determine if a given location can have other
        components attached to it.  Helper method for extendTerm.

        Keyword Arguments:
        loc (tuple): The location of the element to extend.
        data (dict): The set of data to search.

        Returns:
        result (str): The extended term.
        '''
        width = data[loc][1]
        x_0 = loc[0]
        y_0 = loc[1]
        dist_l = x_0 - 20
        result = ""
        for k in data.keys():
            if k[1] > y_0 - 15 and k[1] < y_0 + 15 and k[0] + data[k][1] > dist_l and k[0] < x_0:
                result =  self.extendTermLeft(k, data) + " " + data[k][0]
                break
        return result

    def extendTermRight(self, loc : tuple, data : dict):
        '''
        Uses spacial concerns to determine if a given location can have other
        components attached to it.  Helper method for extendTerm.

        Keyword Arguments:
        loc (tuple): The location of the element to extend.
        data (dict): The set of data to search.

        Returns:
        result (str): The extended term.
        '''
        width = data[loc][1]
        x_0 = loc[0]
        y_0 = loc[1]
        dist_r = x_0 + width + 20
        result = ""
        for k in data.keys():
            if k[1] > y_0 - 15 and k[1] < y_0 + 15 and k[0] < dist_r and k[0] > x_0:
                result = data[k][0] + " " + self.extendTermRight(k, data)
                break
        return result


    def makeMatch(self, idLoc : tuple, expectedType : list, data : dict):
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
        maxDist = 1000
        for k in data.keys():
            dist = self.manhattan(idLoc, k)
            if k != idLoc and dist < maxDist:
                fullTerm = self.extendTerm(k, data).replace(data[idLoc][0], '').strip().replace(':,;', "")
                fullType = self.makeAssociation(fullTerm)
                nums = regx.split(r'[^\d]', data[k][0])
                nums = [n for n in nums if n]
                if fullType in expectedType and fullTerm not in seenTerms:
                    seenTerms.append(fullTerm)
                    matches.append(k)
                elif "LOC" in expectedType and fullType == "DATE" and len(nums) > 0 and len(nums[-1]) == 5:
                    seenTerms.append(fullTerm)
                    matches.append(k)
                elif expectedType == ["CASENO"]:
                    if len(nums) > 0 and len(nums[-1]) >= 4:
                        seenTerms.append(fullTerm)
                        matches.append(k)
        return [matches, seenTerms]


    def checkContext(self, idNames : list, expectedContx : list, data : dict):
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
                contxLocs = self.findItem(cont, data)
                idLocs = self.findItem(id, data)
                for c in contxLocs:
                    for i in idLocs:
                        if self.manhattan(c, i) < maxDist and i not in matchingContx:
                            matchingContx.append(i)
        return matchingContx


    def findItem(self, itemName : str, data : dict):
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

    def matchItemStrict(self, itemName : str, data : dict):
        '''
        Finds all occurances of an existing known item in the document.

        Keyword Arguments:
        itemName (str): The item to search for.
        data (dict): The data set to search.

        Returns:
        itemLocs (list): A list of locations where the item appears.
        '''
        itemLocs = []
        similarLimit = 90
        for loc, term in data.items():
            val = fuzz.token_sort_ratio(itemName, self.extendTerm(loc, data).replace(':,;', ""))
            if val > similarLimit:
                itemLocs.append(loc)
        toRemove = []
        for i1 in range(len(itemLocs)):
            for i2 in range(len(itemLocs))[i1+1:]:
                if (itemLocs[i1][0] + data[itemLocs[i1]][1] + 20 > itemLocs[i2][0] and
                    itemLocs[i1][1] - 15 < itemLocs[i2][1] and
                    itemLocs[i1][1] + 15 > itemLocs[i2][1] and
                    itemLocs[i2] not in toRemove):
                    toRemove.append(itemLocs[i2])
        for r in toRemove:
            itemLocs.remove(r)
        return itemLocs


    def getNames(self, idens : list, data : dict):
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
            idMatch = self.checkContext(id[1], id[2], data)
            items = []
            locs = []
            for m in idMatch:
                termMatch = self.makeMatch(m, ["PERSON", "ORG", "NORP"], data)
                for i in range(len(termMatch[1])):
                    if termMatch[1][i] not in items:
                        locs.append(termMatch[0][i])
                        items.append(termMatch[1][i])
            minDist = 1000
            for match in idMatch:
                for it in locs:
                    dist = self.manhattan(match, it)
                    if dist < minDist:
                        minDist = dist
            for match in idMatch:
                for i in range(len(locs)):
                    if self.manhattan(match, locs[i]) < minDist + 15:
                        if id[0] not in nameDict:
                            nameDict[id[0]] = [items[i]]
                        else:
                            nameDict[id[0]].append(items[i])
        return nameDict


    def getDefendantInfo(self, data : dict):
        '''
        Finds all the defendants in the document, and returns them along with their
        relevant information: sex and date of birth.  This method is used when the
        information is not in a list.

        Keyword Arguments:
        data (dict): The data set to be extracting information from.

        Returns:
        defendantDict (dict): A dictionary containing all found defendant information.
        '''
        names = self.getNames([["Defendant Name(s)", ["defendant", "name", "defendant name"],["defendant"]]], data)
        if "Defendant Name(s)" not in names:
            return {}
        dobLocs = self.matchItemStrict("date of birth", data)
        addressLocs = self.findItem("address", data)
        sKeyLocs = self.findItem("sex", data)
        nameList = names["Defendant Name(s)"]
        defendantDict = {}
        for n in nameList:
            defendantDict[n] = {}
            minDistDate = 500
            dateChoice = ""
            # Make this function choose the date of birth that is closest to the
            # name first
            for dob in dobLocs:
                dates = self.makeMatch(dob, ["DATE", "CARDINAL"], data)
                for d in range(len(dates[0])):
                    dist = self.manhattan(dob, dates[0][d])
                    if dist < minDistDate:
                        minDistDate = dist
                        dateChoice = dates[1][d]
            defendantDict[n]["Date of Birth"] = dateChoice

            minDistSex = 500
            sexPossibilities = ["m", "f", "male", "female", "n/a"]
            sexChoice = ""
            for s in sKeyLocs:
                sexes = self.makeMatch(s, ["NONE"], data)
                for i in range(len(sexes[0])):
                    dist = self.manhattan(s, sexes[0][i])
                    if dist < minDistSex and sexes[1][i] in sexPossibilities:
                        minDistSex = dist
                        sexChoice = sexes[1][i]
            defendantDict[n]["Sex"] = sexChoice

            minDistAddr = 500
            addrChoiceLoc = (-1, -1)
            for adr in addressLocs:
                address = self.makeMatch(adr, ["GPE", "LOC", "ORG"], data)
                for a in range(len(address[0])):
                    dist = self.manhattan(adr, address[0][a])
                    if dist < minDistAddr:
                        minDistAddr = dist
                        addrChoiceLoc = address[0][a]
            fullAddrLine = ""
            toAdd = ""
            if addrChoiceLoc != (-1, -1):
                fullAddrLine = self.extendTerm(addrChoiceLoc, data).strip()
                # Check if the address is complete
                containsZip = regx.split(r'[^\d]', fullAddrLine)[-1]
                if containsZip is "" or len(containsZip) != 5:
                    # Find the line below the original address.
                    minheight = 300
                    for k in data.keys():
                        if (k[0] > addrChoiceLoc[0] - 50
                            and k[0] < addrChoiceLoc[0] + data[addrChoiceLoc][1] + 50
                            and k[1] > addrChoiceLoc[1]
                            and k[1] < addrChoiceLoc[1] + minheight):
                            nums = regx.split(r'[^\d]', self.extendTerm(k, data).strip()).remove("")
                            nums = [n for n in nums if n]
                            if nums != [] and len(nums[-1]) == 5:
                                minheight = k[1]
                                toAdd = " " + self.extendTerm(k, data).strip()
            defendantDict[n]["Address"] = fullAddrLine +  toAdd

        return defendantDict

    def getChargeInfo(self, data : dict):
        '''
        Find all the information about a specific charge: the offense date, the
        arrest date, the file date, the disposition date, and (hopefully) the charge
        text, sentencing, status, and disposition.

        Keyword Arguments:
        data (dict): The data set to be extracting information from.

        Returns:
        chargeInfo (dict): A dictionary containing all found charge information.
            If no offenses are found, the only entry in the offenses tab will be
            Offense 0.  This follows for all objects; any that are not found will
            be indexed by 0.
        '''
        DATE_REGX = regx.compile(r'^(0[1-9]|1[012]|[1-9])[- \/.](0[1-9]|[12][0-9]|3[01]|[1-9])[- \/.](19|20)\d\d$')
        # Most of these are dates.  So let's grab all of them.
        chargeInfo = {}
        dates = []
        for k in data.keys():
            val = regx.sub('^[\\\/\)\(]|[\\\/\)\(]$', '', data[k][0].strip())
            if DATE_REGX.fullmatch(val) != None:
                dates.append([k, val])
        fileLoc = self.findItem("filing", data) + self.findItem("filed", data)
        offenseLoc = self.matchItemStrict("offense date", data)
        arrestLoc = self.matchItemStrict("arrest date", data)
        dispositionLoc = self.matchItemStrict("disposition date", data)
        prisonLoc = self.findItem("prison", data)
        jailLoc = self.findItem("jail", data)
        fineLoc = self.findItem("fine", data)
        probationLoc = self.findItem("probation", data)

        if len(fileLoc) > 0:
            fileDate = ""
            minDistFile = 300
            for f in fileLoc:
                for d in dates:
                    dist = self.manhattan(f, d[0])
                    if dist < minDistFile:
                        minDistFile = dist
                        fileDate = data[d[0]][0]
            chargeInfo["File Date"] = fileDate
        else:
            chargeInfo["File Date"] = ""

        i = 1
        if len(offenseLoc) > 0:
            for o in offenseLoc:
                chargeInfo["Offense " + str(i)] = {}
                minDistOff = 300
                offenseDate = ""
                for d in dates:
                    dist = self.manhattan(o, d[0])
                    if dist < minDistOff:
                        minDistOff = dist
                        offenseDate = d[1]
                chargeInfo["Offense " + str(i)]["Offense Date"] = offenseDate
                # Match a fine, jail, prison, and probation to the offense.
                # Probably will also want to match the disposition
                if len(arrestLoc) > 0:
                    for a in arrestLoc:
                        arrestDate = ""
                        minDistArr = 300
                        for d in dates:
                            dist = self.manhattan(a, d[0])
                            if dist < minDistArr:
                                minDistArr = dist
                                arrestDate = d[1]
                        chargeInfo["Offense " + str(i)]["Arrest Date"] = arrestDate
                else:
                    chargeInfo["Offense " + str(i)]["Arrest Date"] = ""

                if len(dispositionLoc) > 0:
                    for dis in dispositionLoc:
                        dispositionDate = ""
                        minDistDisp = 300
                        for d in dates:
                            dist = self.manhattan(dis, d[0])
                            if dist < minDistDisp:
                                minDistDisp = dist
                                dispositionDate = d[1]
                        chargeInfo["Offense " + str(i)]["Disposition Date"] = dispositionDate
                else:
                    chargeInfo["Offense " + str(i)]["Disposition Date"] = ""

                if len(prisonLoc) > 0:
                    minDistPrisName = 5000
                    choice = (0, 0)
                    for pris in prisonLoc:
                        dist = self.manhattan(o, pris)
                        if dist < minDistPrisName:
                            minDistPrisName = dist
                            choice = pris
                    minDistPrisChoice = 500
                    prisChoice = ""
                    if choice != (0, 0):
                        for k in data.keys():
                            fullTerm = self.extendTerm(k, data)
                            type = self.makeAssociation(fullTerm)
                            sep = self.manhattan(choice, k)
                            if type == "DATE" and sep < minDistPrisChoice:
                                minDistPrisChoice = sep
                                prisChoice = fullTerm
                        chargeInfo["Offense " + str(i)]["Prison Time"] = prisChoice
                        prisonLoc.remove(choice)
                else:
                    chargeInfo["Offense " + str(i)]["Prison Time"] = ""

                if len(jailLoc) > 0:
                    minDistJailName = 5000
                    choice = (0, 0)
                    for jail in jailLoc:
                        dist = self.manhattan(o, jail)
                        if dist < minDistJailName:
                            minDistJailName = dist
                            choice = jail
                    minDistJailChoice = 500
                    jailChoice = ""
                    if choice != (0, 0):
                        for k in data.keys():
                            fullTerm = self.extendTerm(k, data)
                            type = self.makeAssociation(fullTerm)
                            sep = self.manhattan(choice, k)
                            if type == "DATE" and sep < minDistJailChoice:
                                minDistJailChoice = sep
                                jailChoice = fullTerm
                        chargeInfo["Offense " + str(i)]["Jail Time"] = jailChoice
                        jailLoc.remove(choice)
                else:
                    chargeInfo["Offense " + str(i)]["Jail Time"] = ""

                if len(fineLoc) > 0:
                    minDistFineName = 5000
                    choice = (0, 0)
                    for fine in fineLoc:
                        dist = self.manhattan(o, fine)
                        if dist < minDistFineName:
                            minDistFineName = dist
                            choice = fine
                    minDistFineChoice = 500
                    fineChoice = ""
                    if choice != (0, 0):
                        for k in data.keys():
                            fullTerm = self.extendTerm(k, data)
                            type = self.makeAssociation(fullTerm)
                            sep = self.manhattan(choice, k)
                            if type == "MONEY" and sep < minDistJailChoice:
                                minDistFineChoice = sep
                                fineChoice = fullTerm
                        chargeInfo["Offense " + str(i)]["Fine"] = fineChoice
                        fineLoc.remove(choice)
                else:
                    chargeInfo["Offense " + str(i)]["Fine"] = ""

                if len(probationLoc) > 0:
                    minDistProbName = 5000
                    choice = (0, 0)
                    for prob in probationLoc:
                        dist = self.manhattan(o, prob)
                        if dist < minDistProbName:
                            minDistJailName = dist
                            choice = prob
                    minDistProbChoice = 500
                    probationChoice = ""
                    if choice != (0, 0):
                        for k in data.keys():
                            fullTerm = self.extendTerm(k, data)
                            type = self.makeAssociation(fullTerm)
                            sep = self.manhattan(choice, k)
                            if type == "DATE" and sep < minDistProbChoice:
                                minDistProbChoice = sep
                                probationChoice = fullTerm
                        chargeInfo["Offense " + str(i)]["Probation Time"] = probationChoice
                        probationLoc.remove(choice)
                else:
                    chargeInfo["Offense " + str(i)]["Probation Time"] = ""

                i += 1
        else:
            chargeInfo["Offense 0"] = {}
            chargeInfo["Offense 0"]["Offense Date"] = ""

        return chargeInfo

    def isList(self, keyword : str, expected : list, data : dict):
        '''
        Checks if the desired data is in a list.

        Keyword Arguments:
        keyword (str): The expected title of the list object.
        expected (list): The possible set of strings which may be in the list.
        data (dict): The data set to be extracting information from.

        Returns:
        pos (tuple): The location of the list header.  Returns (-1, -1) if not
            found.
        '''
        keywordLocs = self.findItem(keyword, data)
        for k in keywordLocs:
            # Find the elements below the keyword
            x_0 = k[0]
            y_0 = k[1]
            x_1 = k[0] + data[k][1]
            count = 0
            for item in data.keys():
                x_t = item[0]
                y_t = item[1]
                if x_t > x_0 - 15 and x_t < x_1 + 15 and y_t > y_0 and data[item][0] in expected:
                    count += 1
                    if count >= 2:
                        return k
        return (-1, -1)


    def getDefendantInfoList(self, keyrow : tuple, data : dict):
        '''
        Gets the information about a defendant out of a list.

        Keyword Arguments:
        keyrow (tuple): The location of the "defendant" keyword.
        data (dict): The data set to be extracting information from.

        Returns:
        finalDefendants (dict): A dictionary of the defendants, along with their
            respective information.
        '''
        # First, identify what each column represents.
        listItems = []
        rows = []
        seenItems = []
        for k in data.keys():
            x_t = k[0]
            y_t = k[1]
            fullItem = self.extendTerm(k, data)
            if y_t < keyrow[1] + 15 and y_t > keyrow[1] - 15 and fullItem not in seenItems:
                listItems.append(k)
                seenItems.append(fullItem)
            if data[k][0] == 'defendant' and x_t > keyrow[0] - 15 and x_t < keyrow[0] + 15:
                rows.append(k)
        # The column locations are in list items. Then, extract all relevant information:
        seenTerms = []
        defendants = {}
        finalDefendants = {}
        i = 0
        for defn in rows:
            defendants[i] = {}
            for item in listItems:
                x_i = item[0]
                y_i = defn[1]
                for k in data.keys():
                    x_t = k[0]
                    y_t = k[1]
                    if x_t < x_i + 15 and x_t > x_i - 15 and y_t < y_i + 80 and y_t > y_i - 80:
                        fullTerm = self.extendTerm(item, data)
                        fullName = self.extendTerm(k, data)
                        if "name" in fullTerm and fullName not in seenTerms:
                            defendants[i]["Defendant Name"] = fullName
                            seenTerms.append(fullName)
                        elif "sex" in fullTerm:
                            defendants[i]["Sex"] = fullName
                        elif "birth" in fullTerm:
                            defendants[i]["Date of Birth"] = fullName
                        elif "address" in fullTerm:
                            defendants[i]["Address"] = fullName
            if "Defendant Name" in defendants[i]:
                finalDefendants[defendants[i]["Defendant Name"]] = {}
                if "Sex" in defendants[i]:
                    finalDefendants[defendants[i]["Defendant Name"]]["Sex"] = defendants[i]["Sex"]
                else:
                    finalDefendants[defendants[i]["Defendant Name"]]["Sex"] = ""
                if "Date of Birth" in defendants[i]:
                    finalDefendants[defendants[i]["Defendant Name"]]["Date of Birth"] = defendants[i]["Date of Birth"]
                else:
                    finalDefendants[defendants[i]["Defendant Name"]]["Date of Birth"] = ""
                if "Address" in defendants[i]:
                    finalDefendants[defendants[i]["Defendant Name"]]["Address"] = defendants[i]["Address"]
                else:
                    finalDefendants[defendants[i]["Defendant Name"]]["Address"] = ""
            i += 1
        return finalDefendants


    def getJurisdiction(self, counties : list, data : dict):
        '''
        Finds the proper jurisdiction for a given case from the list of jurisdictions
        found on prior webpages and searching for the term "county."

        Keyword Arguments:
        counties (list): A list containing all the previously seen county values
        data (dict): A dictionary of the data parsed from the image.

        Returns:
        jurisdiction (str): A string of the given county.
        '''
        # coun = self.findItem("county", data)
        countyChoice = ""
        # if len(coun) > 0:
        #     for c in coun:
        #         minDist = 200
        #         places = self.makeMatch(c, ["ORG", "LOC", "GPE", "PERSON"], data)
        #         for p in places[0]:
        #             dist = self.manhattan(p, c)
        #             if dist < minDist:
        #                 minDist = dist
        #                 countyChoice = data[p][0]
        # else:
        for c in counties:
            if c != None:
                countyChoice = c
                break
        return countyChoice

    def getCaseNum(self, data : dict):
        '''
        Gets the case number from the given document.
        '''
        caseNo = self.findItem("case", data)
        exc = ["number", "#", "no.", "no", "num"]
        minDist = 1000

        caseNoChoice = ""
        for c in caseNo:
            toCheck = c
            nums = self.makeMatch(c, ["CASENO"], data)
            for n in nums[0]:
                if data[n][0] not in exc:
                    dist = self.manhattan(toCheck, n)
                    if dist < minDist:
                        minDist = dist
                        caseNoChoice = data[n][0]
                else:
                    toCheck = n
        return caseNoChoice

    def parseData(self, path : str, county : list):
        '''
        Takes an input of a file path, then extracts the relevant information from
        the document.

        Keyword Arguments:
        path (str): A path to the intended image.

        Returns:
        parsed (dict): A dictionary of the extracted information.
        '''
        data = self.getRawData(path)
        grid = self.assembleData(data)
        rel = self.isList("relationship", ["plaintiff", "defendant", "judge"], grid)
        defn = {}
        charge = {}
        if (rel != (-1, -1)):
            defn = self.getDefendantInfoList(rel, grid)
            charge = self.getChargeInfo(grid)
        else:
            defn = self.getDefendantInfo(grid)
            charge = self.getChargeInfo(grid)
        case = self.getCaseNum(grid)
        jur = self.getJurisdiction(county, grid)
        parsed = charge
        parsed["Defendants"] = defn
        parsed["Jurisdiction"] = jur
        parsed["Case Number"] = case
        return parsed

if __name__ == "__main__":
    p = ImageParsing()
    print(p.parseData("HireRightImages/wisconsin.png", []))
