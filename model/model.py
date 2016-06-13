from parsers.gParser import simulatorGCode
from parsers.gParser import microMillingFlowGCode, microMillingControlGCode
from parsers.svgParser import SVGParser, SVGFileErrorException
from parsers.libraryParser import LibraryParser
from parsers.configParser import ConfigParser


class Model:

    def __init__(self):
        self.simGCode = simulatorGCode()
        self.mmFlowGCode = microMillingFlowGCode()
        self.mmControlGCode = microMillingControlGCode()
        self.svgParser = SVGParser()
        self.libraryParser = LibraryParser()
        self.configParser = ConfigParser()

        self.svgData = None
        self.libraryData = None
        self.configData = None

        self.mmFlowGCodeData = None
        self.mmControlGCodeData = None
        self.simulatorGCodeData = None

        self.currentSVGFile = None
        self.currentLibraryFile = None
        self.currentConfigFile = None

    def set_micro_milling_flow_g_code(self):

        if self.check_for_files():
            self.mmFlowGCodeData = self.mmFlowGCode.createMMGCodeList(self.svgData,
                                                                      self.libraryData,
                                                                      self.configData)
            self.mmFlowGCode.mmGCodeList = []

    def set_micro_milling_control_g_code(self):

        if self.check_for_files():
            self.mmControlGCodeData = self.mmControlGCode.createMMGCodeList(self.svgData,
                                                                            self.libraryData,
                                                                            self.configData)
            self.mmControlGCode.mmGCodeList = []

    def set_simulator_g_code(self):

        if self.check_for_files():
            self.simulatorGCodeData = self.simGCode.createSimulatorGCodeList(self.svgData,
                                                                             self.libraryData,
                                                                             self.configData)
            self.simGCode.simulateGCodeList = []

    def set_svg_data(self):

        if self.currentSVGFile is None:
            raise NoFileException("Missing SVG File!")
        else:
            self.svgData = self.svgParser.parse_svg(self.currentSVGFile)

    def set_library_data(self):

        if self.currentLibraryFile is None:
            raise NoFileException("Missing Library File!")
        else:
            self.libraryData = self.libraryParser.parse_component_library(self.currentLibraryFile)

    def set_config_data(self):

        if self.currentConfigFile is None:
            raise NoFileException("Missing Configuration File!")
        else:
            self.configData = self.configParser.parse_config(self.currentConfigFile)

            confList = [self.configData['drillOptions']['drillSize'],
                        self.configData['drillOptions']['flow']['depth'],
                        self.configData['drillOptions']['hole']['depth'],
                        self.configData['valveOptions']['width'],
                        self.configData['valveOptions']['height']]

            configCount = 0
            for conf in confList:
                configCount += 1
                if conf == '' or conf == None:
                    raise ConfigFileErrorException("Configuration error in configuration number: " + str(configCount))

    def get_mm_flow_g_code(self):

        if self.mmFlowGCodeData is None:
            raise NoDataSavedException("Missing Micro Milling Flow G-Code Data!")
        else:
            return self.mmFlowGCodeData

    def get_mm_control_g_code(self):

        if self.mmControlGCodeData is None:
            raise NoDataSavedException("Missing Micro Milling Control G-Code Data!")
        else:
            return self.mmControlGCodeData

    def get_simulator_g_code(self):

        if self.simulatorGCodeData is None:
            raise NoDataSavedException("Missing Simulator G-Code Data!")
        else:
            return self.simulatorGCodeData

    def get_svg_data(self):

        if self.svgData is None:
            self.set_svg_data()
        return self.svgData

    def get_library_data(self):

        if self.libraryData is None:
            self.set_library_data()
        return self.libraryData

    def get_config_data(self):

        if self.configData is None:
            self.set_config_data()
        return self.configData

    def set_current_svg_file(self, file):

        self.currentSVGFile = file

    def set_current_library_file(self, file):

        self.currentLibraryFile = file

    def set_current_config_file(self, file):

        self.currentConfigFile = file

    def check_for_files(self):
        if self.currentSVGFile is None:
            raise NoFileException("Missing SVG File!")
        elif self.currentLibraryFile is None:
            raise NoFileException("Missing Library File!")
        elif self.currentConfigFile is None:
            raise NoFileException("Missing Configuration File!")
        else:
            return True


class NoFileException(Exception):
    pass


class NoDataSavedException(Exception):
    pass


class ConfigFileErrorException(Exception):
    pass
