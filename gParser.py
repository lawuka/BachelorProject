'''
Created on 2 march 2015

@author Lasse
'''

class simulatorGCode():

    def __init__(self, svgMap):

        self.svgMap = svgMap

        self.simulateGCodeList = []
        self.newLine = "\n"
        self.drillTop = "10"
        self.drillLow = "3"
        self.drillHoleTop = "10"
        self.drillHoleLow = "-1"

        self.createSimulatorGCode()

    # Function for creating GCode to CAMotics Simulator (MacOS)
    def createSimulatorGCode(self):

        # GCode options
        self.gCodeOptions()

        # Starting position
        self.starterPosition()

        # Flow channels tool
        self.flowChannelTool()

        # Flow channels
        self.flowChannels()

        # Hole tool
        self.holeTool()

        # Holes
        self.holes()

        # Ending position and finishing up
        self.moveBackToOrigin()



    def gCodeOptions(self):

        # Machine options
        self.simulateGCodeList.append("G21")
        self.simulateGCodeList.append("F250")
        self.simulateGCodeList.append("S2000")

    def starterPosition(self):

        line = "G00 X0 Y0 Z10"
        self.simulateGCodeList.append(line)
        line = "X10 Y10 Z10"
        self.simulateGCodeList.append(line)

    def flowChannelTool(self):

        self.simulateGCodeList.append("T1 M6")

    def holeTool(self):

        self.simulateGCodeList.append("T2 M6")

    def flowChannels(self):

        # Lines with fixed x-axis
        # xAxisLines = []
        # Lines with fixed y-axis
        yAxisLines = []
        '''
        Remember to add 10mm to all measures. This is only for the simulator.
        '''
        for line in self.svgMap['lines']:
            if line[0] == line[2]:
                line1 = "G1 X" + str(int(line[0])/10 + 10) + " Y" + str(int(line[1])/10 + 10) + " Z" + \
                        self.drillTop + self.newLine
                line2 = "Z" + self.drillLow + self.newLine
                line3 = "Y" + str(int(line[3])/10 + 10) + self.newLine
                line4 = "Z" + self.drillTop
                self.simulateGCodeList.append(line1 + line2 + line3 + line4)
            else:
                line1 = "G1 X" + str(int(line[0])/10 + 10) + " Y" + str(int(line[1])/10 + 10) + " Z" + \
                        self.drillTop + self.newLine
                line2 = "Z" + self.drillLow + self.newLine
                line3 = "X" + str(int(line[2])/10 + 10) + self.newLine
                line4 = "Z" + self.drillTop
                yAxisLines.append(line1 + line2 + line3 + line4)

        for element in yAxisLines:
            self.simulateGCodeList.append(element)




    def holes(self):

        '''
        Remember to add 10.5mm to all measures. This is only for the simulator.
        '''
        for hole in self.svgMap['holes']:
            line1 = "G1 X" + str(int(hole[0])/10 + 10.5) + " Y" + str(int(hole[1])/10 + 10.5) + self.newLine
            line2 = "Z" + self.drillHoleLow + self.newLine
            line3 = "Z" + self.drillHoleTop
            self.simulateGCodeList.append(line1 + line2 + line3)

    def moveBackToOrigin(self):

        line = "G0 X0 Y0"
        self.simulateGCodeList.append(line)
        self.simulateGCodeList.append("G28")
        self.simulateGCodeList.append("M30")

    def getGCode(self):

        return self.simulateGCodeList