'''

Created on 24 feb 2015

@author Lasse

'''

from tkinter import *
from tkinter import filedialog
from math import pi, cos, sin, radians
from model.mathFunctions import rotate_coordinate


class View(Tk):

    def __init__(self, c):

        self.c = c
        self.library = None
        self.conf = None
        self.canvasMap = None
        self.flowLineMap = None
        self.flowCircleMap = None
        self.flowHoleMap = None
        self.controlMap = None

        Tk.__init__(self)
        self.title('Biochip Production')
        self.grid()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.scale = None
        self.scale = None
        self.minsize(563, 520)
        self.canvas = None

        self.currentSVGFile = StringVar()
        self.currentSVGFile.set('chip_examples/svg_example2.svg')  # Should be ''
        self.c.getModel().setCurrentSVGFile('chip_examples/svg_example2.svg')  # Should be ''

        self.currentLibraryFile = StringVar()
        self.currentLibraryFile.set('library/component_library.xml')  # Should be ''
        self.c.getModel().setCurrentLibraryFile('library/component_library.xml')  # Should be ''

        self.currentConfigFile = StringVar()
        self.currentConfigFile.set('config/conf.ini')  # Should be ''
        self.c.getModel().setCurrentConfigFile('config/conf.ini')  # Should be ''

        self.currentStatusMsg = StringVar()
        self.currentStatusMsg.set('None')

        self.layoutShown = False

    def show(self):

        self.canvas = Canvas(width=400, height=400, highlightthickness=1, highlightbackground='grey')
        self.canvas.grid(column=0, row=0, sticky=N+S+E+W)
        self.canvas.bind('<Configure>', self.updateCanvas)

        rightView = Frame(self)
        buttonWidth = 15

        self.showFlowCheckVar = IntVar()
        self.showFlowCheckVar.set(0)
        self.showControlCheckVar = IntVar()
        self.showControlCheckVar.set(0)
        chipViewFrame = LabelFrame(rightView, text='Chip Layout')
        chipViewFrame.grid(row=0, column=0, sticky=E + W, ipady=3, ipadx=5)
        self.showLayoutCheck = Checkbutton(chipViewFrame, variable=self.showFlowCheckVar,
                                           command=self.drawCanvas, text="Show flow layout", state=DISABLED)
        self.showControlCheck = Checkbutton(chipViewFrame, variable=self.showControlCheckVar,
                                            command=self.drawCanvas,text="Show control layout", state=DISABLED)
        self.showLayoutCheck.pack(side = TOP, anchor=W)
        self.showControlCheck.pack(side = TOP, anchor=W)
        Button(chipViewFrame, text="Generate Chip Layout", command=self.showLayout, width = buttonWidth).pack(side = TOP)

        gCodeFrame = LabelFrame(rightView, text='GCode')
        Button(gCodeFrame, text="Simulator Flow", command=self.produceSimGCode,
               width = buttonWidth, state=DISABLED).pack(side = TOP)
        Button(gCodeFrame, text="Simulator Control", command=self.produceSimControlGCode,
               width = buttonWidth, state=DISABLED).pack(side = TOP)
        Button(gCodeFrame, text="Micro Milling Flow", command=self.produceMMFlowGCode,
               width = buttonWidth).pack(side = TOP)
        Button(gCodeFrame, text="Micro Milling Control", command=self.produceMMControlGCode,
               width=buttonWidth, state=DISABLED).pack(side=TOP)
        gCodeFrame.grid(row=1, column=0, sticky=E + W, ipady=3, ipadx=5)

        gCodeTextFrame = LabelFrame(rightView, text='GCode View')
        self.gCodeTextField = Text(gCodeTextFrame, width=25, state=DISABLED, highlightbackground='grey', highlightthickness=1)
        self.gCodeTextField.pack(side = TOP, expand=True, fill="y", pady=5)
        self.gCodeTextFieldCopy = Button(gCodeTextFrame, text="Copy To Clipboard", width=buttonWidth, state=DISABLED, command=self.copyGCodeToClipboard)
        self.gCodeTextFieldCopy.pack(side = TOP)
        gCodeTextFrame.grid(row=2, column=0, sticky=N + E + W + S, ipady=3, ipadx=5)

        rightView.grid(column = 1, row = 0, rowspan = 4, sticky = N+S, padx=5)
        rightView.rowconfigure(2,weight=1)

        svgInfo = Frame(self)
        Label(svgInfo, text="SVG File:", width=10,  anchor=W).pack(side = LEFT, padx=5)
        Entry(svgInfo, textvariable=self.currentSVGFile, relief=SUNKEN, state = DISABLED).pack(side=LEFT,expand=True,fill="x", padx=5)
        Button(svgInfo, text="Open", width = 5, command=self.openSVGFile).pack(side = LEFT)
        svgInfo.grid(column = 0, row = 1, sticky = W + E)
        libraryInfo = Frame(self)
        Label(libraryInfo, text="Library File:", width=10, anchor=W).pack(side = LEFT, padx = 5, pady = 5)
        Entry(libraryInfo, textvariable=self.currentLibraryFile, relief=SUNKEN, state = DISABLED).pack(side = LEFT,expand=True,fill="x", padx=5)
        Button(libraryInfo, text="Open", width = 5, command=self.openLibraryFile).pack(side = LEFT)
        libraryInfo.grid(column = 0, row = 2, sticky = W + E)
        configInfo = Frame(self)
        Label(configInfo, text="Config File:", width=10, anchor=W).pack(side = LEFT, padx = 5, pady = 5)
        Entry(configInfo, textvariable=self.currentConfigFile, relief=SUNKEN, state = DISABLED).pack(side = LEFT,expand=True,fill="x", padx=5)
        Button(configInfo, text="Open", width = 5, command=self.openConfigFile).pack(side = LEFT)
        configInfo.grid(column = 0, row = 3, sticky = W + E)

        statusBar = Frame(self)
        Entry(statusBar, textvariable=self.currentStatusMsg, relief=SUNKEN, state=DISABLED).pack(fill="x")
        statusBar.grid(column = 0, columnspan=2, row= 4, sticky = W + E)

    def updateCanvas(self, event):

        if self.layoutShown:
            self.scale = min(event.height / int(self.canvasMap['height']),
                             event.width / int(self.canvasMap['width']))
            self.drawCanvas()

    def showLayout(self):

        self.canvasMap = self.c.getChipLayout()
        self.library = self.c.getModel().getLibraryData()
        self.conf = self.c.getModel().getConfigData()
        self.showLayoutCheck['state'] = NORMAL
        self.showControlCheck['state'] = NORMAL
        self.clearMaps()
        self.updateMaps()

        if self.showFlowCheckVar.get() == 1 or self.showControlCheckVar.get() == 1:
            self.drawCanvas()

    def drawCanvas(self):

        self.canvas.delete("all")

        if self.showFlowCheckVar.get() == 1:
            self.drawFlowLines()
            self.drawFlowCircles()
            self.drawFlowHoles()

        if self.showControlCheckVar.get() == 1:
            self.drawControlValves()

        self.layoutShown = True
        self.updateView()

    def updateMaps(self):

        if not self.layoutShown:
            self.scale = min(self.canvas.winfo_height() / int(self.canvasMap['height']),
                             self.canvas.winfo_width() / int(self.canvasMap['width']))

        for line in self.canvasMap['lines']:
            xyxy = [float(line[0]), float(line[1]), float(line[2]), float(line[3])]
            self.flowLineMap.append(xyxy)

        for component in self.canvasMap['components']:
            if component[0] in self.library:
                componentX = float(component[1])
                componentY = float(component[2])
                componentWidth = float(self.library[component[0]]['Size'].find('Width').text)
                componentHeight = float(self.library[component[0]]['Size'].find('Height').text)
                componentActualPositionX = componentX - componentWidth/2
                componentActualPositionY = componentY - componentHeight/2

                controlValves = self.library[component[0]]['Control']
                if controlValves != None and len(controlValves) != 0:
                    self.appendControlValves(controlValves, [componentActualPositionX], [componentActualPositionY],
                                          [component[3] % 360.0],
                                          [componentWidth],
                                          [componentHeight])

                for iComponent in self.library[component[0]]['Internal']:
                    if iComponent.tag == 'FlowLine':
                        self.appendFlowLines(iComponent, [componentActualPositionX], [componentActualPositionY],
                                          [component[3] % 360.0],
                                          [componentWidth],
                                          [componentHeight])
                    elif iComponent.tag == 'FlowCircle':
                        self.appendFlowCircles(iComponent, [componentActualPositionX], [componentActualPositionY],
                                            [component[3] % 360.0],
                                            [componentWidth],
                                            [componentHeight])
                    elif iComponent.tag == 'FlowHole':
                        self.appendFlowHoles(iComponent, [componentActualPositionX], [componentActualPositionY],
                                             [component[3] % 360.0],
                                             [componentWidth],
                                             [componentHeight])
                    else:
                        self.drawComponent(iComponent,
                                           [componentActualPositionX], [componentActualPositionY],
                                           [component[3] % 360.0],
                                           [componentWidth],
                                           [componentHeight])

                    ############################
                    #Red boxes around component#
                    ############################
                    '''
                    self.canvas.create_line(componentActualPositionX * self.scale,
                                            componentActualPositionY * self.scale,
                                            (componentActualPositionX + componentWidth) * self.scale,
                                            (componentActualPositionY) * self.scale,
                                            width=1,
                                            fill='red')
                    self.canvas.create_line(componentActualPositionX * self.scale,
                                            componentActualPositionY * self.scale,
                                            componentActualPositionX * self.scale,
                                            (componentActualPositionY + componentHeight) * self.scale,
                                            width=1,
                                            fill='red')
                    self.canvas.create_line((componentActualPositionX + componentWidth) * self.scale,
                                            componentActualPositionY * self.scale,
                                            (componentActualPositionX + componentWidth) * self.scale,
                                            (componentActualPositionY + componentHeight) * self.scale,
                                            width=1,
                                            fill='red')
                    self.canvas.create_line(componentActualPositionX * self.scale,
                                            (componentActualPositionY + componentHeight) * self.scale,
                                            (componentActualPositionX + componentWidth) * self.scale,
                                            (componentActualPositionY + componentHeight) * self.scale,
                                            width=1,
                                            fill='red')
                    #'''
            else:
                print('Skipping drawing - ' + component[0] + ' not in Library')

        self.currentStatusMsg.set('Chip layout was updated')

    def drawComponent(self, component, componentXList, componentYList,
                      componentRotationList, componentWidthList, componentHeightList):
        if component.tag in self.library:
            componentX = float(component.find('X').text)
            componentY = float(component.find('Y').text)
            componentWidth = float(self.library[component.tag]['Size'].find('Width').text)
            componentHeight = float(self.library[component.tag]['Size'].find('Height').text)
            componentXList.append(componentX - componentWidth/2)
            componentYList.append(componentY - componentHeight/2)
            #self.drawRedBox(componentXList, componentYList, componentWidth, componentHeight)
            componentRotationList.append(float(component.find('Rotation').text) % 360.0)
            componentWidthList.append(componentWidth)
            componentHeightList.append(componentHeight)

            controlValves = self.library[component.tag]['Control']
            if controlValves != None and len(controlValves) != 0:
                self.appendControlValves(controlValves, componentXList, componentYList,
                                        componentRotationList, componentWidthList, componentHeightList)

            for iComponent in self.library[component.tag]['Internal']:
                if iComponent.tag == 'FlowLine':
                    self.appendFlowLines(iComponent, componentXList, componentYList,
                                      componentRotationList,
                                      componentWidthList,
                                      componentHeightList)
                elif iComponent.tag == 'FlowCircle':
                    self.appendFlowCircles(iComponent, componentXList, componentYList,
                                        componentRotationList,
                                        componentWidthList,
                                        componentHeightList)
                elif iComponent.tag == 'FlowHole':
                    self.appendFlowHoles(iComponent, componentXList, componentYList,
                                      componentRotationList,
                                      componentWidthList,
                                      componentHeightList)
                else:
                    self.drawComponent(iComponent, componentXList, componentYList,
                                       componentRotationList,
                                       componentWidthList,
                                       componentHeightList)
                    componentXList.pop()
                    componentYList.pop()
                    componentRotationList.pop()
                    componentWidthList.pop()
                    componentHeightList.pop()
        else:
            print('Skipping drawing - ' + component.tag + ' not in Library')

    def appendFlowLines(self, flowLine, componentXList, componentYList,
                     componentRotationList, componentWidthList, componentHeightList):
        flowStartX = float(flowLine.find('Start').find('X').text)# + componentActualPositionX #- \
                                 #float(self.conf['drillOptions']['drillSize'])/2
        flowStartY = float(flowLine.find('Start').find('Y').text)# + componentActualPositionY #- \
                                 #float(self.conf['drillOptions']['drillSize'])/2
        flowEndX = float(flowLine.find('End').find('X').text)# + componentActualPositionX #- \
                               #float(self.conf['drillOptions']['drillSize'])/2
        flowEndY = float(flowLine.find('End').find('Y').text)# + componentActualPositionY #- \
                               #float(self.conf['drillOptions']['drillSize'])/2

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


        self.flowLineMap.append([flowStartX,
                                 flowStartY,
                                 flowEndX,
                                 flowEndY])

    def drawFlowLines(self):
        for flowLine in self.flowLineMap:
            self.canvas.create_line(self.scaleCoords(flowLine),
                                    width=1)

    def appendFlowCircles(self, flowCircle, componentXList, componentYList,
                       componentRotationList, componentWidthList, componentHeightList):
        circleCenterX = float(flowCircle.find('Center').find('X').text)# + componentXList[0]#- \
                        #float(self.conf['drillOptions']['drillSize'])/2
        circleCenterY = float(flowCircle.find('Center').find('Y').text)# + componentYList[0]# - \
                        #float(self.conf['drillOptions']['drillSize'])/2

        totalRotation = 0

        for i in range(len(componentXList)-1,-1,-1):
            if componentRotationList[i] != 0.0:
                tempCircleCenterX = rotate_coordinate(circleCenterX - componentWidthList[i]/2,
                                                      circleCenterY - componentHeightList[i]/2,
                                                      componentRotationList[i],
                                                      'x')

                tempCircleCenterY = rotate_coordinate(circleCenterX - componentWidthList[i]/2,
                                                      circleCenterY - componentHeightList[i]/2,
                                                      componentRotationList[i],
                                                      'y')
                circleCenterX = tempCircleCenterX + componentXList[i] + componentWidthList[i]/2
                circleCenterY = tempCircleCenterY + componentYList[i] + componentHeightList[i]/2
            else:
                circleCenterX += componentXList[i]
                circleCenterY += componentYList[i]

            totalRotation += componentRotationList[i]

        circleRadius = float(flowCircle.find('Radius').text)
        angleList = list(flowCircle.find('Valves'))

        for valve in angleList:
            valveDegree = float(valve.text)
            valveCenterX = circleCenterX + cos(radians(valveDegree+totalRotation%360.0)) * circleRadius
            valveCenterY = circleCenterY + sin(radians(valveDegree+totalRotation%360.0)) * circleRadius
            self.controlMap.append([valveCenterX - 2,
                                     valveCenterY - 2,
                                     valveCenterX + 2,
                                     valveCenterY + 2])

        xy = [(circleCenterX - circleRadius), (circleCenterY - circleRadius),
              (circleCenterX + circleRadius), (circleCenterY + circleRadius)]

        self.flowCircleMap.append([xy,angleList, totalRotation, circleRadius])

    def drawFlowCircles(self):

        for flowCircle in self.flowCircleMap:
            xy = self.scaleCoords(flowCircle[0])
            angleList = flowCircle[1]
            totalRotation = flowCircle[2]
            circleRadius = flowCircle[3]

            valveLengthAngle = (360 * 2 * float(self.conf['drillOptions']['drillSize']))/(2 * circleRadius * pi)
            remainingAngle = 360

            if len(angleList) == 0:
                self.canvas.create_oval(xy)
            else:
                for i in range(0,len(angleList)):
                    if i == len(angleList)-1:
                        self.canvas.create_arc(xy,
                                               start=float(angleList[i].text)+valveLengthAngle/2 - totalRotation + 180.0,
                                               extent=(remainingAngle-valveLengthAngle) % 360.0,
                                               style=ARC)
                    else:
                        self.canvas.create_arc(xy,
                                               start=float(angleList[i].text)+valveLengthAngle/2 - totalRotation + 180.0,
                                               extent=(float(angleList[i+1].text) - float(angleList[i].text) -
                                                       valveLengthAngle) % 360.0,
                                               style=ARC)
                    if i != len(angleList)-1:
                        remainingAngle -= float(angleList[i+1].text) - float(angleList[i].text)

    def appendFlowHoles(self, flowHole, componentXList, componentYList,
                       componentRotationList, componentWidthList, componentHeightList):

        holeCenterX = float(flowHole.find('Center').find('X').text)
        holeCenterY = float(flowHole.find('Center').find('Y').text)

        for i in range(len(componentXList)-1,-1,-1):
            if componentRotationList[i] != 0.0:
                tempHoleCenterX = rotate_coordinate(holeCenterX - componentWidthList[i]/2,
                                                    holeCenterY - componentHeightList[i]/2,
                                                    componentRotationList[i],
                                                    'x')
                tempHoleCenterY = rotate_coordinate(holeCenterX - componentWidthList[i]/2,
                                                    holeCenterY - componentHeightList[i]/2,
                                                    componentRotationList[i],
                                                    'y')

                holeCenterX = tempHoleCenterX + componentXList[i] + componentWidthList[i]/2
                holeCenterY = tempHoleCenterY + componentYList[i] + componentHeightList[i]/2
            else:
                holeCenterX += componentXList[i]
                holeCenterY += componentYList[i]

        xyxy = [(holeCenterX - 1),
                (holeCenterY - 1),
                (holeCenterX + 1),
                (holeCenterY + 1)]

        self.flowHoleMap.append(xyxy)

    def drawFlowHoles(self):

        for flowHole in self.flowHoleMap:
            self.canvas.create_oval(self.scaleCoords(flowHole))

    def drawRedBox(self, componentXList, componentYList, componentWidth, componentHeight):
        ############################
        #Red boxes around component#
        ############################
        currentX = 0
        currentY = 0
        for i in range(0,len(componentXList)):
            currentX += componentXList[i]
            currentY += componentYList[i]

        self.canvas.create_line(currentX * self.scale,
                                currentY * self.scale,
                                (currentX + componentWidth) * self.scale,
                                (currentY) * self.scale,
                                width=1,
                                fill='red')
        self.canvas.create_line(currentX * self.scale,
                                currentY * self.scale,
                                currentX * self.scale,
                                (currentY + componentHeight) * self.scale,
                                width=1,
                                fill='red')
        self.canvas.create_line((currentX + componentWidth) * self.scale,
                                currentY * self.scale,
                                (currentX + componentWidth) * self.scale,
                                (currentY + componentHeight) * self.scale,
                                width=1,
                                fill='red')
        self.canvas.create_line(currentX * self.scale,
                                (currentY + componentHeight) * self.scale,
                                (currentX + componentWidth) * self.scale,
                                (currentY + componentHeight) * self.scale,
                                width=1,
                                fill='red')

    def appendControlValves(self, valveList, componentXList, componentYList,
                       componentRotationList, componentWidthList, componentHeightList):

        for valve in valveList:
            valveCenterX = float(valve.find('X').text)
            valveCenterY = float(valve.find('Y').text)

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


            xyxy = [(valveCenterX - 2),
                    (valveCenterY - 2),
                    (valveCenterX + 2),
                    (valveCenterY + 2)]

            self.controlMap.append(xyxy)

    def drawControlValves(self):
        for controlValve in self.controlMap:
            self.canvas.create_oval(self.scaleCoords(controlValve), outline='orange')


    def produceSimGCode(self):
        '''
        Produce Simulator G-Code
        '''
        self.c.createSimGCode()
        self.gCodeTextField['state'] = NORMAL
        for line in self.c.getModel().getSimulatorGCode():
            self.gCodeTextField.insert(END, line + "\n")
        self.currentStatusMsg.set('Produced Simulator G-Code')
        self.gCodeTextField['state'] = DISABLED
        if self.gCodeTextFieldCopy['state'] == DISABLED:
            self.gCodeTextFieldCopy['state'] = NORMAL
        self.updateView()

    def produceSimControlGCode(self):

        pass

    def produceMMFlowGCode(self):
        '''
        Produce Micro Milling Machine G-Code
        '''
        self.c.createMMFlowGCode()
        self.currentStatusMsg.set('Produced Micromilling Machine G-Code')
        self.gCodeTextField['state'] = NORMAL
        for line in self.c.getModel().getMMFlowGCode():
            self.gCodeTextField.insert(END, line + "\n")
        self.gCodeTextField['state'] = DISABLED
        if self.gCodeTextFieldCopy['state'] == DISABLED:
            self.gCodeTextFieldCopy['state'] = NORMAL
        self.updateView()

    def produceMMControlGCode(self):

        pass

    def openSVGFile(self):

        fileName = filedialog.askopenfilename()
        if fileName is not '':
            self.currentSVGFile.set(fileName)
            self.c.getModel().setCurrentSVGFile(fileName)
            self.updateView()

    def openLibraryFile(self):

        fileName = filedialog.askopenfilename()
        if fileName is not '':
            self.currentLibraryFile.set(fileName)
            self.c.getModel().setCurrentLibraryFile(fileName)
            self.updateView()

    def openConfigFile(self):

        fileName = filedialog.askopenfilename()
        if fileName is not '':
            self.currentConfigFile.set(fileName)
            self.c.getModel().setCurrentConfigFile(fileName)
            self.updateView()

    def copyGCodeToClipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.gCodeTextField.get("1.0", END))

    def scaleCoords(self, coordsList):

        return coordsList[0] * self.scale, coordsList[1] * self.scale, \
               coordsList[2] * self.scale, coordsList[3] * self.scale

    def clearMaps(self):
        self.flowLineMap = []
        self.flowCircleMap = []
        self.flowHoleMap = []
        self.controlMap = []

    def updateView(self):
        self.update()