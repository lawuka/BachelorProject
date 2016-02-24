'''

Created on 24 feb 2015

@author Lasse

'''

from tkinter import *

class GUI(Tk):

    def __init__(self, canvasMap):
        Tk.__init__(self)
        self.grid()
        self.title('Graphical view of flow layer')

        self.quitButton = Button(self, text = "Quit", command = self.quit)
        self.quitButton.grid()

        self.canvas = Canvas(self, width = canvasMap['width'], height = canvasMap['height'])
        self.canvas.grid()

        for line in canvasMap['lines']:
            self.canvas.create_line(line[0],line[1],line[2],line[3], fill="red", width = 10)

    def showGUI(self):
        '''
        Display gui
        '''
        self.update()
        self.mainloop()