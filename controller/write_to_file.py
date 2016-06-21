'''
Created on 8 june 2016

@author Lasse
'''


class WriteToFile:

    def __init__(self):

        self.file = None

    def write_g_code_list_to_file(self, file_name, g_code):

        self.file = open(file_name, "w")
        self.file.write(g_code)
        self.file.close()

    def write_log_to_file(self, message_list):

        self.file = open('Logfile.txt', "a")
        for line in message_list:
            self.file.write(line + "\n")
        self.file.close()

    def clear_log_file(self):
        self.file = open('Logfile.txt', "w")
        self.file.close()
