from core.motion.amotion import AMotion
from core.motion.motion import Motion
from core.type import Array
from core.util import UtString


class Live2DMotion(AMotion):
    cs_ = "VISIBLE:"
    ar_ = "LAYOUT:"
    MTN_PREFIX_FADEIN = "FADEIN:"
    MTN_PREFIX_FADEOUT = "FADEOUT:"
    Co_ = 0
    _1T = 1

    def __init__(self):

        super().__init__()
        self.motions = Array()
        self.o2_ = None
        self._7r = Live2DMotion.Co_
        Live2DMotion.Co_ += 1
        self.D0_ = 30
        self.yT_ = 0
        self._E = False
        self.loopFadeIn = True
        self.rr_ = -1
        self.eP_ = 0

    def getDurationMSec(self):
        return -1 if self._E else self.rr_

    def getLoopDurationMSec(self):
        return self.rr_

    def dump(self):
        for aJ in range(0, len(self.motions), 1):
            aH = self.motions[aJ]
            print("_wL[%s] [%d]. ", aH._4P, len(aH.I0_))
            for aI in range(0, 10, 1):
                print("%5.2f ,", aH.I0_[aI])

            print("\n")

    def updateParamExe(self, aJ, aN, aQ, a3):
        aO = aN - a3.z2_
        a0 = aO * self.D0_ / 1000
        aK = int(a0)
        aR = a0 - aK
        for aZ in range(0, len(self.motions), 1):
            aV = self.motions[aZ]
            aL = len(aV.I0_)
            aT = aV._4P
            if aV.RP_ == Motion.hs_:
                aX = aV.I0_[(aL - 1 if aK >= aL else aK)]
                aJ.setParamFloat(aT, aX)
            else:
                if Motion.ws_ <= aV.RP_ <= Motion.Ys_:
                    pass
                else:
                    aH = aJ.getParamIndex(aT)
                    a4 = aJ.getModelContext()
                    aY = a4.getParamMax(aH)
                    aW = a4.getParamMin(aH)
                    aM = 0.4
                    aS = aM * (aY - aW)
                    aU = a4.getParamFloat(aH)
                    a2 = aV.I0_[(aL - 1 if aK >= aL else aK)]
                    a1 = aV.I0_[(aL - 1 if aK + 1 >= aL else aK + 1)]
                    if (a2 < a1 and a1 - a2 > aS) or (a2 > a1 and a2 - a1 > aS):
                        aI = a2
                    else:
                        aI = a2 + (a1 - a2) * aR

                    aP = aU + (aI - aU) * aQ
                    aJ.setParamFloat(aT, aP)

        if aK >= self.yT_:
            if self._E:
                a3.z2_ = aN
                if self.loopFadeIn:
                    a3.bs_ = aN
            else:
                a3._9L = True

        self.eP_ = aQ

    def r0_(self):
        return self._E

    def aL_(self, aH):
        self._E = aH

    def S0_(self):
        return self.D0_

    def U0_(self, aH):
        self.D0_ = aH

    def isLoopFadeIn(self):
        return self.loopFadeIn

    def setLoopFadeIn(self, aH):
        self.loopFadeIn = aH

    @staticmethod
    def loadMotion(aT: bytes):
        aN = Live2DMotion()
        aI = [0]
        aQ = len(aT)
        aN.yT_ = 0
        aJ = 0
        while aJ < aQ:
            aL = aT[aJ]
            aS = chr(aL)
            if aS == "\n" or aS == "\r":
                aJ += 1
                continue

            if aS == "#":
                while aJ < aQ:
                    if chr(aT[aJ]) == "\n" or chr(aT[aJ]) == "\r":
                        break
                    aJ += 1

                aJ += 1
                continue

            if aS == "":
                aV = aJ
                aK = -1
                while aJ < aQ:
                    aS = chr(aT[aJ])
                    if aS == "\r" or aS == "\n":
                        break

                    if aS == "=":
                        aK = aJ
                        break
                    aJ += 1

                aP = False
                if aK >= 0:
                    if aK == aV + 4 and chr(aT[aV + 1]) == "f" and chr(aT[aV + 2]) == "p" and chr(aT[aV + 3]) == "s":
                        aP = True

                    aJ = aK + 1
                    while aJ < aQ:
                        aS = chr(aT[aJ])
                        if aS == "\r" or aS == "\n":
                            break

                        if aS == "," or aS == " " or aS == "\t":
                            aJ += 1
                            continue

                        aM = UtString.strToFloat(aT, aQ, aJ, aI)
                        if aI[0] > 0:
                            if aP and 5 < aM < 121:
                                aN.D0_ = aM

                        aJ = aI[0]
                        aJ += 1

                while aJ < aQ:
                    if chr(aT[aJ]) == "\n" or chr(aT[aJ]) == "\r":
                        break
                    aJ += 1

                aJ += 1
                continue

            if (97 <= aL <= 122) or (65 <= aL <= 90) or aS == "_":
                aV = aJ
                aK = -1
                while aJ < aQ:
                    aS = chr(aT[aJ])
                    if aS == "\r" or aS == "\n":
                        break

                    if aS == "=":
                        aK = aJ
                        break
                    aJ += 1

                if aK >= 0:
                    aO = Motion()
                    if UtString.startswith(aT, aV, Live2DMotion.cs_):
                        aO.RP_ = Motion.hs_
                        aO._4P = UtString.createString(aT, aV, aK - aV)
                    else:
                        if UtString.startswith(aT, aV, Live2DMotion.ar_):
                            aO._4P = UtString.createString(aT, aV + 7, aK - aV - 7)
                            if UtString.startswith(aT, aV + 7, "ANCHOR_X"):
                                aO.RP_ = Motion.xs_
                            else:
                                if UtString.startswith(aT, aV + 7, "ANCHOR_Y"):
                                    aO.RP_ = Motion.us_
                                else:
                                    if UtString.startswith(aT, aV + 7, "SCALE_X"):
                                        aO.RP_ = Motion.qs_
                                    else:
                                        if UtString.startswith(aT, aV + 7, "SCALE_Y"):
                                            aO.RP_ = Motion.Ys_
                                        else:
                                            if UtString.startswith(aT, aV + 7, "AffineEnt"):
                                                aO.RP_ = Motion.ws_
                                            else:
                                                if UtString.startswith(aT, aV + 7, "Y"):
                                                    aO.RP_ = Motion.Ns_
                        else:
                            aO.RP_ = Motion.Fr_
                            aO._4P = UtString.createString(aT, aV, aK - aV)

                    aN.motions.append(aO)
                    aU = 0
                    aR = []
                    aJ = aK + 1
                    while aJ < aQ:
                        aS = chr(aT[aJ])
                        if aS == "\r" or aS == "\n":
                            break

                        if aS == "," or aS == " " or aS == "\t":
                            aJ += 1
                            continue

                        aM = UtString.strToFloat(aT, aQ, aJ, aI)
                        if aI[0] > 0:
                            aR.append(aM)
                            aU += 1
                            aH = aI[0]
                            if aH < aJ:
                                print("_n0 hi_ . @Live2DMotion loadMotion()\n")
                                break

                            aJ = aH - 1
                        aJ += 1

                    aO.I0_ = aR
                    if aU > aN.yT_:
                        aN.yT_ = aU

            aJ += 1

        aN.rr_ = int((1000 * aN.yT_) / aN.D0_)
        return aN
