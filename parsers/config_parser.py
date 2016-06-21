'''

Created 14 may 2016

@author Lasse

'''
import json


class ConfigParser:

    def __init__(self):

        self.file = None
        self.conf = None

    def parse_config(self, file_name):

        self.file = open(file_name)
        self.conf = json.load(self.file)
        self.file.close()

        return self.conf
