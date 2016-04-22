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
        self.simulateGCodeList.append("; Height: " + self.svgMap['height'])
        self.simulateGCodeList.append("; Width: " + self.svgMap['width'])
        self.simulateGCodeList.append("G21")
        self.simulateGCodeList.append("G90")
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

class microMillingGCode():

    def __init__(self, svgMap):

        self.svgMap = svgMap

        self.mmGCodeList = []
        self.newLine = "\n"
        self.drillHoleLow = "Z-3"
        self.drillHigh = "Z1"

        self.createMMGCodeList()

    def createMMGCodeList(self):

        self.gCodeOptions()

        self.flowChannels()

        self.holeTool()

        self.holes()

        self.moveBackToOrigin()

    def gCodeOptions(self):

        '''
        Parenthese is comments
        '''
        self.mmGCodeList.append("(PROGRAM START)")
        '''
        1 mm drill used for flow channels
        '''
        self.mmGCodeList.append("(1MM FLOW DRILL)")
        '''
        M00 is break in Gcode, and machine pauses (Drill change or similar)
        '''
        self.mmGCodeList.append("M00")
        '''
        With a spindle controller, the spindle speed is ignored.
        self.mmGCodeList.append("S2000")
        '''
        '''
        Feed rate - how fast drill moves in X,Y or Z direction
        '''
        self.mmGCodeList.append("F250")

    def holeTool(self):

        self.mmGCodeList.append("(PAUSE FOR DRILL CHANGE)")
        self.mmGCodeList.append("M00")
        self.mmGCodeList.append("(1MM HOLE DRILL)")

    def flowChannels(self):

        yAxisLines = []

        '''
        Z coordinate expected to start at 5 which means the drill head should start at 10
        '''
        for line in self.svgMap['lines']:
            if line[0] == line[2]:
                line1 = "G01 X" + str(int(line[0])/10) + " Y" + str(int(line[1])/10) + " " + self.drillHigh + self.newLine
                line2 = "Z-0.25" + self.newLine
                line3 = "Y" + str(int(line[3])/10) + self.newLine
                line4 = "Z-0.50" + self.newLine
                line5 = "Y" + str(int(line[1])/10) + self.newLine
                line6 = "Z-0.75" + self.newLine
                line7 = "Y" + str(int(line[3])/10) + self.newLine
                line8 = "Z-1" + self.newLine
                line9 = "Y" + str(int(line[1])/10) + self.newLine
                line10 = self.drillHigh
                self.mmGCodeList.append(line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10)
            else:
                line1 = "G01 X" + str(int(line[0])/10) + " Y" + str(int(line[1])/10) + " " + self.drillHigh + self.newLine
                line2 = "Z-0.25" + self.newLine
                line3 = "X" + str(int(line[2])/10) + self.newLine
                line4 = "Z-0.50" + self.newLine
                line5 = "X" + str(int(line[0])/10) + self.newLine
                line6 = "Z-0.75" + self.newLine
                line7 = "X" + str(int(line[2])/10) + self.newLine
                line8 = "Z-1" + self.newLine
                line9 = "X" + str(int(line[0])/10) + self.newLine
                line10 = self.drillHigh
                yAxisLines.append(line1 + line2 + line3 + line4 + line5 + line6 + line7 + line8 + line9 + line10)

        for element in yAxisLines:
            self.mmGCodeList.append(element)

    def holes(self):
        '''
         Remember to add 0.5 to X and Y coordinate, to locate center of hole, in flow channel.
        '''
        for hole in self.svgMap['holes']:
            line1 = "G1 X" + str(int(hole[0])/10 + 0.5) + " Y" + str(int(hole[1])/10 + 0.5) + self.newLine
            line2 = self.drillHoleLow + self.newLine
            line3 = self.drillHigh
            self.mmGCodeList.append(line1 + line2 + line3)


    def moveBackToOrigin(self):

        self.mmGCodeList.append("X0.0 Y0.0")
        self.mmGCodeList.append("M30")
        self.mmGCodeList.append("(DONE DRILLING)")

    def getGCode(self):

        return self.mmGCodeList