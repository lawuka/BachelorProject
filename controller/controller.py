'''
Created on 16 june 2015

@author Lasse
'''

import time
import datetime
import model.model as model
from controller.write_to_file import WriteToFile
from view.view import View
from parsers.architecture_parser import ArchitectureFileErrorException


class Controller:

    def __init__(self):

        self.model = model.Model()
        self.view = View(self)
        self.wtf = WriteToFile()
        self.log_file_list = None
        self.error_occurred = False

    # Start the program
    def run(self):

        # Clear log file
        self.log_file_list = []
        self.wtf.clear_log_file()

        # Start the GUI
        self.view.show()
        self.view.deiconify()
        self.view.mainloop()

    # Function for creating Simulator G-code
    def create_sim_g_code(self):

        # Try creating the Simulator G-code, and catch exception if occuring
        try:
            self.update_data()
            self.error_update(0)
            self.check_for_architecture_parser_errors()
            self.model.set_simulator_g_code()
            self.view.update_status_message()
            return True
        except model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return False
        except model.NoDataSavedException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return False
        except model.ConfigFileErrorException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return False

    # Function for creating Micro Milling Flow Layer G-code
    def create_mm_flow_g_code(self):

        # Try creating the Micro Milling Flow Layer G-code, and catch exception if occuring
        try:
            self.update_data()
            self.error_update(0)
            self.check_for_architecture_parser_errors()
            self.model.set_micro_milling_flow_g_code()
            self.view.update_status_message()
            return True
        except model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return False
        except model.NoDataSavedException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return False
        except model.ConfigFileErrorException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return False

    # Function for creating Micro Milling Control Layer G-code
    def create_mm_control_g_code(self):

        # Try creating the Micro Milling Control Layer G-code, and catch exception if occuring
        try:
            self.update_data()
            self.error_update(0)
            self.check_for_architecture_parser_errors()
            self.model.set_micro_milling_control_g_code()
            self.view.update_status_message()
            return True
        except model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return False
        except model.NoDataSavedException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return False
        except model.ConfigFileErrorException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return False

    # Function for writing G-code to a file.
    def write_g_code_to_file(self, file_name, g_code_list):

        self.wtf.write_g_code_list_to_file(file_name, g_code_list)

    # Update model data.
    def update_data(self):

        self.model.set_config_data()
        self.model.set_library_data()
        self.model.set_architecture_data()

    # Get chip layout, which is also the biochip architecture
    def get_chip_layout(self):

        try:
            self.update_data()
            self.error_update(0)
            self.check_for_architecture_parser_errors()
            self.view.update_status_message()
            return self.model.get_architecture_data()
        except model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return None
        except model.NoDataSavedException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return None
        except model.ConfigFileErrorException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return None
        except ArchitectureFileErrorException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()
            return None

    # Set the current biochip architecture file
    def set_architecture_file(self, file_name):

        self.model.current_architecture_file = file_name

    # Set the current component library file
    def set_library_file(self, file_name):

        self.model.current_library_file = file_name

    # Set the current configuration file
    def set_config_file(self, file_name):

        self.model.current_config_file = file_name

    def get_library_data(self):
        try:
            self.error_update(0)
            return self.model.get_library_data()
        except model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()

    def get_config_data(self):
        try:
            self.error_update(0)
            return self.model.get_config_data()
        except model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.update_status_message()

    # Log any errors
    def add_to_log(self, message):
        self.error_update(1)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        self.log_file_list.append(st + ": " + str(message))
        self.wtf.write_log_to_file(self.log_file_list)
        self.log_file_list = []

    def error_update(self, error_status):
        if error_status == 1:
            self.error_occurred = True
        else:
            self.error_occurred = False
        pass

    def check_for_architecture_parser_errors(self):
        # Check for parser errors in components
        if self.model.architecture_parser.component_errors:
            for error in self.model.architecture_parser.component_errors:
                self.add_to_log(error)
        # Check for parser errors in lines
        if self.model.architecture_parser.line_errors:
            for error in self.model.architecture_parser.line_errors:
                self.add_to_log(error)

    def get_model(self):

        return self.model
