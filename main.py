'''
Created on 24 feb 2015

@author Lasse

Frylunds fagteori , fagteori.dk

3 skærs

Mach3 program
Mach preprocessor
'''

from gui import GUI
from gParser import simulatorGCode
from gParser import microMillingGCode
from svgParser import svgParser

# Map of flow layer, used by several instances
global map

'''
Create the GUI for user interference
'''
class createGUI():

    def __init__(self, G):
        gui = GUI(map, G)
        gui.showGUI()

'''
Create the G-Code if the user wants it
'''
class createGCode():

    def createSimGCode(self):

        simGCode = simulatorGCode(map)
        self.gCode = simGCode.getGCode()

        self.writeToFile("SimulaterGCode.ngc")

    def createMMGCode(self):

        mmGCode = microMillingGCode(map)
        self.gCode = mmGCode.getGCode()

        self.writeToFile("MMGCode.txt")

    def writeToFile(self, filename):

        file = open(filename, "w")
        for line in self.gCode:
            file.write(line + "\n")
        file.close()

'''
Triggering the main program
'''
if __name__ == '__main__':
    # Get the contents of the SVG file and send to the parser
    file = open('svg_example.svg')
    parser = svgParser(file)
    file.close()

    # Create dictionary of the flow layout
    map = parser.getMap()

    # Show GUI
    createG = createGCode()
    createGUI(createG)




