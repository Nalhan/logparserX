# -*- coding: utf-8 -*-

import sys, os
import numpy
import multiprocessing as mp
from PyQt5 import QtCore, QtGui, QtWidgets
from parsergui import Ui_MainWindow
from topsideParser import topsideParse
from dgpsParser import dgpsParse
# Filepath list generator function
# Returns a list of full paths to all files in a given directory
def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield (path + "/" + file) # full path + file name

# Main parser application, drives GUI interactions and calls parser functions
class parserApplication(Ui_MainWindow):
    def __init__(self,MainWindow):
        Ui_MainWindow.__init__(self)
        self.setupUi(MainWindow)

        # Connect "Browse..." button to custom function which opens file dialog window
        self.subBrowseButton.clicked.connect(self.selectSubLog)
        self.magBrowseButton.clicked.connect(self.selectMagLog)
        self.gpsBrowseButton.clicked.connect(self.selectGPSLog)
        self.topBrowseButton.clicked.connect(self.selectTopLog)
        self.outputBrowseButton.clicked.connect(self.selectOutputDir)
        self.runParseButton.clicked.connect(self.runParse)

    def selectSubLog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _filter = QtWidgets.QFileDialog.getOpenFileName(None,"Select log file...", "", "All Files (*);;Python Files (*.py)", options=options)

        # Set selected path to text box
        self.subFilePath.setText(fileName)

    def selectMagLog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _filter = QtWidgets.QFileDialog.getOpenFileName(None,"Select log file...", "", "All Files (*);;Python Files (*.py)", options=options)

        # Set selected path to text box
        self.magFilePath.setText(fileName)

    def selectGPSLog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _filter = QtWidgets.QFileDialog.getOpenFileName(None,"Select log file...", "", "DGPS Log (*.txt)", options=options)

        self.gpsFilePath.setText(fileName)

    def selectTopLog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        dir = QtWidgets.QFileDialog.getExistingDirectory(None,"Select topside log folder...", "", QtWidgets.QFileDialog.ShowDirsOnly)

        # Set selected path to text box
        self.topFilePath.setText(dir)


    def selectOutputDir(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(None, "Select output folder...", "", QtWidgets.QFileDialog.ShowDirsOnly)

        # Set selected path to text box
        self.outputFilePath.setText(dir)


    # Function that executes when Run Parse is clicked
    def runParse(self):

        logDir = self.outputFilePath.text()
        topsideDir = self.topFilePath.text()
        dgpsFile = self.gpsFilePath.text()

        # Throw exceptions for missing file or directory paths
        if logDir == "":
            raise Exception("No output directory path specified!")
        if topsideDir == "":
            raise Exception("No topside directory path specified!")
        if dgpsFile == "":
            raise Exception("No DGPS log specified!")

        # Grab all topside files
        topsideFiles = [s for s in files(topsideDir) if "PSK_Log" in s]

        # Execute processes in parallel for faster execution
        p1 = mp.Process(target=topsideProcess, args=(topsideFiles, logDir))
        p2 = mp.Process(target=dgpsProcess, args=(dgpsFile,logDir))
        p1.start()
        p2.start()


def topsideProcess(topsideFiles, logDir):
    # Function to run with multiprocessing
    # Allows topside parsing to be done in parallel with other functions

    topsideData = topsideParse(topsideFiles, 15) # 15 = 4 buoys

    # Save data
    # Retrieve test date from file name of PSK_Log.mode932.YY.MM.DD.*
    dateRaw = topsideFiles[0].split(".")[2]
    dateSplit = [dateRaw[i:i+2] for i in range(0, len(dateRaw), 2)]
    date = dateSplit[0] + "-" + dateSplit[1] + "-" + dateSplit[2]
    numpy.savetxt(logDir + "/toaTbl-" + date +".csv",topsideData,delimiter=",")

def dgpsProcess(dgpsFile, logDir):
    # Function to run with multiprocessing
    # Allows DGPS parsing to be done in parallel with other functions
    dgpsData = dgpsParse(dgpsFile)

    # Save dgpsData to dgps-date.csv
    numpy.savetxt(logDir + "/dgps" + ".csv", dgpsData, delimiter=",")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = parserApplication(MainWindow)

    MainWindow.show()

    sys.exit(app.exec_())
