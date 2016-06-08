'''

Created on 24 feb 2015

@author Lasse

'''

from tkinter import *
from tkinter import filedialog
from math import pi
from model.mathFunctions import rotate_coordinate


class View(Tk):

    def __init__(self, c):

        self.c = c
        self.library = None
        self.conf = None
        self.canvasMap = None

        Tk.__init__(self)
        self.title('Biochip Production')
        self.grid()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.scaleH = None
        self.scaleW = None
        self.minsize(563, 520)
        self.canvas = None

        self.currentSVGFile = StringVar()
        self.currentSVGFile.set('chip_examples/svg_example2.svg')  # Should be ''
        self.c.getModel().setCurrentSVGFile('chip_examples/svg_example2.svg')  # Should be ''

        self.currentLibraryFile = StringVar()
        self.currentLibraryFile.set('library/component_library.svg')  # Should be ''
        self.c.getModel().setCurrentLibraryFile('library/component_library.svg')  # Should be ''

        self.currentConfigFile = StringVar()
        self.currentConfigFile.set('config/conf.ini')  # Should be ''
        self.c.getModel().setCurrentConfigFile('config/conf.ini')  # Should be ''

        self.currentStatusMsg = StringVar()
        self.currentStatusMsg.set('None')

        self.layoutShown = False

    def show(self):

        self.canvas = Canvas(width=400, height=400, highlightthickness=1, highlightbackground='grey')
        self.canvas.grid(column=0, row=0, sticky=N+S+E+W)
        self.canvas.bind('<Configure>', self.updateCanvasScale)

        rightView = Frame(self)
        buttonWidth = 15
        Button(rightView, text="Simulator G-Code", command=self.produceSimGCode, width = buttonWidth, state=DISABLED).pack(side = TOP)
        Button(rightView, text="Micro Milling G-Code", command=self.produceMMFlowGCode, width = buttonWidth).pack(side = TOP)
        Button(rightView, text="Show Chip Layout", command=self.showLayout, width = buttonWidth).pack(side = TOP)
        self.gCodeTextField = Text(rightView, width=22, state=DISABLED)
        self.gCodeTextField.pack(side = TOP, expand=True, fill="y")
        rightView.grid(column = 1, row = 0, rowspan = 4, sticky = N + E + S)

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

    def updateCanvasScale(self, event):

        if self.layoutShown:
            self.scaleH =  event.height / int(self.canvasMap['height'])
            self.scaleW = event.width / int(self.canvasMap['width'])
            self.canvas.delete("all")
            self.showLayout()

        #print(self.winfo_height())
        #print(self.winfo_width())
        #print(self.canvas.winfo_height())
        #print(self.canvas.winfo_width())
        #print(self.scaleH)
        #print(self.scaleW)

    def showLayout(self):

        self.library = self.c.getModel().getLibraryData()
        self.conf = self.c.getModel().getConfigData()
        self.canvasMap = self.c.getChipLayout()
        self.updateLayout()

    def updateLayout(self):

        if self.layoutShown:
            self.canvas.delete("all")
        else:
            self.scaleH =  self.canvas.winfo_height() / int(self.canvasMap['height'])
            self.scaleW = self.canvas.winfo_width() / int(self.canvasMap['width'])

        for line in self.canvasMap['lines']:
            xyxy = float(line[0])*self.scaleW, float(line[1])*self.scaleH, float(line[2])*self.scaleW, float(line[3])*self.scaleH
            self.canvas.create_line(xyxy, width=1)

        for hole in self.canvasMap['holes']:
            self.canvas.create_oval((float(hole[0])-1)*self.scaleW, (float(hole[1])-1)*self.scaleH,
                                    (float(hole[0]) + 1)*self.scaleW, (float(hole[1]) + 1)*self.scaleH)

        for component in self.canvasMap['components']:
            if component[0] in self.library:
                componentX = float(component[1])
                componentY = float(component[2])
                componentWidth = float(self.library[component[0]]['Size'].find('Width').text)
                componentHeight = float(self.library[component[0]]['Size'].find('Height').text)
                componentActualPositionX = componentX - componentWidth/2
                componentActualPositionY = componentY - componentHeight/2
                for iComponent in self.library[component[0]]['Internal']:
                    if iComponent.tag == 'FlowLine':
                        self.drawFlowLine(iComponent, componentActualPositionX, componentActualPositionY,
                                          component[3] % 360.0,
                                          componentWidth,
                                          componentHeight)
                    elif iComponent.tag == 'FlowCircle':
                        self.drawFlowCircle(iComponent, componentActualPositionX, componentActualPositionY,
                                            component[3] % 360.0)

                    ############################
                    #Red boxes around component#
                    ############################
                    '''
                    self.canvas.create_line(componentActualPositionX * self.scaleW,
                                            componentActualPositionY * self.scaleH,
                                            (componentActualPositionX + componentWidth) * self.scaleW,
                                            (componentActualPositionY) * self.scaleH,
                                            width=1,
                                            fill='red')
                    self.canvas.create_line(componentActualPositionX * self.scaleW,
                                            componentActualPositionY * self.scaleH,
                                            componentActualPositionX * self.scaleW,
                                            (componentActualPositionY + componentHeight) * self.scaleH,
                                            width=1,
                                            fill='red')
                    self.canvas.create_line((componentActualPositionX + componentWidth) * self.scaleW,
                                            componentActualPositionY * self.scaleH,
                                            (componentActualPositionX + componentWidth) * self.scaleW,
                                            (componentActualPositionY + componentHeight) * self.scaleH,
                                            width=1,
                                            fill='red')
                    self.canvas.create_line(componentActualPositionX * self.scaleW,
                                            (componentActualPositionY + componentHeight) * self.scaleH,
                                            (componentActualPositionX + componentWidth) * self.scaleW,
                                            (componentActualPositionY + componentHeight) * self.scaleH,
                                            width=1,
                                            fill='red')
                    '''
            else:
                print('Skipping drawing - ' + component[0] + ' not in Library')

        if not self.layoutShown:
            self.layoutShown = True

        self.currentStatusMsg.set('Chip layout was updated')
        self.updateView()

    def drawFlowLine(self, flowLine, componentActualPositionX, componentActualPositionY,
                     componentRotation, componentWidth, componentHeight):
        flowStartX = float(flowLine.find('Start').find('X').text)# + componentActualPositionX #- \
                                 #float(self.conf['drillOptions']['drillSize'])/2
        flowStartY = float(flowLine.find('Start').find('Y').text)# + componentActualPositionY #- \
                                 #float(self.conf['drillOptions']['drillSize'])/2
        flowEndX = float(flowLine.find('End').find('X').text)# + componentActualPositionX #- \
                               #float(self.conf['drillOptions']['drillSize'])/2
        flowEndY = float(flowLine.find('End').find('Y').text)# + componentActualPositionY #- \
                               #float(self.conf['drillOptions']['drillSize'])/2

        if componentRotation in {90, 180, 270}:
            tempFlowStartX = rotate_coordinate(flowStartX - componentWidth/2,
                                                   flowStartY - componentHeight/2,
                                                   componentRotation,
                                                   'x')
            tempFlowStartY = rotate_coordinate(flowStartX - componentWidth/2,
                                                   flowStartY - componentHeight/2,
                                                   componentRotation,
                                                   'y')
            tempFlowEndX = rotate_coordinate(flowEndX - componentWidth/2,
                                                 flowEndY - componentHeight/2,
                                                 componentRotation,
                                                 'x')
            tempFlowEndY = rotate_coordinate(flowEndX - componentWidth/2,
                                                 flowEndY - componentHeight/2,
                                                 componentRotation,
                                                 'y')

            flowStartX = tempFlowStartX + componentActualPositionX + componentWidth/2
            flowStartY = tempFlowStartY + componentActualPositionY + componentHeight/2
            flowEndX = tempFlowEndX + componentActualPositionX + componentWidth/2
            flowEndY = tempFlowEndY + componentActualPositionY + componentHeight/2

        else:
            flowStartX += componentActualPositionX
            flowStartY += componentActualPositionY
            flowEndX += componentActualPositionX
            flowEndY += componentActualPositionY

        self.canvas.create_line(flowStartX * self.scaleW,
                                flowStartY * self.scaleH,
                                flowEndX * self.scaleW,
                                flowEndY * self.scaleH,
                                width=1)

    def drawFlowCircle(self, flowCircle, componentActualPositionX, componentActualPositionY,
                       componentRotation):
        circleCenterX = float(flowCircle.find('Center').find('X').text) + componentActualPositionX#- \
                        #float(self.conf['drillOptions']['drillSize'])/2
        circleCenterY = float(flowCircle.find('Center').find('Y').text) + componentActualPositionY# - \
                        #float(self.conf['drillOptions']['drillSize'])/2
        circleRadius = float(flowCircle.find('Radius').text)#- float(self.conf['drillOptions']['drillSize'])/2
        angleList = list(flowCircle.find('Valves'))
        xy = (circleCenterX - circleRadius) * self.scaleW, (circleCenterY - circleRadius) * self.scaleH, \
              (circleCenterX + circleRadius) * self.scaleW, (circleCenterY + circleRadius) * self.scaleH
        valveLengthAngle = (360 * 2 * float(self.conf['drillOptions']['drillSize']))/(2 * circleRadius * pi)

        remainingAngle = 360
        for i in range(0,len(angleList)):
            if i == len(angleList)-1:
                self.canvas.create_arc(xy,
                                       start=float(angleList[i].text)+valveLengthAngle/2 + componentRotation,
                                       extent=(remainingAngle-valveLengthAngle) % 360.0,
                                       style=ARC)
            else:
                self.canvas.create_arc(xy,
                                       start=float(angleList[i].text)+valveLengthAngle/2 + componentRotation,
                                       extent=(float(angleList[i+1].text) - float(angleList[i].text) -
                                               valveLengthAngle) % 360.0,
                                       style=ARC)
            if i != len(angleList)-1:
                remainingAngle -= float(angleList[i+1].text) - float(angleList[i].text)

    def produceSimGCode(self):
        '''
        Produce Simulator G-Code
        '''
        self.c.createSimGCode()
        self.currentStatusMsg.set('Produced Simulator G-Code')
        self.updateView()

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
        self.updateView()

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

    def updateView(self):
        self.update()