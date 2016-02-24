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

        # Flow lines in canvas
        self.map['lines'] = []
        tempVal = 0
        for lines in self.treeRoot:
            for line in lines:
                tempList = []
                tempList.append(line.get('x1'))
                tempList.append(line.get('y1'))
                tempList.append(line.get('x2'))
                tempList.append(line.get('y2'))
                self.map['lines'].append(tempList)


    def getMap(self):

        return self.map

class Line():

    tag = 'line'

    def __init__(self, element):

        self.P1 = [element.get('x1'),element.get('y1')]
        self.P2 = [element.get('x2'),element.get('y2')]

    def __repr__(self):

        return {'P1', self.P1 ,
                'P2', self.P2}



