'''

Created 24 feb 2016

@author Lasse

'''

import xml.etree.ElementTree as etree

class Parser():

    def __init__(self,file):

        self.map = {}
        self.file = file
        self.tree = etree.parse(self.file)
        self.treeRoot = self.tree.getroot()

        # Canvas width and height
        self.map['width'] = self.treeRoot.get('width')
        self.map['height'] = self.treeRoot.get('height')

        self.map['lines'] = []
        self.map['components'] = []
        self.map['holes'] = []

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
                # Holes for input output of fluid / air
                elif element.tag == 'hole':
                    tempList.append(element.get('x'))
                    tempList.append(element.get('y'))
                    self.map['holes'].append(tempList)
                # Components in canvas
                else:
                    tempList.append(element.get('id'))
                    tempList.append(element.get('x'))
                    tempList.append(element.get('y'))
                    self.map['components'].append(tempList)

    def getMap(self):

        return self.map
