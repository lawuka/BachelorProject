'''

Created 24 feb 2016

@author Lasse

'''

import xml.etree.ElementTree as Etree


class ArchitectureParser:

    def __init__(self):

        self.file = None
        self.tree = None
        self.tree_root = None
        self.map = None
        self.line_errors = None
        self.component_errors = None

    # Parse the biochip architecture
    def parse_architecture(self, file_name):

        self.file = open(file_name)
        # Error list, if errors occure in line or components
        self.line_errors = []
        self.component_errors = []
        try:
            # Parse the file
            self.tree = Etree.parse(self.file)
            self.tree_root = self.tree.getroot()
            self.map = {}

            # Check that the architecture width and height are defined
            self.map['width'] = self.tree_root.find('size').get('width')
            if self.map['width'] not in {None, ""}:
                self.map['height'] = self.tree_root.find('size').get('height')
                if self.map['height'] not in {None, ""}:

                    self.map['components'] = []
                    self.map['lines'] = []

                    line_count = 0
                    component_count = 0
                    for elements in self.tree_root:
                        for element in elements:
                            temp_list = []
                            # Flow lines in architecture
                            if element.tag == 'line':
                                line_count += 1
                                ele1 = element.get('x1')
                                ele2 = element.get('y1')
                                ele3 = element.get('x2')
                                ele4 = element.get('y2')
                                # Check that the line is defined correctly
                                if None in {ele1, ele2, ele3, ele4} or "" in {ele1, ele2, ele3, ele4}:
                                    self.line_errors.append('Error on line number ' + str(line_count) +
                                                            ' in Architecture File, skipping line!')
                                else:
                                    temp_list.append(ele1)
                                    temp_list.append(ele2)
                                    temp_list.append(ele3)
                                    temp_list.append(ele4)
                                    self.map['lines'].append(temp_list)
                            # Components in architecture
                            else:
                                component_count += 1
                                ele1 = element.get('type')
                                ele2 = element.get('x')
                                ele3 = element.get('y')
                                ele4 = element.get('rotation')
                                # Check that the component is defined correctly
                                if None in {ele1, ele2, ele3, ele4} or "" in {ele1, ele2, ele3, ele4}:
                                    self.component_errors.append('Error in component number ' + str(component_count) +
                                                                 ' in Architecture File, skipping component!')
                                else:
                                    temp_list.append(ele1)
                                    temp_list.append(ele2)
                                    temp_list.append(ele3)
                                    temp_list.append(float(ele4))
                                    self.map['components'].append(temp_list)

                    self.file.close()
                    return self.map
                else:
                    raise ArchitectureFileErrorException('Missing Height of Architecture Biochip!')
            else:
                raise ArchitectureFileErrorException('Missing Width of Architecture Biochip!')

        except Etree.ParseError:
            raise ArchitectureFileErrorException('Parse Error of Architecture Biochip - check syntax!')


class ArchitectureFileErrorException(Exception):
    pass
