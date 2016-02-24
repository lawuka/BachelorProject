'''
Created on 24 feb 2015

@author Lasse
'''

from gui import GUI
from parser import Parser

class createGUI():

    def __init__(self, map):
        gui = GUI(map)
        gui.showGUI()

if __name__ == '__main__':
    # Get the contents of the SVG file and parse to the parser
    file = open('svg_example.svg')
    parser = Parser(file)
    file.close()

    # Create dictionary of the flow layout
    map = parser.getMap()
    createGUI(map)




