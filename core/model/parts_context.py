class PartsDataContext:

    def __init__(self, parts):
        super().__init__()
        self.partsOpacity = None
        self.partsData = parts

    def getPartsOpacity(self):
        return self.partsOpacity

    def setPartsOpacity(self, value):
        self.partsOpacity = value
