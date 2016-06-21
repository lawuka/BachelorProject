'''

Created 14 may 2016

@author Lasse

'''

import xml.etree.ElementTree as Etree


class LibraryParser:

    def __init__(self):

        self.file = None
        self.root = None
        self.component_library = None

    def parse_component_library(self, file_name):

        self.file = open(file_name)
        self.root = Etree.parse(self.file).getroot()

        components = self.root.findall('Component')
        self.component_library = {}

        try:
            for component in components:
                component_type = component.find('Type').text
                self.component_library[component_type] = {}

                size = component.find('Size')
                self.component_library[component_type]['Size'] = size

                external = component.find('External')
                self.component_library[component_type]['External'] = external

                internal = component.find('Internal')
                self.component_library[component_type]['Internal'] = internal

                control = component.find('Control')
                self.component_library[component_type]['Control'] = control

            self.file.close()
        except LibraryParseError:
            pass

        return self.component_library


class LibraryParseError(Exception):
    pass
