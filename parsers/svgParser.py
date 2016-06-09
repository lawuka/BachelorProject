'''

Created 24 feb 2016

@author Lasse

'''

import xml.etree.ElementTree as etree

class svgParser():

    def __init__(self):

        self.file = None

    def parseSvg(self,fileName):

        self.file = open(fileName)
        self.tree = etree.parse(self.file)
        self.treeRoot = self.tree.getroot()
        self.map = {}

        # Canvas width and height
        self.map['width'] = self.treeRoot.get('width')
        self.map['height'] = self.treeRoot.get('height')

        self.map['components'] = []
        self.map['lines'] = []

        for elements in self.treeRoot:
            for element in elements:
                tempList = []
                # Flow lines in canvas
                if element.tag == 'line':
                    tempList.append(element.get('x1'))
                    tempList.append(element.get('y1'))
                    tempList.append(element.get('x2'))
                    tempList.append(element.get('y2'))
                    self.map['lines'].append(tempList)
                # Components in canvas
                else:
                    tempList.append(element.get('type'))
                    tempList.append(element.get('x'))
                    tempList.append(element.get('y'))
                    tempList.append(float(element.get('rotation')))
                    self.map['components'].append(tempList)

        self.file.close()
        return self.map
