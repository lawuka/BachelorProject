'''
Created on 2 march 2015

@author Lasse
'''
from math import ceil, cos, pi, sin, radians, fabs
from model.mathFunctions import rotate_coordinate

class simulatorGCode():

    def __init__(self):

        self.svgMap = None
        self.library = None
        self.conf = None
        self.simulateGCodeList = None

        self.newLine = "\n"
        self.drillTop = "10"
        self.drillLow = "1"
        self.drillHoleTop = "10"
        self.drillHoleLow = "-3"


    def createSimulatorGCodeList(self, svgMap, library, conf):

        self.svgMap = svgMap
        self.library = library
        self.conf = conf
        self.simulateGCodeList = []

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

        return self.simulateGCodeList

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

    def getSimulatorGCode(self):

        return self.simulateGCodeList

class microMillingFlowGCode():

    def __init__(self):

        self.svgMap = None
        self.library = None
        self.conf = None
        self.mmGCodeList = None
        self.flowHoleList = None

    def createMMGCodeList(self, svgMap, library, conf):

        self.svgMap = svgMap
        self.library = library
        self.conf = conf
        self.mmGCodeList = []
        self.flowHoleList = []

        # Current config
        self.drillFlowDepth = self.conf['drillOptions']['flow']['depth']
        self.drillHoleDepth = self.conf['drillOptions']['hole']['depth']
        self.drillSize = self.conf['drillOptions']['drillSize']

        # Calculate number of drilling in one flow channel
        if ((float(self.drillFlowDepth) * -1.0) / (float(self.drillSize) / 4.0)) <= 1.0 :
            self.repeat = 1
        else :
            self.repeat = int(ceil((float(self.drillFlowDepth) * -1.0) / (float(self.drillSize) / 4.0)))

        self.gCodeOptions()

        self.components()

        self.flowChannels()

        self.flowHoles()

        self.moveBackToOrigin()

        return self.mmGCodeList

    def gCodeOptions(self):

        '''
        Parenthese in GCode is comments
        '''
        self.mmGCodeList.append("(PROGRAM START)")
        '''
        Drill used for flow channels
        '''
        self.mmGCodeList.append("(" + self.drillSize +"MM FLOW DRILL)")
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

    def components(self):

        if self.svgMap['components']:
            # Start going through each component in 'components'
            for component in self.svgMap['components']:
                if component[0] in self.library:
                    componentX = float(component[1]) * float(self.drillSize)
                    componentY = float(component[2]) * float(self.drillSize)
                    componentWidth = float(self.library[component[0]]['Size'].find('Width').text) * float(self.drillSize)
                    componentHeight = float(self.library[component[0]]['Size'].find('Height').text) * float(self.drillSize)
                    componentActualPositionX = componentX - componentWidth/2
                    componentActualPositionY = componentY - componentHeight/2

                    for iComponent in self.library[component[0]]['Internal']:
                        if iComponent.tag == 'FlowLine':
                            self.internalFlowChannel(iComponent,
                                                     [componentActualPositionX],
                                                     [componentActualPositionY],
                                                     [component[3] % 360],
                                                     [componentWidth],
                                                     [componentHeight])
                        elif iComponent.tag == 'FlowCircle':
                            self.internalFlowCircle(iComponent,
                                                    [componentActualPositionX],
                                                    [componentActualPositionY],
                                                    [component[3] % 360],
                                                    [componentWidth],
                                                    [componentHeight])
                        elif iComponent.tag == "FlowHole":
                            self.internalFlowHole(iComponent,
                                                  [componentActualPositionX],
                                                  [componentActualPositionY],
                                                  [component[3] % 360],
                                                  [componentWidth],
                                                  [componentHeight])
                        else:
                            self.internalComponent(iComponent,
                                                [componentActualPositionX],
                                                [componentActualPositionY],
                                                [component[3] % 360],
                                                [componentWidth],
                                                [componentHeight])

                            # If internal component is another "not" basic component, repeat
                            #newComponentX = float(internalComponent.find('X').text) * float(self.drillSize) + componentActualPositionX
                            #newComponentY = float(internalComponent.find('Y').text) * float(self.drillSize) + componentActualPositionY
                            #newComponentRotation = float(internalComponent.find('Rotation').text)
                else:
                    print("Component \"" + component[0] + "\" not found in library - skipping!")

    def flowChannels(self):

        if self.svgMap['lines']:
            # Start going through each line in 'lines'
            for line in self.svgMap['lines']:
                self.flowChannelGCode(float(line[0]) * float(self.drillSize),
                                      float(line[1]) * float(self.drillSize),
                                      float(line[2]) * float(self.drillSize),
                                      float(line[3]) * float(self.drillSize))

    def flowHoles(self):

        '''
        Pausing the drilling, since drill for drilling all the way through is different than flow channels
        '''
        self.mmGCodeList.append("(PAUSE FOR DRILL CHANGE)")
        self.mmGCodeList.append("M00")
        self.mmGCodeList.append("(" + self.drillSize + "MM HOLE DRILL)")

        for flowHole in self.flowHoleList:
            self.flowHoleGCode(flowHole[0],flowHole[1])

    def moveBackToOrigin(self):

        self.mmGCodeList.append("X0.0 Y0.0")
        self.mmGCodeList.append("M30")
        self.mmGCodeList.append("(DONE DRILLING)")

    def internalComponent(self, component, componentXList, componentYList,
                          componentRotationList, componentWidthList, componentHeightList):
        if component.tag in self.library:
            componentX = float(component.find('X').text) * float(self.drillSize)
            componentY = float(component.find('Y').text) * float(self.drillSize)
            componentWidth = float(self.library[component.tag]['Size'].find('Width').text) * float(self.drillSize)
            componentHeight = float(self.library[component.tag]['Size'].find('Height').text) * float(self.drillSize)
            componentXList.append(componentX - componentWidth/2)
            componentYList.append(componentY - componentHeight/2)
            componentRotationList.append(float(component.find('Rotation').text) % 360.0)
            componentWidthList.append(componentWidth)
            componentHeightList.append(componentHeight)

            for iComponent in self.library[component.tag]['Internal']:
               if iComponent.tag == 'FlowLine':
                    self.internalFlowChannel(iComponent,
                                             componentXList,
                                             componentYList,
                                             componentRotationList,
                                             componentWidthList,
                                             componentHeightList)
               elif iComponent.tag == 'FlowCircle':
                    self.internalFlowCircle(iComponent,
                                            componentXList,
                                            componentYList,
                                            componentRotationList,
                                            componentWidthList,
                                            componentHeightList)
               elif iComponent.tag == 'FlowHole':
                   self.internalFlowHole(iComponent,
                                         componentXList,
                                         componentYList,
                                         componentRotationList,
                                         componentWidthList,
                                         componentHeightList)
               else:
                    self.internalComponent(iComponent,
                                           componentXList,
                                           componentYList,
                                           componentRotationList,
                                           componentWidthList,
                                           componentHeightList)
                    componentXList.pop()
                    componentYList.pop()
                    componentRotationList.pop()
                    componentWidthList.pop()
                    componentHeightList.pop()
        else:
            print("Component \"" + component.tag + "\" not found in library - skipping!")

    def internalFlowChannel(self, flowChannel, componentXList, componentYList, componentRotationList,
                            componentWidthList, componentHeightList):
        flowStartX = float(flowChannel.find('Start').find('X').text) * float(self.drillSize)# + componentActualPositionX
        flowStartY = float(flowChannel.find('Start').find('Y').text) * float(self.drillSize)# + componentActualPositionY
        flowEndX = float(flowChannel.find('End').find('X').text) * float(self.drillSize)# + componentActualPositionX
        flowEndY = float(flowChannel.find('End').find('Y').text) * float(self.drillSize)# + componentActualPositionY

        for i in range(len(componentXList)-1,-1,-1):
            if componentRotationList[i] != 0.0:
                tempFlowStartX = rotate_coordinate(flowStartX - componentWidthList[i]/2,
                                                       flowStartY - componentHeightList[i]/2,
                                                       componentRotationList[i],
                                                       'x')
                tempFlowStartY = rotate_coordinate(flowStartX - componentWidthList[i]/2,
                                                       flowStartY - componentHeightList[i]/2,
                                                       componentRotationList[i],
                                                       'y')
                tempFlowEndX = rotate_coordinate(flowEndX - componentWidthList[i]/2,
                                                     flowEndY - componentHeightList[i]/2,
                                                     componentRotationList[i],
                                                     'x')
                tempFlowEndY = rotate_coordinate(flowEndX - componentWidthList[i]/2,
                                                     flowEndY - componentHeightList[i]/2,
                                                     componentRotationList[i],
                                                     'y')

                flowStartX = tempFlowStartX + componentXList[i] + componentWidthList[i]/2
                flowStartY = tempFlowStartY + componentYList[i] + componentHeightList[i]/2
                flowEndX = tempFlowEndX + componentXList[i] + componentWidthList[i]/2
                flowEndY = tempFlowEndY + componentYList[i] + componentHeightList[i]/2
            else:
                flowStartX += componentXList[i]
                flowStartY += componentYList[i]
                flowEndX += componentXList[i]
                flowEndY += componentYList[i]

        self.flowChannelGCode(flowStartX,flowStartY,flowEndX,flowEndY)

    def internalFlowCircle(self, flowCircle, componentXList, componentYList, componentRotationList,
                           componentWidthList, componentHeightList):
        flowCircleCenterX = float(flowCircle.find('Center').find('X').text) * float(self.drillSize)# + componentActualPositionX
        flowCircleCenterY = float(flowCircle.find('Center').find('Y').text) * float(self.drillSize)# + componentActualPositionY

        totalRotation = 0

        for i in range(len(componentXList)-1,-1,-1):
            if componentRotationList[i] != 0.0:
                tempCircleCenterX = rotate_coordinate(flowCircleCenterX - componentWidthList[i]/2,
                                                      flowCircleCenterY - componentHeightList[i]/2,
                                                      componentRotationList[i],
                                                      'x')
                tempCircleCenterY = rotate_coordinate(flowCircleCenterX - componentWidthList[i]/2,
                                                      flowCircleCenterY - componentHeightList[i]/2,
                                                      componentRotationList[i],
                                                      'y')
                flowCircleCenterX = tempCircleCenterX + componentXList[i] + componentWidthList[i]/2
                flowCircleCenterY = tempCircleCenterY + componentYList[i] + componentHeightList[i]/2
            else:
                flowCircleCenterX += componentXList[i]
                flowCircleCenterY += componentYList[i]

            totalRotation += componentRotationList[i]

        flowCircleRadius = float(flowCircle.find('Radius').text) * float(self.drillSize)

        flowCircleStartX = flowCircleCenterX
        flowCircleStartY = flowCircleCenterY

        angleList = sorted(list(flowCircle.find('Valves')),key=lambda elem: float(elem.text)%360.0)
        valveLengthAngle = (360 * 2 * float(self.drillSize))/(2 * flowCircleRadius * pi)

        if len(angleList) == 0:
            self.completeCircleGCode(str(flowCircleStartX + flowCircleRadius),
                                     str(flowCircleStartY),
                                     flowCircleRadius)
        elif len(angleList) == 1:
            self.oneAngleCircleGCode(str(flowCircleCenterX + flowCircleRadius),
                                     str(flowCircleCenterY),
                                     flowCircleRadius,
                                     flowCircleStartX, flowCircleStartY,
                                     valveLengthAngle/2, (float(angleList[0].text)+totalRotation)%360.0)
        else:
            if totalRotation % 360 == 90:
                flowCircleStartY += flowCircleRadius
            elif totalRotation % 360 == 180:
                flowCircleStartX -= flowCircleRadius
            elif totalRotation % 360 == 270:
                flowCircleStartY -= flowCircleRadius
            else:
                flowCircleStartX += flowCircleRadius

            for i in range(0,len(angleList)):
                if i == len(angleList)-1:
                    flowStartX = str(cos(radians(float(angleList[i-1].text)+valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterX)
                    flowStartY = str(sin(radians(float(angleList[i-1].text)+valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterY)
                    flowEndX = str(cos(radians(float(angleList[i].text)-valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterX)
                    flowEndY = str(sin(radians(float(angleList[i].text)-valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterY)
                    self.flowCircleGCode(flowStartX, flowStartY, flowEndX, flowEndY, flowCircleRadius)
                    flowStartX = str(cos(radians(float(angleList[i].text)+valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterX)
                    flowStartY = str(sin(radians(float(angleList[i].text)+valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterY)
                    self.flowCircleGCode(flowStartX, flowStartY, str(flowCircleStartX), str(flowCircleStartY),
                                         -flowCircleRadius if float(angleList[i].text) <= 180 else flowCircleRadius)
                elif i == 0:
                    flowEndX = str(cos(radians(float(angleList[i].text)-valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterX)
                    flowEndY = str(sin(radians(float(angleList[i].text)-valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterY)
                    self.flowCircleGCode(str(flowCircleStartX),
                                         str(flowCircleStartY),
                                         flowEndX,
                                         flowEndY,
                                         flowCircleRadius)
                else:
                    flowStartX = str(cos(radians(float(angleList[i-1].text)+valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterX)
                    flowStartY = str(sin(radians(float(angleList[i-1].text)+valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterY)
                    flowEndX = str(cos(radians(float(angleList[i].text)-valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterX)
                    flowEndY = str(sin(radians(float(angleList[i].text)-valveLengthAngle/2+totalRotation%360.0)) * flowCircleRadius + flowCircleCenterY)
                    self.flowCircleGCode(flowStartX, flowStartY, flowEndX, flowEndY, flowCircleRadius)

    def internalFlowHole(self, flowHole, componentXList, componentYList, componentRotationList,
                           componentWidthList, componentHeightList):

        flowHoleCenterX = float(flowHole.find('Center').find('X').text)
        flowHoleCenterY = float(flowHole.find('Center').find('Y').text)

        for i in range(len(componentXList)-1,-1,-1):
            if componentRotationList[i] != 0.0:
                tempHoleCenterX = rotate_coordinate(flowHoleCenterX - componentWidthList[i]/2,
                                                    flowHoleCenterY - componentHeightList[i]/2,
                                                    componentRotationList[i],
                                                    'x')
                tempHoleCenterY = rotate_coordinate(flowHoleCenterX - componentWidthList[i]/2,
                                                    flowHoleCenterY - componentHeightList[i]/2,
                                                    componentRotationList[i],
                                                    'y')

                flowHoleCenterX = tempHoleCenterX + componentXList[i] + componentWidthList[i]/2
                flowHoleCenterY = tempHoleCenterY + componentYList[i] + componentHeightList[i]/2
            else:
                flowHoleCenterX += componentXList[i]
                flowHoleCenterY += componentYList[i]

        self.flowHoleList.append([flowHoleCenterX, flowHoleCenterY])


    def flowChannelGCode(self, flowStartX, flowStartY, flowEndX, flowEndY):

        currentDrillLevel = 0.0
        if flowStartX == flowEndX:
            self.mmGCodeList.append("G01 X" + str(flowStartX) + " Y" + str(flowStartY) + " Z" + self.drillSize)
            for i in range(0,self.repeat) :
                currentDrillLevel -= (float(self.drillSize) / 4.0)
                if currentDrillLevel < float(self.drillFlowDepth):
                    currentDrillLevel = float(self.drillFlowDepth)
                self.mmGCodeList.append("Z" + str(currentDrillLevel))
                if i % 2 == 0:
                    self.mmGCodeList.append("Y" + str(flowEndY))
                else :
                    self.mmGCodeList.append("Y" + str(flowStartY))
            self.mmGCodeList.append("Z" + self.drillSize)
        else:
            self.mmGCodeList.append("G01 X" + str(flowStartX) + " Y" + str(flowStartY) + " Z" + self.drillSize)
            for i in range(0,self.repeat) :
                currentDrillLevel -= (float(self.drillSize) / 4.0)
                if currentDrillLevel < float(self.drillFlowDepth):
                    currentDrillLevel = float(self.drillFlowDepth)
                self.mmGCodeList.append("Z" + str(currentDrillLevel))
                if i % 2 == 0:
                    self.mmGCodeList.append("X" + str(flowEndX))
                else :
                    self.mmGCodeList.append("X" + str(flowStartX))
            self.mmGCodeList.append("Z" + self.drillSize)

    def flowCircleGCode(self, flowStartX, flowStartY, flowEndX, flowEndY, flowCircleRadius):

        currentDrillLevel = 0.0

        self.mmGCodeList.append("G01 X" + flowStartX + " Y" + flowStartY + " Z" + self.drillSize)

        for i in range(0, self.repeat):
            currentDrillLevel -= (float(self.drillSize) / 4.0)
            if currentDrillLevel < float(self.drillFlowDepth):
                currentDrillLevel = float(self.drillFlowDepth)
            self.mmGCodeList.append("G01 Z" + str(currentDrillLevel))
            if i % 2 == 0:
                self.mmGCodeList.append("G03 X" + flowEndX + " Y" + flowEndY + " R" + str(flowCircleRadius))
            else:
                self.mmGCodeList.append("G02 X" + flowStartX + " Y" + flowStartY + " R" + str(flowCircleRadius))
        self.mmGCodeList.append("G01 Z" + self.drillSize)

    def completeCircleGCode(self, startX, startY, flowCircleRadius):

        currentDrillLevel = 0.0

        self.mmGCodeList.append("G01 X" + startX + " Y" + startY + " Z" + self.drillSize)

        for i in range(0, self.repeat):
            currentDrillLevel -= (float(self.drillSize) / 4.0)
            if currentDrillLevel < float(self.drillFlowDepth):
                currentDrillLevel = float(self.drillFlowDepth)
            self.mmGCodeList.append("G01 Z" + str(currentDrillLevel))
            if i % 2 == 0:
                self.mmGCodeList.append("G03 I-" + str(flowCircleRadius))
            else:
                self.mmGCodeList.append("G02 I-" + str(flowCircleRadius))
        self.mmGCodeList.append("G01 Z" + self.drillSize)

    def oneAngleCircleGCode(self, flowCircleCenterX,
                                  flowCircleCenterY,
                                  flowCircleRadius,
                                  flowCircleStartX,
                                  flowCircleStartY,
                                  valveLengthAngle,
                                  angle):

        print(angle)

        if angle != 0:
            flowEndX = str(cos(radians(angle-valveLengthAngle)) * flowCircleRadius + flowCircleCenterX)
            flowEndY = str(sin(radians(angle-valveLengthAngle)) * flowCircleRadius + flowCircleCenterY)
            self.flowCircleGCode(flowCircleStartX, flowCircleStartY, flowEndX, flowEndY,
                                 flowCircleRadius if angle <= 180.0 else -flowCircleRadius)
            flowStartX = str(cos(radians(angle+(valveLengthAngle))) * flowCircleRadius + flowCircleCenterX)
            flowStartY = str(sin(radians(angle+(valveLengthAngle))) * flowCircleRadius + flowCircleCenterY)
            self.flowCircleGCode(flowStartX, flowStartY, flowCircleStartX, flowCircleStartY,
                                 -flowCircleRadius if angle <= 180.0 else flowCircleRadius)
        else:
            flowStartX = str(cos(radians(valveLengthAngle)) * flowCircleRadius + flowCircleCenterX)
            flowStartY = str(sin(radians(valveLengthAngle)) * flowCircleRadius + flowCircleCenterY)
            flowEndX = str(cos(radians(360-(valveLengthAngle))) * flowCircleRadius + flowCircleCenterX)
            flowEndY = str(sin(radians(360-(valveLengthAngle))) * flowCircleRadius + flowCircleCenterY)
            self.flowCircleGCode(flowStartX, flowStartY, flowEndX, flowEndY, -flowCircleRadius)

    def flowHoleGCode(self, flowHoleCenterX, flowHoleCenterY):

        self.mmGCodeList.append("G1 X" + str(flowHoleCenterX)
                                +" Y" + str(flowHoleCenterY))
        self.mmGCodeList.append("Z" + self.drillHoleDepth)
        self.mmGCodeList.append("Z" + self.drillSize)

class microMillingControlGCode():

    def __init__(self):

        self.svgMap = None
        self.library = None
        self.conf = None
        self.mmGCodeList = None
        self.controlMap = None
        self.scale = None

    def createMMGCodeList(self, svgMap, library, conf):

        self.svgMap = svgMap
        self.library = library
        self.conf = conf
        self.mmGCodeList = []
        self.controlMap = []

        # Current config
        self.drillFlowDepth = self.conf['drillOptions']['flow']['depth']
        self.drillHoleDepth = self.conf['drillOptions']['hole']['depth']
        self.drillSize = self.conf['drillOptions']['drillSize']
        self.valveWidth = self.conf['valveOptions']['width']
        self.valveHeight = self.conf['valveOptions']['height']

        # Calculate number of drilling in one flow channel
        if ((float(self.drillFlowDepth) * -1.0) / (float(self.drillSize) / 4.0)) <= 1.0 :
            self.repeat = 1
        else :
            self.repeat = int(ceil((float(self.drillFlowDepth) * -1.0) / (float(self.drillSize) / 4.0)))

        # Scale for scaling according to drillsize
        self.scale = float(self.drillSize)

        # Use chip size, to modify control layer so it fits correctly on top
        self.svgMapWidth = float(self.svgMap['width']) * self.scale
        self.svgMapHeight = float(self.svgMap['height']) * self.scale

        # Create GCode List
        self.gCodeOptions()

        self.fetchValves()

        self.valves()

        self.valveHolesGCode()

        self.moveBackToOrigin()

        return self.mmGCodeList

    def gCodeOptions(self):

        '''
        Parenthese in GCode is comments
        '''
        self.mmGCodeList.append("(PROGRAM START)")
        '''
        Drill used for flow channels
        '''
        self.mmGCodeList.append("(" + self.drillSize +"MM FLOW DRILL)")
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

    def fetchValves(self):

        if self.svgMap['components']:
            # Start going through each component in 'components'
            for component in self.svgMap['components']:
                if component[0] in self.library:
                    componentX = float(component[1]) * self.scale
                    componentY = float(component[2]) * self.scale
                    componentWidth = float(self.library[component[0]]['Size'].find('Width').text) * self.scale
                    componentHeight = float(self.library[component[0]]['Size'].find('Height').text) * self.scale
                    componentActualPositionX = componentX - componentWidth/2
                    componentActualPositionY = componentY - componentHeight/2

                    controlValves = self.library[component[0]]['Control']
                    if controlValves != None and len(controlValves) != 0:
                        self.appendControlValves(controlValves, [componentActualPositionX], [componentActualPositionY],
                                                 [component[3] % 360],
                                                 [componentWidth],
                                                 [componentHeight])

                    for iComponent in self.library[component[0]]['Internal']:
                        if iComponent.tag in {'FlowLine', 'FlowHole'}:
                            pass
                        elif iComponent.tag == 'FlowCircle':
                            self.internalFlowCircle(iComponent,
                                                    [componentActualPositionX],
                                                    [componentActualPositionY],
                                                    [component[3] % 360],
                                                    [componentWidth],
                                                    [componentHeight])
                        else:
                            self.internalComponent(iComponent,
                                                [componentActualPositionX],
                                                [componentActualPositionY],
                                                [component[3] % 360],
                                                [componentWidth],
                                                [componentHeight])
                else:
                    print("Component \"" + component[0] + "\" not found in library - skipping!")

    def moveBackToOrigin(self):

        self.mmGCodeList.append("X0.0 Y0.0")
        self.mmGCodeList.append("M30")
        self.mmGCodeList.append("(DONE DRILLING)")

    def internalComponent(self, component, componentXList, componentYList,
                          componentRotationList, componentWidthList, componentHeightList):
        if component.tag in self.library:
            componentX = float(component.find('X').text) * self.scale
            componentY = float(component.find('Y').text) * self.scale
            componentWidth = float(self.library[component.tag]['Size'].find('Width').text) * self.scale
            componentHeight = float(self.library[component.tag]['Size'].find('Height').text) * self.scale
            componentXList.append(componentX - componentWidth/2)
            componentYList.append(componentY - componentHeight/2)
            componentRotationList.append(float(component.find('Rotation').text) % 360.0)
            componentWidthList.append(componentWidth)
            componentHeightList.append(componentHeight)

            controlValves = self.library[component.tag]['Control']
            if controlValves != None and len(controlValves) != 0:
                self.appendControlValves(controlValves, componentXList, componentYList,
                                         componentRotationList, componentWidthList, componentHeightList)

            for iComponent in self.library[component.tag]['Internal']:
                if iComponent.tag in {'FlowLine', 'FlowHole'}:
                    pass
                elif iComponent.tag == 'FlowCircle':
                    self.internalFlowCircle(iComponent,
                                            componentXList,
                                            componentYList,
                                            componentRotationList,
                                            componentWidthList,
                                            componentHeightList)
                else:
                    self.internalComponent(iComponent,
                                           componentXList,
                                           componentYList,
                                           componentRotationList,
                                           componentWidthList,
                                           componentHeightList)
                    if len(componentXList) != 0:
                        componentXList.pop()
                        componentYList.pop()
                        componentRotationList.pop()
                        componentWidthList.pop()
                        componentHeightList.pop()
        else:
            print("Component \"" + component.tag + "\" not found in library - skipping!")

    def appendControlValves(self, valveList, componentXList, componentYList,
                            componentRotationList, componentWidthList, componentHeightList):

        for valve in valveList:
            valveCenterX = float(valve.find('X').text) * self.scale
            valveCenterY = float(valve.find('Y').text) * self.scale
            valveRotation = float(valve.find('Rotation').text)

            totalRotation = 0.0

            for i in range(len(componentXList)-1,-1,-1):
                if componentRotationList[i] != 0.0:
                    tempValveCenterX = rotate_coordinate(valveCenterX - componentWidthList[i]/2,
                                                         valveCenterY - componentHeightList[i]/2,
                                                         componentRotationList[i],
                                                         'x')
                    tempValveCenterY = rotate_coordinate(valveCenterX - componentWidthList[i]/2,
                                                         valveCenterY - componentHeightList[i]/2,
                                                         componentRotationList[i],
                                                         'y')
                    valveCenterX = tempValveCenterX + componentXList[i] + componentWidthList[i]/2
                    valveCenterY = tempValveCenterY + componentYList[i] + componentHeightList[i]/2
                else:
                    valveCenterX += componentXList[i]
                    valveCenterY += componentYList[i]

                totalRotation += componentRotationList[i]


            xyxy = [self.svgMapWidth - valveCenterX,
                    valveCenterY,
                    (valveRotation - totalRotation)%360.0,
                    None]

            self.controlMap.append(xyxy)

    def internalFlowCircle(self, flowCircle, componentXList, componentYList, componentRotationList,
                           componentWidthList, componentHeightList):
        flowCircleCenterX = float(flowCircle.find('Center').find('X').text) * self.scale
        flowCircleCenterY = float(flowCircle.find('Center').find('Y').text) * self.scale

        totalRotation = 0

        for i in range(len(componentXList)-1,-1,-1):
            if componentRotationList[i] != 0.0:
                tempCircleCenterX = rotate_coordinate(flowCircleCenterX - componentWidthList[i]/2,
                                                      flowCircleCenterY - componentHeightList[i]/2,
                                                      componentRotationList[i],
                                                      'x')
                tempCircleCenterY = rotate_coordinate(flowCircleCenterX - componentWidthList[i]/2,
                                                      flowCircleCenterY - componentHeightList[i]/2,
                                                      componentRotationList[i],
                                                      'y')
                flowCircleCenterX = tempCircleCenterX + componentXList[i] + componentWidthList[i]/2
                flowCircleCenterY = tempCircleCenterY + componentYList[i] + componentHeightList[i]/2
            else:
                flowCircleCenterX += componentXList[i]
                flowCircleCenterY += componentYList[i]

            totalRotation += componentRotationList[i]

        flowCircleRadius = float(flowCircle.find('Radius').text) * self.scale

        angleList = sorted(list(flowCircle.find('Valves')),key=lambda elem: float(elem.text)%360.0)

        for valve in angleList:
            valveDegree = float(valve.text)
            valveCenterX = flowCircleCenterX + cos(radians(valveDegree+totalRotation%360.0)) * flowCircleRadius
            valveCenterY = flowCircleCenterY + sin(radians(valveDegree+totalRotation%360.0)) * flowCircleRadius

            xyxy = [self.svgMapWidth - valveCenterX,
                    valveCenterY,
                    None,
                    (valveDegree-totalRotation)%360.0]

            self.controlMap.append(xyxy)

    def valves(self):
        valveWidth = float(self.valveWidth) * self.scale
        valveHeight = float(self.valveHeight) * self.scale
        valveOuterR = float(2.5/6) * valveHeight * self.scale
        valveInnerR = float(1.5/6) * valveHeight * self.scale

        for valve in self.controlMap:

            x = valve[0]
            y = valve[1]
            valveRot = valve[2]
            circleRot = valve[3]

            xLeft = x + (-1.5/9) * valveWidth
            xLeftLeft = x + (-2.0/9) * valveWidth
            xRight = x + (1.5/9) * valveWidth
            xRightRight = x + (2.0/9) * valveWidth

            yTopTop = y + (2.5/6) * valveHeight
            yTopMiddle = y + (1.5/6) * valveHeight
            yTopLow = y + (0.5/6) * valveHeight
            yLowTop = y + (-0.5/6) * valveHeight
            yLowMiddle = y + (-1.5/6) * valveHeight
            yLowLow = y + (-2.5/6) * valveHeight

            xList = [xLeft, xLeftLeft,
                     xRight, xRightRight]

            yList = [yTopTop, yTopMiddle,
                     yTopLow, yLowTop,
                     yLowMiddle, yLowLow]

            if valveRot != None:
                if valveRot in {90.0, 270.0}:
                    self.valveGCode(self.getRotatedXList(x, y, xList, yList, valveRot),
                                    self.getRotatedYList(x, y, xList, yList, valveRot),
                                    90, valveOuterR, valveInnerR)

                else:
                    self.valveGCode(xList, yList, None, valveOuterR, valveInnerR)
            else:
                if circleRot in {90.0, 270.0}:
                    self.valveGCode(xList, yList, None, valveOuterR, valveInnerR)

                elif circleRot in {0.0, 180.0}:
                    self.valveGCode(self.getRotatedXList(x, y, xList, yList, circleRot),
                                    self.getRotatedYList(x, y, xList, yList, circleRot),
                                    90, valveOuterR, valveInnerR)
                else:
                    self.valveGCode(self.getRotatedXList(x, y, xList, yList, 90.0-circleRot),
                                    self.getRotatedYList(x, y, xList, yList, 90.0-circleRot),
                                    circleRot, valveOuterR, valveInnerR)

    def valveGCode(self, xList, yList, valveRotate, valveOuterR, valveInnerR):

        currentDrillLevel = 0.0

        for i in range(0, self.repeat):
            currentDrillLevel -= self.scale / 4.0
            if currentDrillLevel < float(self.drillFlowDepth):
                currentDrillLevel = float(self.drillFlowDepth)

            if valveRotate == None:
                self.mmGCodeList.append("G01 X" + str(xList[0]) +
                                        " Y" + str(yList[0]) +
                                        " Z" + self.drillSize)
                self.mmGCodeList.append("Z" + str(currentDrillLevel))
                self.mmGCodeList.append("G01 X" + str(xList[2]) +
                                        " Y" + str(yList[0]))
                self.mmGCodeList.append("G02 X" + str(xList[2]) +
                                        " Y" + str(yList[5]) +
                                        " R" + str(valveOuterR))
                self.mmGCodeList.append("G01 X" + str(xList[0]) +
                                        " Y" + str(yList[5]))
                self.mmGCodeList.append("G02 X" + str(xList[0]) +
                                        " Y" + str(yList[0]) +
                                        " R" + str(valveOuterR))
                self.mmGCodeList.append("G01 X" + str(xList[0]) +
                                        " Y" + str(yList[1]))
                self.mmGCodeList.append("G01 X" + str(xList[2]) +
                                        " Y" + str(yList[1]))
                self.mmGCodeList.append("G02 X" + str(xList[2]) +
                                        " Y" + str(yList[4]) +
                                        " R" + str(valveInnerR))
                self.mmGCodeList.append("G01 X" + str(xList[0]) +
                                        " Y" + str(yList[4]))

                self.mmGCodeList.append("G02 X" + str(xList[0]) +
                                        " Y" + str(yList[1]) +
                                        " R" + str(valveInnerR))

                self.mmGCodeList.append("G01 X" + str(xList[1]) +
                                        " Y" + str(yList[2]))
                self.mmGCodeList.append("G01 X" + str(xList[3]) +
                                        " Y" + str(yList[2]))
                self.mmGCodeList.append("G01 X" + str(xList[3]) +
                                        " Y" + str(yList[3]))
                self.mmGCodeList.append("G01 X" + str(xList[1]) +
                                        " Y" + str(yList[3]))
                self.mmGCodeList.append("Z" + self.drillSize)
            else:
                self.mmGCodeList.append("G01 X" + str(xList[0]) +
                                        " Y" + str(yList[0]) +
                                        " Z" + self.drillSize)
                self.mmGCodeList.append("Z" + str(currentDrillLevel))
                self.mmGCodeList.append("G01 X" + str(xList[1]) +
                                        " Y" + str(yList[1]))
                self.mmGCodeList.append("G02 X" + str(xList[2]) +
                                        " Y" + str(yList[2]) +
                                        " R" + str(valveOuterR))
                self.mmGCodeList.append("G01 X" + str(xList[3]) +
                                        " Y" + str(yList[3]))
                self.mmGCodeList.append("G02 X" + str(xList[0]) +
                                        " Y" + str(yList[0]) +
                                        " R" + str(valveOuterR))
                self.mmGCodeList.append("G01 X" + str(xList[4]) +
                                        " Y" + str(yList[4]))
                self.mmGCodeList.append("G01 X" + str(xList[5]) +
                                        " Y" + str(yList[5]))
                self.mmGCodeList.append("G02 X" + str(xList[6]) +
                                        " Y" + str(yList[6]) +
                                        " R" + str(valveInnerR))
                self.mmGCodeList.append("G01 X" + str(xList[7]) +
                                        " Y" + str(yList[7]))

                self.mmGCodeList.append("G02 X" + str(xList[4]) +
                                        " Y" + str(yList[4]) +
                                        " R" + str(valveInnerR))

                self.mmGCodeList.append("G01 X" + str(xList[8]) +
                                        " Y" + str(yList[8]))
                self.mmGCodeList.append("G01 X" + str(xList[9]) +
                                        " Y" + str(yList[9]))
                self.mmGCodeList.append("G01 X" + str(xList[10]) +
                                        " Y" + str(yList[10]))
                self.mmGCodeList.append("G01 X" + str(xList[11]) +
                                        " Y" + str(yList[11]))
                self.mmGCodeList.append("Z" + self.drillSize)

    def getRotatedXList(self, x, y, xList, yList, valveRot):

        rotatedXList = [rotate_coordinate(xList[0] - x, yList[0] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[2] - x, yList[0] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[2] - x, yList[5] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[0] - x, yList[5] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[0] - x, yList[1] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[2] - x, yList[1] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[2] - x, yList[4] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[0] - x, yList[4] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[1] - x, yList[2] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[3] - x, yList[2] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[3] - x, yList[3] - y, valveRot, 'x') + x,
                        rotate_coordinate(xList[1] - x, yList[3] - y, valveRot, 'x') + x]
        return rotatedXList

    def getRotatedYList(self, x, y, xList, yList, valveRot):

        rotatedYList = [rotate_coordinate(xList[0] - x, yList[0] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[2] - x, yList[0] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[2] - x, yList[5] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[0] - x, yList[5] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[0] - x, yList[1] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[2] - x, yList[1] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[2] - x, yList[4] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[0] - x, yList[4] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[1] - x, yList[2] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[3] - x, yList[2] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[3] - x, yList[3] - y, valveRot, 'y') + y,
                        rotate_coordinate(xList[1] - x, yList[3] - y, valveRot, 'y') + y]
        return rotatedYList

    def valveHolesGCode(self):

        self.mmGCodeList.append("(PAUSE FOR DRILL CHANGE)")
        self.mmGCodeList.append("M00")
        self.mmGCodeList.append("(" + self.drillSize + "MM HOLE DRILL)")

        for valve in self.controlMap:

            self.mmGCodeList.append("G1 X" + str(valve[0]) + " Y" + str(valve[1]))
            self.mmGCodeList.append("Z" + self.drillHoleDepth)
            self.mmGCodeList.append("Z" + self.drillSize)


