'''

Created 24 feb 2016

@author Lasse

'''

import xml.etree.ElementTree as Etree


class SVGParser:

    def __init__(self):

        self.file = None
        self.tree = None
        self.treeRoot = None
        self.map = None
        self.lineErrors = None
        self.componentErrors = None

    def parse_svg(self, file_name):

        self.file = open(file_name)
        self.lineErrors = []
        self.componentErrors = []
        try:
            self.tree = Etree.parse(self.file)
            self.treeRoot = self.tree.getroot()
            self.map = {}

            # Canvas width and height
            self.map['width'] = self.treeRoot.find('size').get('width')
            if self.map['width'] not in {None, ""}:
                self.map['height'] = self.treeRoot.find('size').get('height')
                if self.map['height'] not in {None, ""} :

                    self.map['components'] = []
                    self.map['lines'] = []

                    lineCount = 0
                    componentCount = 0
                    for elements in self.treeRoot:
                        for element in elements:
                            temp_list = []
                            # Flow lines in canvas
                            if element.tag == 'line':
                                lineCount += 1
                                ele1 = element.get('x1')
                                ele2 = element.get('y1')
                                ele3 = element.get('x2')
                                ele4 = element.get('y2')
                                if None in {ele1, ele2, ele3, ele4} or "" in {ele1, ele2, ele3, ele4}:
                                    self.lineErrors.append('Error on line number ' + str(lineCount) +
                                                           ' in SVG File, skipping line!')
                                else:
                                    temp_list.append(ele1)
                                    temp_list.append(ele2)
                                    temp_list.append(ele3)
                                    temp_list.append(ele4)
                                    self.map['lines'].append(temp_list)
                            # Components in canvas
                            else:
                                componentCount += 1
                                ele1 = element.get('type')
                                ele2 = element.get('x')
                                ele3 = element.get('y')
                                ele4 = element.get('rotation')
                                if None in {ele1, ele2, ele3, ele4} or "" in {ele1, ele2, ele3, ele4}:
                                    self.componentErrors.append('Error in component number ' + str(componentCount) +
                                                                ' in SVG File, skipping component!')
                                else:
                                    temp_list.append(ele1)
                                    temp_list.append(ele2)
                                    temp_list.append(ele3)
                                    temp_list.append(float(ele4))
                                    self.map['components'].append(temp_list)

                    self.file.close()
                    return self.map
                else:
                    raise SVGFileErrorException('Missing Height of SVG Chip!')
            else:
                raise SVGFileErrorException('Missing Width of SVG Chip!')

        except Etree.ParseError:
            raise SVGFileErrorException('Parse Error of SVG Chip - check syntax!')


class SVGFileErrorException(Exception):
    pass
