# For Data Management
import json

# For Date Formatting
import datetime

# Will be given a single dictionary from a picture parsing class that contains candidate's case data.
# Testing variable for candidate's case data

class DataStorage:
    #######################################################################
    # CONSTRUCTOR

    # Will default to strings in parameter if no arguments are given    
    def __init__(self, _lName="lname", _fName="fname", _mName="mname", _dob=datetime.datetime(1984, 6, 6)):
        self.__LNAME = _lName
        self.__FNAME = _fName
        self.__MNAME = _mName
        self.__DOB = _dob

        self.__FILE_NAME__ = f"{self.__LNAME}_{self.__FNAME}_{self.__MNAME}_{self.__DOB:%y}{self.__DOB:%m}{self.__DOB:%d}.json"
        self.__CAND__ = []


    #######################################################################
    # METHODS

    def recordData(self, case):
        '''
        Given a candidate's case (dictionary), this function will
        append the case data to the candidate (list of dictionaries)
        and then output it to the JSON file: __FILE_NAME__.
        '''

        self.checkIfFileExists()
        
        # Grab candidate from the file, so that we can append the case data
        with open(self.__FILE_NAME__, "r") as read_file:
            _candData = json.load(read_file)

        # Append case data to candidate
        self.__CAND__.append(case)

        # Write updated candidate's data to file
        with open(self.__FILE_NAME__, "w") as write_file:
            json.dump(self.__CAND__, write_file)    


    def clearData(self):
        '''
        Given a candidate's file (string), clear the data associated with them
        '''

        self.checkIfFileExists()

        # Grab candidate from the file, so that we can append the case data
        with open(self.__FILE_NAME__, "r") as read_file:
            _candData = json.load(read_file)  

        # Clear the candidate's data
        _candData.clear()

        # Write updated candidate's data to file
        with open(self.__FILE_NAME__, "w") as write_file:
            json.dump(_candData, write_file)


    def printData(self):
        '''
        Given a file name (string), print the data in the file.
        '''

        self.checkIfFileExists()

        with open(self.__FILE_NAME__, "r") as read_file:
            _candData = json.load(read_file)        
            print(json.dumps(_candData, indent=4, sort_keys=True))

        
    #######################################################################
    # HELPER METHODS

    def checkIfFileExists(self):
        '''
        Given a file name (string), see if file exists. If it does not,
        create one.
        '''

        try:   
            file = open(self.__FILE_NAME__)
            file.close()
            return True
            
        except FileNotFoundError:
            print(f"There is no file. One is created under: {self.__FILE_NAME__}")            
            with open(self.__FILE_NAME__, "w") as write_file:
                json.dump(self.__CAND__, write_file)
            return False


    def getFileName(self):
        '''
        Return File name as string
        '''
        print(self.__FILE_NAME__)
        
        return self.__FILE_NAME__
        


#######################################################################
#=====================================================================#
#========================= END OF CLASS ==============================#            
#=====================================================================#   
#######################################################################


# Driver program
if __name__ == "__main__":
    __CASE__ = {
        "courtCaseID": "001",
        "fName": "John",
        "mName": "Bob",
        "lName": "Smith",
        "gender": "Boy",
        "dob": "01/01/1984",
        "jName": "Justice",
        "jState": "South Carolina",
        "offDate": "02/02/2002",
        "arrDate": "02/03/2002",
        "fileDate": "02/05/2002",
        "disDate": "03/03/2002",
        "chargeStat": "Assault",
        "chargeDisp": "Trial",
        "chargeSent": "Fine",
        "prisTime": "None",
        "jailTime": "None",
        "probation": "None",
        "fine": "1,500",    
        }

    __CASE2__ = {
        "courtCaseID": "002",
        "fName": "John",
        "mName": "Bob",
        "lName": "Smith",
        "gender": "Boy",
        "dob": "01/01/1984",
        "jName": "Justice",
        "jState": "South Carolina",
        "offDate": "12/02/2005",
        "arrDate": "12/03/2005",
        "fileDate": "12/05/2005",
        "disDate": "11/03/2005",
        "chargeStat": "Sexual Assault",
        "chargeDisp": "Trial",
        "chargeSent": "Prison",
        "prisTime": "5 Years",
        "jailTime": "None",
        "probation": "None",
        "fine": "0",    
        }
    

    dataStorage = DataStorage()
    dataStorage.clearData()
    #dataStorage.recordData(__CASE__)
    #dataStorage.recordData(__CASE2__)
    dataStorage.printData()
    dataStorage.getFileName()
