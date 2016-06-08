from parsers.gParser import simulatorGCode
from parsers.gParser import microMillingFlowGCode
from parsers.svgParser import svgParser
from parsers.libraryParser import libraryParser
from parsers.configParser import configParser

class Model():

    def __init__(self):
        self.simGCode = simulatorGCode()
        self.mmFlowGCode = microMillingFlowGCode()
        self.svgParser = svgParser()
        self.libraryParser = libraryParser()
        self.configParser = configParser()

        self.svgData = None
        self.libraryData = None
        self.configData = None

        self.mmFlowGCodeData = None
        self.simulatorGCodeData = None

        self.currentSVGFile = None
        self.currentLibraryFile = None
        self.currentConfigFile = None

    def setMicroMillingFlowGCode(self):

        if self.currentSVGFile == None or self.currentLibraryFile == None or self.currentConfigFile == None:
            raise NoFileException("Missing SVG, Library or Config")
        else:
            self.mmFlowGCodeData = self.mmFlowGCode.createMMGCodeList(self.svgData, self.libraryData, self.configData)
            self.mmFlowGCode.mmGCodeList = []

    def setSimulatorGCode(self):

        if self.currentSVGFile == None or self.currentLibraryFile == None or self.currentConfigFile == None:
            raise NoFileException("Missing SVG, Library or Config")
        else:
            self.simulatorGCodeData = self.simGCode.createSimulatorGCodeList(self.svgData, self.libraryData, self.configData)
            self.simGCode.simulateGCodeList = []

    def setSVGData(self):

        if self.currentSVGFile == None:
            raise NoFileException("Missing SVG File")
        else:
            self.svgData = self.svgParser.parseSvg(self.currentSVGFile)

    def setLibraryData(self):

        if self.currentLibraryFile == None:
            raise NoFileException("Missing Library File")
        else:
            self.libraryData = self.libraryParser.parseComponentLibrary(self.currentLibraryFile)

    def setConfigData(self):

        if self.currentConfigFile == None:
            raise NoFileException("Missing Configuration File")
        else:
            self.configData = self.configParser.parseConfig(self.currentConfigFile)

    def getMMFlowGCode(self):

        return self.mmFlowGCodeData

    def getSimulatorGCode(self):

        return self.simulatorGCodeData

    def getSVGData(self):

        if self.svgData == None:
            self.setSVGData()
        return self.svgData

    def getLibraryData(self):

        if self.libraryData == None:
            self.setLibraryData()
        return self.libraryData

    def getConfigData(self):

        if self.configData == None:
            self.setConfigData()
        return self.configData

    def setCurrentSVGFile(self, file):

        self.currentSVGFile = file

    def setCurrentLibraryFile(self, file):

        self.currentLibraryFile = file

    def setCurrentConfigFile(self, file):

        self.currentConfigFile = file

class NoFileException(Exception):
    pass