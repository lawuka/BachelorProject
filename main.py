'''
Created on 24 feb 2015

@author Lasse
'''
from model.model import Model
from view.view import View

class Controller():

    def __init__(self):

        self.model = Model()
        self.view = View(self)
        self.wtf = WriteToFile()

    def run(self):

        self.view.show()
        self.view.deiconify()
        self.view.mainloop()

    def createSimGCode(self):

        self.updateData()
        self.model.setSimulatorGCode()
        self.writeGCodeToFile("SimulatorGCode.ngc", self.model.getSimulatorGCode())

    def createMMFlowGCode(self):

        self.updateData()
        self.model.setMicroMillingFlowGCode()
        self.writeGCodeToFile("MMFlowGCode.txt", self.model.getMMFlowGCode())

    def writeGCodeToFile(self, fileName, gCodeList):

        self.wtf.writeGCodeListToFile(fileName, gCodeList)

    def updateData(self):

        self.model.setConfigData()
        self.model.setLibraryData()
        self.model.setSVGData()

    def getChipLayout(self):

        self.updateData()
        return self.model.getSVGData()

    def setSVGFile(self, fileName):

        self.model.currentSVGFile = fileName

    def setLibraryFile(self, fileName):

        self.model.currentLibraryFile = fileName

    def setConfigFile(self, fileName):

        self.model.currentConfigFile = fileName

    def getModel(self):

        return self.model


class WriteToFile():

    def __init__(self):

        self.file = None

    def writeGCodeListToFile(self, fileName, gCodeList):

        self.file = open(fileName, "w")
        for line in gCodeList:
            self.file.write(line + "\n")
        self.file.close()

'''
Triggering the main program
'''
if __name__ == '__main__':
    controller = Controller()
    controller.run()
    #controller.createMMFlowGCode()





