'''

Created 14 may 2016

@author Lasse

'''

import xml.etree.ElementTree as etree

class libraryParser():

    def __init__(self):

        self.file = None

    def parseComponentLibrary(self, fileName):

        self.file = open(fileName)
        self.root = etree.parse(self.file).getroot()

        components = self.root.findall('Component')
        self.componentLibrary = {}

        try:
            for component in components:
                type = component.find('Type').text
                self.componentLibrary[type] = {}

                size = component.find('Size')
                self.componentLibrary[type]['Size'] = size

                external = component.find('External')
                self.componentLibrary[type]['External'] = external

                internal = component.find('Internal')
                self.componentLibrary[type]['Internal'] = internal

                control = component.find('Control')
                self.componentLibrary[type]['Control'] = control

            self.file.close()
        except LibraryParseError:
            pass

        return self.componentLibrary

class LibraryParseError(Exception):
    pass
