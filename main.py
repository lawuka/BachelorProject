'''
Created on 24 feb 2015

@author Lasse
'''
import time, datetime
import model.model as Model
from view.view import View
from parsers.svgParser import SVGFileErrorException
from model.model import ConfigFileErrorException


class Controller:

    def __init__(self):

        self.model = Model.Model()
        self.view = View(self)
        self.wtf = WriteToFile()
        self.logFileList = None
        self.errorOccurred = False

    def run(self):

        self.logFileList = []
        self.wtf.clear_log_file()
        self.view.show()
        self.view.deiconify()
        self.view.mainloop()

    def create_sim_g_code(self):

        try:
            self.update_data()
            self.model.set_simulator_g_code()
            self.write_g_code_to_file("SimulatorGCode.ngc", self.model.get_simulator_g_code())
            self.error_update(0)
            return True
        except Model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return False
        except Model.NoDataSavedException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return False
        except Model.ConfigFileErrorException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return False

    def create_mm_flow_g_code(self):

        try:
            self.update_data()
            self.model.set_micro_milling_flow_g_code()
            self.write_g_code_to_file("MMFlowGCode.txt", self.model.get_mm_flow_g_code())
            self.error_update(0)
            return True
        except Model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return False
        except Model.NoDataSavedException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return False
        except Model.ConfigFileErrorException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return False

    def create_mm_control_g_code(self):

        try:
            self.update_data()
            self.model.set_micro_milling_control_g_code()
            self.write_g_code_to_file("MMControlGCode.txt", self.model.get_mm_control_g_code())
            self.error_update(0)
            return True
        except Model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return False
        except Model.NoDataSavedException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return False
        except Model.ConfigFileErrorException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return False

    def write_g_code_to_file(self, file_name, g_code_list):

        self.wtf.write_g_code_list_to_file(file_name, g_code_list)

    def update_data(self):

        self.model.set_config_data()
        self.model.set_library_data()
        self.model.set_svg_data()

    def get_chip_layout(self):

        try:
            self.update_data()
            self.error_update(0)
            if self.model.svgParser.componentErrors != []:
                for error in self.model.svgParser.componentErrors:
                    self.add_to_log(error)
            if self.model.svgParser.lineErrors != []:
                for error in self.model.svgParser.lineErrors:
                    self.add_to_log(error)
            self.view.updateStatusMessage()
            return self.model.get_svg_data()
        except Model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return None
        except Model.NoDataSavedException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return None
        except Model.ConfigFileErrorException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return None
        except SVGFileErrorException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()
            return None

    def set_svg_file(self, file_name):

        self.model.currentSVGFile = file_name

    def set_library_file(self, file_name):

        self.model.currentLibraryFile = file_name

    def set_config_file(self, file_name):

        self.model.currentConfigFile = file_name

    def get_library_data(self):
        try:
            self.error_update(0)
            return self.model.get_library_data()
        except Model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()

    def get_config_data(self):
        try:
            self.error_update(0)
            return self.model.get_config_data()
        except Model.NoFileException as msg:
            self.add_to_log(msg)
            self.view.updateStatusMessage()

    def add_to_log(self, message):
        self.error_update(1)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        self.logFileList.append(st + ": " + str(message))
        self.wtf.write_log_to_file(self.logFileList)
        self.logFileList = []

    def error_update(self, error_status):
        if error_status == 1:
            self.errorOccurred = True
        else:
            self.errorOccurred = False
        pass

    def get_model(self):

        return self.model


class WriteToFile:

    def __init__(self):

        self.file = None

    def write_g_code_list_to_file(self, file_name, g_code_list):

        self.file = open(file_name, "w")
        for line in g_code_list:
            self.file.write(line + "\n")
        self.file.close()

    def write_log_to_file(self, message_list):

        self.file = open('Logfile.txt', "a")
        for line in message_list:
            self.file.write(line + "\n")
        self.file.close()

    def clear_log_file(self):
        self.file = open('Logfile.txt', "w")
        self.file.close()



'''
Triggering the main program
'''
if __name__ == '__main__':
    controller = Controller()
    controller.run()
