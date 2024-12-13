class IDrawContext:

    def __init__(self, dd):
        self.interpolatedDrawOrder = None
        self.paramOutside = [False]
        self.partsOpacity = 0
        self.available = True
        self.baseOpacity = 1
        self.clipBufPre_clipContext = None
        self.drawData = dd

    def u2_(self):
        return self.paramOutside[0]

    def yo_(self):
        return self.available and not self.paramOutside[0]

    def getDrawData(self):
        return self.drawData
