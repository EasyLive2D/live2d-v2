from core.util.ut_motion import UtMotion
from core.util import UtSystem


class AMotion:

    def __init__(self):
        self.dP_ = None
        self.eo_ = None
        self.V0_ = None
        self.dP_ = 1000
        self.eo_ = 1000
        self.V0_ = 1
        self.a0_()

    def a0_(self):
        pass

    def setFadeIn(self, aH):
        self.dP_ = aH

    def setFadeOut(self, aH):
        self.eo_ = aH

    def pT_(self, aH):
        self.V0_ = aH

    def getFadeOut(self):
        return self.eo_

    def _4T(self):
        return self.eo_

    def mT_(self):
        return self.V0_

    def getDurationMSec(self):
        return -1

    def getLoopDurationMSec(self):
        return -1

    def updateParam(self, aJ, aN):
        if not aN.AT_ or aN._9L:
            return

        aL = UtSystem.getUserTimeMSec()
        if aN.z2_ < 0:
            aN.z2_ = aL
            aN.bs_ = aL
            aM = self.getDurationMSec()
            if aN.Do_ < 0:
                aN.Do_ = -1 if (aM <= 0) else aN.z2_ + aM

        aI = self.V0_
        aH = 1 if (self.dP_ == 0) else UtMotion.r2_(((aL - aN.bs_) / self.dP_))
        aK = 1 if (self.eo_ == 0 or aN.Do_ < 0) else UtMotion.r2_(((aN.Do_ - aL) / self.eo_))
        aI = aI * aH * aK
        if not (0 <= aI <= 1):
            print("### assert!! ### ")

        self.updateParamExe(aJ, aL, aI, aN)
        if 0 < aN.Do_ < aL:
            aN._9L = True

    def updateParamExe(self, aH, aI, aJ, aK):
        pass

    @staticmethod
    def JT_(aP, aN, aO):
        aQ = aP / aN
        a1 = aO / aN
        aU = a1
        aZ = 1 / 3
        aR = 2 / 3
        a0 = 1 - (1 - a1) * (1 - a1)
        a2 = 1 - (1 - aU) * (1 - aU)
        aM = 0
        aL = ((1 - a1) * aZ) * a0 + (aU * aR + (1 - aU) * aZ) * (1 - a0)
        aK = (aU + (1 - aU) * aR) * a2 + (a1 * aZ + (1 - a1) * aR) * (1 - a2)
        aJ = 1
        aY = aJ - 3 * aK + 3 * aL - aM
        aX = 3 * aK - 6 * aL + 3 * aM
        aW = 3 * aL - 3 * aM
        aV = aM
        if aQ <= 0:
            return 0
        elif aQ >= 1:
            return 1

        aS = aQ
        aI = aS * aS
        aH = aS * aI
        aT = aY * aH + aX * aI + aW * aS + aV
        return aT
