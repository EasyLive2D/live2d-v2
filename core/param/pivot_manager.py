from core import DEF
from core.param import ParamPivots
from core.type import Array, Float32Array


class PivotManager:

    def __init__(self):
        self.Ob_ = None

    def zP_(self):
        self.Ob_ = Array()

    def read(self, aH):
        self.Ob_ = aH.readObject()

    def Ur_(self, aK):
        if aK.requireSetup():
            return True

        aH = aK.getInitVersion()
        for aJ in range(len(self.Ob_) - 1, -1, -1):
            aI = self.Ob_[aJ].getParamIndex(aH)
            if aI == ParamPivots.ds_:
                aI = aK.getParamIndex(self.Ob_[aJ].getParamID())

            if aK.isParamUpdated(aI):
                return True

        return False

    def Q2_(self, aL, aV):
        aX = len(self.Ob_)
        aJ = aL.getInitVersion()
        aN = 0
        for aK in range(0, aX, 1):
            aH = self.Ob_[aK]
            aI = aH.getParamIndex(aJ)
            if aI == ParamPivots.ds_:
                aI = aL.getParamIndex(aH.getParamID())
                aH.Pb_(aI, aJ)

            if aI < 0:
                raise Exception("err 23242 : " + aH.getParamID())

            aU = 0 if aI < 0 else aL.getParamFloat(aI)
            aQ = aH.N2_()
            aM = aH.d2_()
            aP = -1
            aT = 0
            if aQ < 1:
                pass
            else:
                if aQ == 1:
                    aS = aM[0]
                    if aS - DEF.GOSA < aU < aS + DEF.GOSA:
                        aP = 0
                        aT = 0
                    else:
                        aP = 0
                        aV[0] = True
                else:
                    aS = aM[0]
                    if aU < aS - DEF.GOSA:
                        aP = 0
                        aV[0] = True
                    else:
                        if aU < aS + DEF.GOSA:
                            aP = 0
                        else:
                            aW = False
                            for aO in range(1, aQ, 1):
                                aR = aM[aO]
                                if aU < aR + DEF.GOSA:
                                    if aR - DEF.GOSA < aU:
                                        aP = aO
                                    else:
                                        aP = aO - 1
                                        aT = (aU - aS) / (aR - aS)
                                        aN += 1

                                    aW = True
                                    break

                                aS = aR

                            if not aW:
                                aP = aQ - 1
                                aT = 0
                                aV[0] = True

            aH.wr_(aP)
            aH.AL_(aT)

        return aN

    def zr_(self, aN, aT, aP):
        aR = 1 << aP
        if aR + 1 > DEF.PIVOT_TABLE_SIZE:
            print("err 23245\n")

        aS = len(self.Ob_)
        aK = 1
        aH = 1
        aJ = 0
        for aQ in range(0, aR, 1):
            aN[aQ] = 0

        for aL in range(0, aS, 1):
            aI = self.Ob_[aL]
            if aI.SL_() == 0:
                aO = aI.Lr_() * aK
                if aO < 0:
                    raise Exception("err 23246")

                for aQ in range(0, aR, 1):
                    aN[aQ] += aO
            else:
                aO = aK * aI.Lr_()
                aM = aK * (aI.Lr_() + 1)
                for aQ in range(0, aR, 1):
                    aN[aQ] += aO if (int(aQ / aH) % 2 == 0) else aM

                aT[aJ] = aI.SL_()
                aJ += 1
                aH *= 2

            aK *= aI.N2_()

        aN[aR] = 65535
        aT[aJ] = -1

    def h2_(self, aJ, aH, aK):
        aM = Float32Array(aH)
        for aL in range(0, aH, 1):
            aM[aL] = aK[aL]

        aI = ParamPivots()
        aI.yP_(aJ)
        aI.t2_(aH, aM)
        self.Ob_.append(aI)

    def J2_(self, aO):
        aN = aO
        aM = len(self.Ob_)
        for aK in range(0, aM, 1):
            aI = self.Ob_[aK]
            aH = aI.N2_()
            aJ = aN % aI.N2_()
            aL = aI.d2_()[aJ]
            print("%s[%d]=%7.2f / ", aI.getParamID(), aJ, aL)
            aN /= aH

        print("\n")

    def getParamCount(self):
        return len(self.Ob_)

    def zs_(self):
        return self.Ob_
