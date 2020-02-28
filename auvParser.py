# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 14:11:17 2018

@author: park0387
"""

# auvParser.py
# Takes a KIRK log file (.txt) and parses it into a python dict.
# This can later be saved as a Matlab struct (.mat)
import os, re
import dateutil.parser
import datetime


# Main AUV log parsing function - pass filepath to this function.
def auvParse(filepath):
    data = open(filepath, encoding="cp437") # Sub log text file is encoded as cp137 (DOS format?)
    legacyKeyFile = None # Implement logic for finding legacy key file in working dir.

    # Get key info for parsing
    key = initKeys(data, legacyKeyFile)

    if not key:
        raise Exception('Empty key dict. Cannot parse log.')
    
    (hw_id, logDate) = getFilenameInfo(filepath)

    parsePath = os.path.abspath("AUV" + hw_id + "_" + logDate.strftime("%Y-%m-%d"))

    # Make sure output log folder exists, and if not, make it.
    if not os.path.isdir(parsePath):
        os.makedirs(parsePath)

    # Double check to see if folder exists before moving on.
    # If not, raise exception to stop Bad Things(TM) from happening
    if os.path.isdir(parsePath):
        Log = extractLog(data, key, hw_id)
        
    else:
        raise Exception("Parsing folder missing - did you delete it mid-execution?")

    return 0 #return actual parse

# Returns dict with year, month, day, hw_id of log
def getFilenameInfo(filepath):
    filename = os.path.split(filepath)[1] # separate filename from file path
    # search filename string using regex, separate out req'd variables
    reSplit = re.search(r"sub(\d*)_(.+)", filename)

    hw_id = reSplit.group(1)
    # use magic dateutil parser library to parse weirdly formatted date.
    # if the date format ever changes this will still magically parse correctly.
    logDate = dateutil.parser.parse(reSplit.group(2))

    return (hw_id, logDate)


# Check for keys in log header and parse; if not, fall back to legacyKeyFile and parse
# Returns key dict
def initKeys(data, legacyKeyFile=None): # Default to None for legacyKeyFile

    for line in data:
        # scan file for BEGIN PACKET KEYS
        if re.match(r'BEGIN PACKET KEYS',line):
            key = parseKeys(data)
            return key
        elif line[:5] == "START":   # if no key header in log, fall back to legacy
            legacyKeyData = open(legacyKeyFile)
            key = parseKeys(legacyKeyData)
            legacyKeyData.close() # clean up after yourself
            return key

# Read open data file and parse log keys
# Returns list of dicts for each key type
def parseKeys(data):
    key = []

    # Build key dict for use in log parse
    for i, line in enumerate(data):
        if line[:3] == "KEY":
            # Use regex to grab contents of each () and {} in a given line
            regexSplit = re.search(r"\(([^)]+)\)\(([^)]+)\)\(([^)]+)\)\{([^)]+)\}",line)
            key.append({"title": regexSplit.group(1).lower()})
            key[i]["subpackets"] = regexSplit.group(2)
            key[i]["cformat"] = regexSplit.group(3)
            # Grab string of entries, remove '' wrapping, make lowercase
            # and split into list with delimiter ,
            key[i]["entry"] = regexSplit.group(4).replace('\'', '').lower().split(',')

        # Return when we see the end of the key definition
        if re.match("END PACKET KEYS", line):
            return key
    # If you got here something's wrong
    raise Exception('Malformed key header? No END PACKET KEYS found')


def extractLog(data, key, hw_id):
    for line in data:
        if re.match('START', line): # if START is found in line
            # if Log variable has not been initalized
            # This safeguards against repeated START packets.
            if not 'Log' in locals(): 
                Log = Log(key, hw_id) # initalize log based on key and hw_id
                Log.start.parse(line) # Parse START packet


    return Log

# converts a timestamp log string to seconds.
def convertLogTimestamp(ts):
    reDate = re.findall(r"[0-9]+", ts)
    reDate = [int(i) for i in reDate]
    # convert from HH:MM:SS:sss -> seconds for timestamp
    return sum(map(lambda x,y:x*y, reDate, [3600, 60, 1, 0.001]))

class Log:
    # constructor
    def __init__(self, key, hw_id):
        self.key = key
        self.hw_id = hw_id
        self.start = self.start(hw_id) 
        #self.parsed.date = datetime.datetime.now()

    class start():
        def __init__(self, hw_id):
            self.hardware_id = hw_id

        def parse(self, line):
            strSplit = line.split(',')
            self.runStart      = convertLogTimestamp(strSplit[0])
            self.mission_no    = strSplit[1]
            self.run_no        = strSplit[2]
            self.vehicle_pos   = strSplit[3]
            self.software_id   = strSplit[4]
            self.leader_flag   = strSplit[5]
            self.comms_mode    = strSplit[6]
            self.date          = strSplit[7]
            #self.hardware_id   = self.hw_id
            
    # handle a start packet line
    # def parseStart(self, line):
    #     strSplit = line.split(',')
    #     self.start.runStart      = convertLogTimestamp(strSplit[0])
    #     self.start.mission_no    = strSplit[1]
    #     self.start.run_no        = strSplit[2]
    #     self.start.vehicle_pos   = strSplit[3]
    #     self.start.software_id   = strSplit[4]
    #     self.start.leader_flag   = strSplit[5]
    #     self.start.comms_mode    = strSplit[6]
    #     self.start.date          = strSplit[7]
    #     self.start.hardware_id   = self.hw_id

    def parseAbort(self, line):
        strSplit = line.split(',')
        Log.start.runEnd = convertLogTimestamp(strSplit[0])
        Log.start.Abort = strSplit[1]
        




    
# Runs if file is executed directly. Used for testing.
# Don't execute directly in normal use.
if __name__ == "__main__":
    filepath = "KIRK_LOG_sub2_19-Apr-2018.txt"
    parse = auvParse(filepath)