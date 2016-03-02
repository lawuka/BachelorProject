'''

Created on 24 feb 2015

@author Lasse

'''

from tkinter import *

class GUI(Tk):

    def __init__(self, canvasMap, mainClass):

        #Main class
        self.mainClass = mainClass
        Tk.__init__(self)
        self.grid()
        self.title('Graphical view of flow layer')

        self.quitButton = Button(self, text = "Quit", command = self.quit).grid()
        self.produceG = Button(self, text = "G-Code", command = self.produceGCode).grid()

        self.canvas = Canvas(self, width = canvasMap['width'], height = canvasMap['height'])
        self.canvas.grid()

        for line in canvasMap['lines']:
            self.canvas.create_line(line[0],line[1],line[2],line[3], fill="blue", width = 10)

        for hole in canvasMap['holes']:
            self.canvas.create_oval(hole[0],hole[1],int(hole[0])+ 10, int(hole[1]) + 10, fill = "green")

    def showGUI(self):
        '''
        Display gui
        '''
        self.update()
        self.mainloop()

    def produceGCode(self):
        '''
        Produce G-Code
        '''
        self.mainClass.createSimGCode()