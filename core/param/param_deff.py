class ParamDefF:

    def __init__(self):
        self.TT_ = None
        self.LT_ = None
        self.FS_ = None
        self.wL_ = None

    def read(self, aH):
        self.TT_ = aH.readFloat32()
        self.LT_ = aH.readFloat32()
        self.FS_ = aH.readFloat32()
        self.wL_ = aH.readObject()

    def getMinValue(self):
        return self.TT_

    def getMaxValue(self):
        return self.LT_

    def getDefaultValue(self):
        return self.FS_

    def getParamID(self):
        return self.wL_
