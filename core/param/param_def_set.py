from core.type import Array


class ParamDefSet:

    def __init__(self):
        self.paramDefList = None

    def getParamDefFloatList(self):
        return self.paramDefList

    def initDirect(self):
        self.paramDefList = Array()

    def read(self, br):
        self.paramDefList = br.readObject()
