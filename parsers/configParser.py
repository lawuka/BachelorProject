import json

class configParser() :

    def __init__(self):

        self.file = None
        self.conf = None

    def parseConfig(self, fileName):

        self.file = open(fileName)
        self.conf = json.load(self.file)
        self.file.close()
        #load['drillOptions']['drillSize']
        #load['drillOptions']['hole']['depth']
        #load['drillOptions']['flow']['depth']
        #load['componentOptions']['valve']['length']

        return self.conf
