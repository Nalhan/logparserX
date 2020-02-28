# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 13:46:08 2018

@author: park0387
"""

# dgpsParser.py
# Processes DGPS data 

import numpy
import datetime, pytz
import dateutil.parser

def dgpsParse(filename):
    data = open(filename,'r')
    dgpsData = []
    for line in data:
        # split line with delimiter " "
        splitLine = line.split(" ")
        
        strDate = splitLine[0] # datestring is first chunk of line
        date = dateutil.parser.parse(strDate) # parse ISO format date to datetime object
        naive_date = date.astimezone(pytz.utc).replace(tzinfo=None) # convert to UTC and strip timezone
        
        # Calculate seconds after midnight and append to list
        dgpsData.append((naive_date - datetime.datetime.min).seconds)
        # Append rest of values
        for j in range(5):
            # cast from unicode to float, so numpy.savetxt works
            dgpsData.append(float(splitLine[j+1]))
    dgpsData = numpy.asarray(dgpsData)
    numRows = int(len(dgpsData)/6)
    # Reshape to expected dimensions for processing
    dgpsData = numpy.reshape(dgpsData, (numRows, 6))
    
    data.close()
    return dgpsData
if __name__ == "__main__":
    dgpsData = dgpsParse('180419_ui_alpha32_rover1_track.txt')
    print(dgpsData)
    #with open('dgpsData.csv','ab') as f:
    numpy.savetxt('dgpsData.csv',dgpsData,delimiter=",")