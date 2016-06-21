'''
Created on 8 june 2016

@author Lasse
'''

from parsers.g_code_parser import SimulatorGCode
from parsers.g_code_parser import MicroMillingFlowGCode, MicroMillingControlGCode
from parsers.architecture_parser import ArchitectureParser
from parsers.library_parser import LibraryParser
from parsers.config_parser import ConfigParser


class Model:

    def __init__(self):
        self.sim_g_code = SimulatorGCode()
        self.mm_flow_g_code = MicroMillingFlowGCode()
        self.mm_control_g_code = MicroMillingControlGCode()
        self.architecture_parser = ArchitectureParser()
        self.library_parser = LibraryParser()
        self.config_parser = ConfigParser()

        self.architecture_data = None
        self.library_data = None
        self.config_data = None

        self.mm_flow_g_code_data = None
        self.mm_control_g_code_data = None
        self.simulator_g_code_data = None

        self.current_architecture_file = None
        self.current_library_file = None
        self.current_config_file = None

    def set_micro_milling_flow_g_code(self):

        if self.check_for_files():
            self.mm_flow_g_code_data = self.mm_flow_g_code.create_mm_g_code_list(self.architecture_data,
                                                                                 self.library_data,
                                                                                 self.config_data)
            self.mm_flow_g_code.mm_g_code_list = []

    def set_micro_milling_control_g_code(self):

        if self.check_for_files():
            self.mm_control_g_code_data = self.mm_control_g_code.create_mm_g_code_list(self.architecture_data,
                                                                                       self.library_data,
                                                                                       self.config_data)
            self.mm_control_g_code.mm_g_code_list = []

    def set_simulator_g_code(self):

        if self.check_for_files():
            self.simulator_g_code_data = self.sim_g_code.create_simulator_g_code_list(self.architecture_data,
                                                                                      self.library_data,
                                                                                      self.config_data)
            self.sim_g_code.simulate_g_code_list = []

    def set_architecture_data(self):

        if self.current_architecture_file is None:
            raise NoFileException("Missing SVG File!")
        else:
            self.architecture_data = self.architecture_parser.parse_architecture(self.current_architecture_file)

    def set_library_data(self):

        if self.current_library_file is None:
            raise NoFileException("Missing Library File!")
        else:
            self.library_data = self.library_parser.parse_component_library(self.current_library_file)

    def set_config_data(self):

        if self.current_config_file is None:
            raise NoFileException("Missing Configuration File!")
        else:
            self.config_data = self.config_parser.parse_config(self.current_config_file)
            # Check that each configuration is correctly defined.
            conf_list = [self.config_data['Flow_Layer_Options']['Drill_Z_Top'],
                         self.config_data['Flow_Layer_Options']['Valve_Discontinuity_Width'],
                         self.config_data['Flow_Layer_Options']['Flow_Drill_Size'],
                         self.config_data['Flow_Layer_Options']['Flow_Depth'],
                         self.config_data['Flow_Layer_Options']['Hole_Drill_Size'],
                         self.config_data['Flow_Layer_Options']['Hole_Depth'],
                         self.config_data['Control_Layer_Options']['Drill_Z_Top'],
                         self.config_data['Control_Layer_Options']['Subsidence_Drill_Size'],
                         self.config_data['Control_Layer_Options']['Subsidence_Depth'],
                         self.config_data['Control_Layer_Options']['Hole_Drill_Size'],
                         self.config_data['Control_Layer_Options']['Hole_Depth']]

            config_count = 0
            for conf in conf_list:
                config_count += 1
                if conf == '' or conf is None:
                    raise ConfigFileErrorException("Configuration error in configuration number: " + str(config_count))

    def get_mm_flow_g_code(self):

        if self.mm_flow_g_code_data is None:
            raise NoDataSavedException("Missing Micro Milling Flow G-Code Data!")
        else:
            return self.mm_flow_g_code_data

    def get_mm_control_g_code(self):

        if self.mm_control_g_code_data is None:
            raise NoDataSavedException("Missing Micro Milling Control G-Code Data!")
        else:
            return self.mm_control_g_code_data

    def get_simulator_g_code(self):

        if self.simulator_g_code_data is None:
            raise NoDataSavedException("Missing Simulator G-Code Data!")
        else:
            return self.simulator_g_code_data

    def get_architecture_data(self):

        if self.architecture_data is None:
            self.set_architecture_data()
        return self.architecture_data

    def get_library_data(self):

        if self.library_data is None:
            self.set_library_data()
        return self.library_data

    def get_config_data(self):

        if self.config_data is None:
            self.set_config_data()
        return self.config_data

    def set_current_architecture_file(self, file):

        self.current_architecture_file = file

    def set_current_library_file(self, file):

        self.current_library_file = file

    def set_current_config_file(self, file):

        self.current_config_file = file

    # Used by must function, to check that files are okay and not missing.
    def check_for_files(self):
        if self.current_architecture_file is None:
            raise NoFileException("Missing Architecture File!")
        elif self.current_library_file is None:
            raise NoFileException("Missing Library File!")
        elif self.current_config_file is None:
            raise NoFileException("Missing Configuration File!")
        else:
            return True


class NoFileException(Exception):
    pass


class NoDataSavedException(Exception):
    pass


class ConfigFileErrorException(Exception):
    pass
