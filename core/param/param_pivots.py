class ParamPivots:
    ds_ = -2

    def __init__(self):
        self.VP_ = 0
        self.wL_ = None
        self.GP_ = None
        self._8o = ParamPivots.ds_
        self._2r = -1
        self.O2_ = 0
        self.ri_ = 0

    def read(self, aH):
        self.wL_ = aH.readObject()
        self.VP_ = aH.readInt32()
        self.GP_ = aH.readObject()

    def getParamIndex(self, aH):
        if self._2r != aH:
            self._8o = ParamPivots.ds_

        return self._8o

    def Pb_(self, aI, aH):
        self._8o = aI
        self._2r = aH

    def getParamID(self):
        return self.wL_

    def yP_(self, aH):
        self.wL_ = aH

    def N2_(self):
        return self.VP_

    def d2_(self):
        return self.GP_

    def t2_(self, aI, aH):
        self.VP_ = aI
        self.GP_ = aH

    def Lr_(self):
        return self.O2_

    def wr_(self, aH):
        self.O2_ = aH

    def SL_(self):
        return self.ri_

    def AL_(self, aH):
        self.ri_ = aH
