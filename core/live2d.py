import math
import struct
import time


class IBaseContext:

    def __init__(self, ibaseData):
        self._IP = None
        self._JS = False
        self._AT = True
        self.ibaseData = ibaseData
        self.totalScale = 1
        self._7s = 1
        self.totalOpacity = 1

    def isAvailable(self):
        return self._AT and not self._JS

    def _hS(self, aH):
        self._AT = aH

    def _GT(self):
        return self.ibaseData

    def _l2(self, aH):
        self._IP = aH

    def getPartsIndex(self):
        return self._IP

    def _x2(self):
        return self._JS

    def _Ib(self, aH):
        self._JS = aH

    def getTotalScale(self):
        return self.totalScale

    def setTotalScale_notForClient(self, aH):
        self.totalScale = aH

    def getInterpolatedOpacity(self):
        return self._7s

    def setInterpolatedOpacity(self, aH):
        self._7s = aH

    def getTotalOpacity(self, aH=None):
        return self.totalOpacity

    def setTotalOpacity(self, aH):
        self.totalOpacity = aH


class ClippingManagerWebGL():
    CHANNEL_COUNT = 4
    RENDER_TEXTURE_USE_MIPMAP = False
    NOT_USED_FRAME = -100

    def __init__(self, aJ):
        self.clipContextList = Array()
        self.glcontext = aJ.gl
        self.dp_webgl = aJ
        self.curFrameNo = 0
        self.firstError_clipInNotUpdate = True
        self.colorBuffer = 0
        self.isInitGLFBFunc = False
        self.tmpBoundsOnModel = LDRectF()
        if len(Live2D.glContext) > len(Live2D.frameBuffers):
            self.curFrameNo = self.getMaskRenderTexture()
        else:
            pass

        self.tmpModelToViewMatrix = LDMatrix44()
        self.tmpMatrix2 = LDMatrix44()
        self.tmpMatrixForMask = LDMatrix44()
        self.tmpMatrixForDraw = LDMatrix44()
        self.CHANNEL_COLORS = Array()
        aI = o()
        aI = o()
        aI.r = 0
        aI.g = 0
        aI.b = 0
        aI.a = 1
        self.CHANNEL_COLORS.append(aI)
        aI = o()
        aI.r = 1
        aI.g = 0
        aI.b = 0
        aI.a = 0
        self.CHANNEL_COLORS.append(aI)
        aI = o()
        aI.r = 0
        aI.g = 1
        aI.b = 0
        aI.a = 0
        self.CHANNEL_COLORS.append(aI)
        aI = o()
        aI.r = 0
        aI.g = 0
        aI.b = 1
        aI.a = 0
        self.CHANNEL_COLORS.append(aI)
        for aH in range(0, len(self.CHANNEL_COLORS), 1):
            self.dp_webgl.setChannelFlagAsColor(aH, self.CHANNEL_COLORS[aH])

    def _L7(self):
        if self.tmpModelToViewMatrix:
            self.tmpModelToViewMatrix = None

        if self.tmpMatrix2:
            self.tmpMatrix2 = None

        if self.tmpMatrixForMask:
            self.tmpMatrixForMask = None

        if self.tmpMatrixForDraw:
            self.tmpMatrixForDraw = None

        if self.tmpBoundsOnModel:
            self.tmpBoundsOnModel = None

        if self.CHANNEL_COLORS:
            aH = len(self.CHANNEL_COLORS) - 1
            while aH >= 0:
                self.CHANNEL_COLORS.pop(aH)
                aH -= 1

            self.CHANNEL_COLORS = []

        self.releaseShader()

    def releaseShader(self):
        aI = len(Live2D.frameBuffers)
        for aH in range(0, aI, 1):
            self.gl.deleteFramebuffer(Live2D.frameBuffers[aH].framebuffer)

        Live2D.frameBuffers = []
        Live2D.glContext = []

    def init(self, aO, aN, aL):
        for aM in range(0, len(aN), 1):
            aH = aN[aM].getClipIDList()
            if aH is None:
                continue

            aJ = self.findSameClip(aH)
            if aJ is None:
                aJ = ClipContext(self, aO, aH)
                self.clipContextList.append(aJ)

            aI = aN[aM].getDrawDataID()
            aK = aO.getDrawDataIndex(aI)
            aJ.addClippedDrawData(aI, aK)
            aP = aL[aM]
            aP.clipBufPre_clipContext = aJ

    def getMaskRenderTexture(self):
        aH = self.dp_webgl.createFramebuffer()
        Live2D.frameBuffers[self.dp_webgl.glno] = aH
        return self.dp_webgl.glno

    def setupClip(self, a1, aQ):
        aK = 0
        for aO in range(0, len(self.clipContextList), 1):
            aP = self.clipContextList[aO]
            self.calcClippedDrawTotalBounds(a1, aP)
            if aP.isUsing:
                aK += 1

        if aK > 0:
            aM = aQ.gl.getParameter(aQ.gl.FRAMEBUFFER_BINDING)
            aW = Array(4)
            aW[0] = 0
            aW[1] = 0
            aW[2] = aQ.gl.width
            aW[3] = aQ.gl.height
            aQ.gl.viewport(0, 0, Live2D.clippingMaskBufferSize, Live2D.clippingMaskBufferSize)
            self.setupLayoutBounds(aK)
            aQ.gl.bindFramebuffer(aQ.gl.FRAMEBUFFER, Live2D.frameBuffers[self.curFrameNo].framebuffer)
            aQ.gl.clearColor(0, 0, 0, 0)
            aQ.gl.clear(aQ.gl.COLOR_BUFFER_BIT)
            for aO in range(0, len(self.clipContextList), 1):
                aP = self.clipContextList[aO]
                aT = aP.allClippedDrawRect
                aN = aP.layoutChannelNo
                aV = aP.layoutBounds
                aJ = 0.05
                self.tmpBoundsOnModel._jL(aT)
                self.tmpBoundsOnModel.expand(aT.width * aJ, aT.height * aJ)
                aZ = aV.width / self.tmpBoundsOnModel.width
                aY = aV.height / self.tmpBoundsOnModel.height
                self.tmpMatrix2.identity()
                self.tmpMatrix2.translate(-1, -1, 0)
                self.tmpMatrix2.scale(2, 2, 1)
                self.tmpMatrix2.translate(aV.x, aV.y, 0)
                self.tmpMatrix2.scale(aZ, aY, 1)
                self.tmpMatrix2.translate(-self.tmpBoundsOnModel.x, -self.tmpBoundsOnModel.y, 0)
                self.tmpMatrixForMask.setMatrix(self.tmpMatrix2.m)
                self.tmpMatrix2.identity()
                self.tmpMatrix2.translate(aV.x, aV.y, 0)
                self.tmpMatrix2.scale(aZ, aY, 1)
                self.tmpMatrix2.translate(-self.tmpBoundsOnModel.x, -self.tmpBoundsOnModel.y, 0)
                self.tmpMatrixForDraw.setMatrix(self.tmpMatrix2.m)
                aH = self.tmpMatrixForMask.getArray()
                for aX in range(0, 16, 1):
                    aP.matrixForMask[aX] = aH[aX]

                a0 = self.tmpMatrixForDraw.getArray()
                for aX in range(0, 16, 1):
                    aP.matrixForDraw[aX] = a0[aX]

                aS = len(aP.clippingMaskDrawIndexList)
                for aU in range(0, aS, 1):
                    aR = aP.clippingMaskDrawIndexList[aU]
                    aI = a1.getDrawData(aR)
                    aL = a1._C2(aR)
                    aQ.setClipBufPre_clipContextForMask(aP)
                    # print("setupClip", aI._gP.id)
                    aI.draw(aQ, a1, aL)

            aQ.gl.bindFramebuffer(aQ.gl.FRAMEBUFFER, aM)
            aQ.setClipBufPre_clipContextForMask(None)
            aQ.gl.viewport(aW[0], aW[1], aW[2], aW[3])

    def getColorBuffer(self):
        return self.colorBuffer

    def findSameClip(self, aK):
        for aN in range(0, len(self.clipContextList), 1):
            aO = self.clipContextList[aN]
            aH = len(aO.clipIDList)
            if aH != len(aK):
                continue

            aI = 0
            for aM in range(0, aH, 1):
                aL = aO.clipIDList[aM]
                for aJ in range(0, aH, 1):
                    if aK[aJ] == aL:
                        aI += 1
                        break

            if aI == aH:
                return aO

        return None

    def calcClippedDrawTotalBounds(self, a6, aV):
        aU = a6._Ri.getModelImpl().getCanvasWidth()
        a5 = a6._Ri.getModelImpl().getCanvasHeight()
        aJ = aU if aU > a5 else a5
        aT = aJ
        aR = aJ
        aS = 0
        aP = 0
        aL = len(aV.clippedDrawContextList)
        for aM in range(0, aL, 1):
            aW = aV.clippedDrawContextList[aM]
            aN = aW.drawDataIndex
            aK = a6._C2(aN)
            if aK._yo():
                aX = aK.getTransformedPoints()
                a4 = len(aX)
                aI = Float32Array(a4)
                aH = Float32Array(a4)
                aO = 0
                for a3 in range(DEF.VERTEX_OFFSET, a4, DEF.VERTEX_STEP):
                    aI[aO] = aX[a3]
                    aH[aO] = aX[a3 + 1]
                    aO += 1

                a2 = min(aI)
                a1 = min(aH)
                a0 = max(aI)
                aZ = max(aH)
                if a2 < aT:
                    aT = a2

                if a1 < aR:
                    aR = a1

                if a0 > aS:
                    aS = a0

                if aZ > aP:
                    aP = aZ

        if aT == aJ:
            aV.allClippedDrawRect.x = 0
            aV.allClippedDrawRect.y = 0
            aV.allClippedDrawRect.width = 0
            aV.allClippedDrawRect.height = 0
            aV.isUsing = False
        else:
            aQ = aS - aT
            aY = aP - aR
            aV.allClippedDrawRect.x = aT
            aV.allClippedDrawRect.y = aR
            aV.allClippedDrawRect.width = aQ
            aV.allClippedDrawRect.height = aY
            aV.isUsing = True

    def setupLayoutBounds(self, aQ):
        aI = aQ / ClippingManagerWebGL.CHANNEL_COUNT
        aP = aQ % ClippingManagerWebGL.CHANNEL_COUNT
        aI = int(aI)
        aP = int(aP)
        aH = 0
        for aJ in range(0, ClippingManagerWebGL.CHANNEL_COUNT, 1):
            aM = aI + (1 if aJ < aP else 0)
            if aM == 0:
                pass
            else:
                if aM == 1:
                    aL = self.clipContextList[aH]
                    aH += 1
                    aL.layoutChannelNo = aJ
                    aL.layoutBounds.x = 0
                    aL.layoutBounds.y = 0
                    aL.layoutBounds.width = 1
                    aL.layoutBounds.height = 1
                else:
                    if aM == 2:
                        for aO in range(0, aM, 1):
                            aN = aO % 2
                            aK = 0
                            aN = int(aN)
                            aL = self.clipContextList[aH]
                            aH += 1
                            aL.layoutChannelNo = aJ
                            aL.layoutBounds.x = aN * 0.5
                            aL.layoutBounds.y = 0
                            aL.layoutBounds.width = 0.5
                            aL.layoutBounds.height = 1
                    else:
                        if aM <= 4:
                            for aO in range(0, aM, 1):
                                aN = aO % 2
                                aK = aO / 2
                                aN = int(aN)
                                aK = int(aK)
                                aL = self.clipContextList[aH]
                                aH += 1
                                aL.layoutChannelNo = aJ
                                aL.layoutBounds.x = aN * 0.5
                                aL.layoutBounds.y = aK * 0.5
                                aL.layoutBounds.width = 0.5
                                aL.layoutBounds.height = 0.5
                        else:
                            if aM <= 9:
                                for aO in range(0, aM, 1):
                                    aN = aO % 3
                                    aK = aO / 3
                                    aN = int(aN)
                                    aK = int(aK)
                                    aL = self.clipContextList[aH]
                                    aH += 1
                                    aL.layoutChannelNo = aJ
                                    aL.layoutBounds.x = aN / 3
                                    aL.layoutBounds.y = aK / 3
                                    aL.layoutBounds.width = 1 / 3
                                    aL.layoutBounds.height = 1 / 3
                            else:
                                raise Exception("error in mask")


class ClipContext:

    def __init__(self, aH, aK, aI):
        self.clipIDList = Array()
        self.clipIDList = aI
        self.clippingMaskDrawIndexList = Array()
        for aJ in range(0, len(aI), 1):
            self.clippingMaskDrawIndexList.append(aK.getDrawDataIndex(aI[aJ]))

        self.clippedDrawContextList = Array()
        self.isUsing = True
        self.layoutChannelNo = 0
        self.layoutBounds = LDRectF()
        self.allClippedDrawRect = LDRectF()
        self.matrixForMask = Float32Array(16)
        self.matrixForDraw = Float32Array(16)
        self.owner = aH

    def addClippedDrawData(self, aJ, aI):
        aH = ClipDrawContext(aJ, aI)
        self.clippedDrawContextList.append(aH)


class ClipDrawContext:

    def __init__(self, aI, aH):
        self._gP = aI
        self.drawDataIndex = aH


class LDColor():

    def __init__(self):
        self.color = None


class AMotion():

    def __init__(self):
        self._dP = None
        self._eo = None
        self._V0 = None
        self._dP = 1000
        self._eo = 1000
        self._V0 = 1
        self._a0()

    def _a0(self):
        pass

    def setFadeIn(self, aH):
        self._dP = aH

    def setFadeOut(self, aH):
        self._eo = aH

    def _pT(self, aH):
        self._V0 = aH

    def getFadeOut(self):
        return self._eo

    def _4T(self):
        return self._eo

    def _mT(self):
        return self._V0

    def getDurationMSec(self):
        return -1

    def getLoopDurationMSec(self):
        return -1

    def updateParam(self, aJ, aN):
        if not aN._AT or aN._9L:
            return

        aL = UtSystem.getUserTimeMSec()
        if aN._z2 < 0:
            aN._z2 = aL
            aN._bs = aL
            aM = self.getDurationMSec()
            if aN._Do < 0:
                aN._Do = -1 if (aM <= 0) else aN._z2 + aM

        aI = self._V0
        aH = 1 if (self._dP == 0) else UtMotion._r2(((aL - aN._bs) / (self._dP)))
        aK = 1 if (self._eo == 0 or aN._Do < 0) else UtMotion._r2(((aN._Do - aL) / (self._eo)))
        aI = aI * aH * aK
        if not ((0 <= aI and aI <= 1)):
            print("### assert!! ### ")

        self.updateParamExe(aJ, aL, aI, aN)
        if aN._Do > 0 and aN._Do < aL:
            aN._9L = True

    def updateParamExe(self, aH, aI, aJ, aK):
        pass

    @staticmethod
    def _JT(aP, aN, aO):
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
        else:
            if aQ >= 1:
                return 1

        aS = aQ
        aI = aS * aS
        aH = aS * aI
        aT = aY * aH + aX * aI + aW * aS + aV
        return aT


class DebugTimerObj():

    def __init__(self):
        self.key = None
        self.startTimeMs = None


class LDRect():

    def __init__(self):
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def _8P(self):
        return 0.5 * (self.x + self.x + self.width)

    def _6P(self):
        return 0.5 * (self.y + self.y + self.height)

    def _EL(self):
        return self.x + self.width

    def _5T(self):
        return self.y + self.height


class S:
    pass


class ModelImpl():
    INSTANCE_COUNT = 0

    def __init__(self):
        self.paramDefSet = None
        self.partsDataList = None
        self.canvasWidth = 400
        self.canvasHeight = 400
        ModelImpl.INSTANCE_COUNT += 1

    def initDirect(self):
        if self.paramDefSet is None:
            self.paramDefSet = ParamDefSet()

        if self.partsDataList is None:
            self.partsDataList = Array()

    def getCanvasWidth(self):
        return self.canvasWidth

    def getCanvasHeight(self):
        return self.canvasHeight

    def read(self, br):
        self.paramDefSet = br._nP()
        self.partsDataList = br._nP()
        self.canvasWidth = br._6L()
        self.canvasHeight = br._6L()

    def _6S(self, aH):
        self.partsDataList.append(aH)

    def getPartsDataList(self):
        return self.partsDataList

    def _E2(self):
        return self.paramDefSet


class PhysicsHair:

    def __init__(self):
        self.p1 = PhysicsPoint()
        self.p2 = PhysicsPoint()
        self._Fo = 0
        self._Db = 0
        self._L2 = 0
        self._M2 = 0
        self._ks = 0
        self._9b = 0
        self._iP = 0
        self._iT = 0
        self._lL = Array()
        self._qP = Array()
        self.setup(0.3, 0.5, 0.1)

    def setup(self, aJ=None, aI=None, aH=None):
        self._ks = self._Yb()
        self.p2._xT()
        if aH is not None:
            self._Fo = aJ
            self._L2 = aI
            self.p1._p = aH
            self.p2._p = aH
            self.p2.y = aJ
            self.setup()

    def getPhysicsPoint1(self):
        return self.p1

    def getPhysicsPoint2(self):
        return self.p2

    def _qr(self):
        return self._Db

    def _pr(self, aH):
        self._Db = aH

    def _5r(self):
        return self._M2

    def _Cs(self):
        return self._9b

    def _Yb(self):
        return (-180 * (math.atan2(self.p1.x - self.p2.x, -(self.p1.y - self.p2.y))) / math.pi)

    def addSrcParam(self, aJ, aH, aL, aI):
        aK = PhysicsSrc(aJ, aH, aL, aI)
        self._lL.append(aK)

    def addTargetParam(self, aJ, aH, aK, aI):
        aL = PhysicsTarget(aJ, aH, aK, aI)
        self._qP.append(aL)

    def update(self, aI, aL):
        if self._iP == 0:
            self._iP = self._iT = aL
            self._Fo = (math.sqrt((self.p1.x - self.p2.x) * (self.p1.x - self.p2.x) + (self.p1.y - self.p2.y) * (
                    self.p1.y - self.p2.y)))
            return

        aK = (aL - self._iT) / 1000
        if aK != 0:
            for aJ in range(len(self._lL) - 1, 0 - 1, -1):
                # aJ = len(self._lL) - 1
                # while aJ >= 0:
                aM = self._lL[aJ]
                aM._oP(aI, self)
                # aJ -= 1

            self._oo(aI, aK)
            self._M2 = self._Yb()
            self._9b = (self._M2 - self._ks) / aK
            self._ks = self._M2

        for aJ in range(len(self._qP) - 1, 0 - 1, -1):
            # aJ = len(self._qP) - 1
            # while aJ >= 0:
            aH = self._qP[aJ]
            aH._YS(aI, self)
            # aJ -= 1

        self._iT = aL

    def _oo(self, aN, aI):
        if aI < 0.033:
            aI = 0.033

        aU = 1 / aI
        self.p1.vx = (self.p1.x - self.p1._s0) * aU
        self.p1.vy = (self.p1.y - self.p1._70) * aU
        self.p1.ax = (self.p1.vx - self.p1._7L) * aU
        self.p1.ay = (self.p1.vy - self.p1._HL) * aU
        self.p1.fx = self.p1.ax * self.p1._p
        self.p1.fy = self.p1.ay * self.p1._p
        self.p1._xT()
        aM = -(math.atan2((self.p1.y - self.p2.y), self.p1.x - self.p2.x))
        aL = None
        aV = None
        aR = math.cos(aM)
        aH = math.sin(aM)
        aW = 9.8 * self.p2._p
        aQ = (self._Db * UtMath._bS)
        aP = (aW * math.cos(aM - aQ))
        aL = (aP * aH)
        aV = (aP * aR)
        aK = (-self.p1.fx * aH * aH)
        aT = (-self.p1.fy * aH * aR)
        aJ = ((-self.p2.vx * self._L2))
        aS = ((-self.p2.vy * self._L2))
        self.p2.fx = ((aL + aK + aJ))
        self.p2.fy = ((aV + aT + aS))
        self.p2.ax = self.p2.fx / self.p2._p
        self.p2.ay = self.p2.fy / self.p2._p
        self.p2.vx += self.p2.ax * aI
        self.p2.vy += self.p2.ay * aI
        self.p2.x += self.p2.vx * aI
        self.p2.y += self.p2.vy * aI
        aO = (math.sqrt(
            (self.p1.x - self.p2.x) * (self.p1.x - self.p2.x) + (self.p1.y - self.p2.y) * (self.p1.y - self.p2.y)))
        self.p2.x = self.p1.x + self._Fo * (self.p2.x - self.p1.x) / aO
        self.p2.y = self.p1.y + self._Fo * (self.p2.y - self.p1.y) / aO
        self.p2.vx = (self.p2.x - self.p2._s0) * aU
        self.p2.vy = (self.p2.y - self.p2._70) * aU
        self.p2._xT()

    Src = type('', (), {
        "SRC_TO_X": "SRC_TO_X",
        "SRC_TO_Y": "SRC_TO_Y",
        "SRC_TO_G_ANGLE": "SRC_TO_G_ANGLE",
    })()

    Target = type('', (), {
        "TARGET_FROM_ANGLE": "TARGET_FROM_ANGLE",
        "TARGET_FROM_ANGLE_V": "TARGET_FROM_ANGLE_V",
    })()


class PhysicsPoint():

    def __init__(self):
        self._p = 1
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        self.fx = 0
        self.fy = 0
        self._s0 = 0
        self._70 = 0
        self._7L = 0
        self._HL = 0

    def _xT(self):
        self._s0 = self.x
        self._70 = self.y
        self._7L = self.vx
        self._HL = self.vy


class IPhysicsSrc():

    def __init__(self, aJ, aI, aH):
        self._wL = None
        self.scale = None
        self._V0 = None
        self._wL = aJ
        self.scale = aI
        self._V0 = aH

    def _oP(self, aI, aH):
        pass


class PhysicsSrc(IPhysicsSrc):

    def __init__(self, aJ, aK, aI, aH):
        super().__init__(aK, aI, aH)
        self._tL = None
        self._tL = aJ

    def _oP(self, aJ, aH):
        aK = self.scale * aJ.getParamFloat(self._wL)
        aL = aH.getPhysicsPoint1()

        switch = self._tL
        if switch == PhysicsHair.Src.SRC_TO_X:
            aL.x = aL.x + (aK - aL.x) * self._V0
        elif switch == PhysicsHair.Src.SRC_TO_Y:
            aL.y = aL.y + (aK - aL.y) * self._V0
        elif switch == PhysicsHair.Src.SRC_TO_G_ANGLE:
            aI = aH._qr()
            aI = aI + (aK - aI) * self._V0
            aH._pr(aI)


class IPhysicsTarget():

    def __init__(self, aJ, aI, aH):
        self._wL = None
        self.scale = None
        self._V0 = None
        self._wL = aJ
        self.scale = aI
        self._V0 = aH

    def _YS(self, aI, aH):
        pass


class PhysicsTarget(IPhysicsTarget):

    def __init__(self, aI, aK, aJ, aH):
        super().__init__(aK, aJ, aH)
        self._YP = None
        self._YP = aI

    def _YS(self, aI, aH):

        _switch_9328 = self._YP

        if _switch_9328 == PhysicsHair.Target.TARGET_FROM_ANGLE:
            aI.setParamFloat(self._wL, self.scale * aH._5r(), self._V0)
        elif _switch_9328 == PhysicsHair.Target.TARGET_FROM_ANGLE_V:
            aI.setParamFloat(self._wL, self.scale * aH._Cs(), self._V0)


class AffineEnt:

    def __init__(self):
        self._fL = 0
        self._gL = 0
        self._B0 = 1
        self._z0 = 1
        self._qT = 0
        self.reflectX = False
        self.reflectY = False

    def init(self, aH):
        self._fL = aH._fL
        self._gL = aH._gL
        self._B0 = aH._B0
        self._z0 = aH._z0
        self._qT = aH._qT
        self.reflectX = aH.reflectX
        self.reflectY = aH.reflectY

    def read(self, aH):
        self._fL = aH.readFloat32()
        self._gL = aH.readFloat32()
        self._B0 = aH.readFloat32()
        self._z0 = aH.readFloat32()
        self._qT = aH.readFloat32()
        if aH.getFormatVersion() >= FileFormat2.LIVE2D_FORMAT_VERSION_V2_10_SDK2:
            self.reflectX = aH._po()
            self.reflectY = aH._po()

    def _e(self):
        pass


class UtVector():
    @staticmethod
    def _ni(aL, aJ, aR, aQ, aK, aI, aH, aS, aN):
        aM = (aH * aI - aS * aK)
        if aM == 0:
            return None
        else:
            aO = ((aL - aR) * aI - (aJ - aQ) * aK) / aM
            aP = None
            if aK != 0:
                aP = (aL - aR - aO * aH) / aK
            else:
                aP = (aJ - aQ - aO * aS) / aI

            if math.isnan(aP):
                aP = (aL - aR - aO * aH) / aK
                if math.isnan(aP):
                    aP = (aJ - aQ - aO * aS) / aI

                if math.isnan(aP):
                    print("a is NaN @UtVector#_ni() ")
                    print("v1x : " + aK)
                    print("v1x != 0 ? " + (aK != 0))

            if aN == None:
                return Array(aP, aO)
            else:
                aN[0] = aP
                aN[1] = aO
                return aN


class LDRectF():

    def __init__(self):
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def _8P(self):
        return self.x + 0.5 * self.width

    def _6P(self):
        return self.y + 0.5 * self.height

    def _EL(self):
        return self.x + self.width

    def _5T(self):
        return self.y + self.height

    def contains(self, aH, aI):
        return self.x <= self.x and self.y <= self.y and (self.x <= self.x + self.width) and (
                self.y <= self.y + self.height)

    def expand(self, aH, aI):
        self.x -= aH
        self.y -= aI
        self.width += aH * 2
        self.height += aI * 2

    def _jL(self, aH):
        self.x = aH.x
        self.y = aH.y
        self.width = aH.width
        self.height = aH.height


class aG():
    @staticmethod
    def _Z2(bb, bo, bp, a2):
        a1 = bo._Q2(bb, bp)
        a3 = bb._vs()
        ba = bb._Tr()
        bo._zr(a3, ba, a1)
        if a1 <= 0:
            return a2[a3[0]]
        else:
            if a1 == 1:
                bj = a2[a3[0]]
                bi = a2[a3[1]]
                a9 = ba[0]
                return int(bj + (bi - bj) * a9)
            else:
                if a1 == 2:
                    bj = a2[a3[0]]
                    bi = a2[a3[1]]
                    a0 = a2[a3[2]]
                    aZ = a2[a3[3]]
                    a9 = ba[0]
                    a8 = ba[1]
                    br = int(bj + (bi - bj) * a9)
                    bq = int(a0 + (aZ - a0) * a9)
                    return int(br + (bq - br) * a8)
                else:
                    if a1 == 3:
                        aP = a2[a3[0]]
                        aO = a2[a3[1]]
                        bn = a2[a3[2]]
                        bm = a2[a3[3]]
                        aK = a2[a3[4]]
                        aJ = a2[a3[5]]
                        bg = a2[a3[6]]
                        bf = a2[a3[7]]
                        a9 = ba[0]
                        a8 = ba[1]
                        a6 = ba[2]
                        bj = int(aP + (aO - aP) * a9)
                        bi = int(bn + (bm - bn) * a9)
                        a0 = int(aK + (aJ - aK) * a9)
                        aZ = int(bg + (bf - bg) * a9)
                        br = int(bj + (bi - bj) * a8)
                        bq = int(a0 + (aZ - a0) * a8)
                        return int(br + (bq - br) * a6)
                    else:
                        if a1 == 4:
                            aT = a2[a3[0]]
                            aS = a2[a3[1]]
                            bu = a2[a3[2]]
                            bt = a2[a3[3]]
                            aN = a2[a3[4]]
                            aM = a2[a3[5]]
                            bl = a2[a3[6]]
                            bk = a2[a3[7]]
                            be = a2[a3[8]]
                            bc = a2[a3[9]]
                            aX = a2[a3[10]]
                            aW = a2[a3[11]]
                            a7 = a2[a3[12]]
                            a5 = a2[a3[13]]
                            aR = a2[a3[14]]
                            aQ = a2[a3[15]]
                            a9 = ba[0]
                            a8 = ba[1]
                            a6 = ba[2]
                            a4 = ba[3]
                            aP = int(aT + (aS - aT) * a9)
                            aO = int(bu + (bt - bu) * a9)
                            bn = int(aN + (aM - aN) * a9)
                            bm = int(bl + (bk - bl) * a9)
                            aK = int(be + (bc - be) * a9)
                            aJ = int(aX + (aW - aX) * a9)
                            bg = int(a7 + (a5 - a7) * a9)
                            bf = int(aR + (aQ - aR) * a9)
                            bj = int(aP + (aO - aP) * a8)
                            bi = int(bn + (bm - bn) * a8)
                            a0 = int(aK + (aJ - aK) * a8)
                            aZ = int(bg + (bf - bg) * a8)
                            br = int(bj + (bi - bj) * a6)
                            bq = int(a0 + (aZ - a0) * a6)
                            return int(br + (bq - br) * a4)
                        else:
                            aV = 1 << a1
                            aY = Float32Array(aV)
                            for bh in range(0, aV, 1):
                                aI = bh
                                aH = 1
                                for aL in range(0, a1, 1):
                                    aH *= (1 - ba[aL]) if (aI % 2 == 0) else ba[aL]
                                    aI /= 2

                                aY[bh] = aH

                            bs = Float32Array(aV)
                            for aU in range(0, aV, 1):
                                bs[aU] = a2[a3[aU]]

                            bd = 0
                            for aU in range(0, aV, 1):
                                bd += aY[aU] * bs[aU]

                            return int(bd + 0.5)

    @staticmethod
    def _br(ba, bo, bp, bg):
        a1 = bo._Q2(ba, bp)
        a2 = ba._vs()
        a9 = ba._Tr()
        bo._zr(a2, a9, a1)
        if a1 <= 0:
            return bg[a2[0]]
        else:
            if a1 == 1:
                bj = bg[a2[0]]
                bi = bg[a2[1]]
                a8 = a9[0]
                return bj + (bi - bj) * a8
            else:
                if a1 == 2:
                    bj = bg[a2[0]]
                    bi = bg[a2[1]]
                    a0 = bg[a2[2]]
                    aZ = bg[a2[3]]
                    a8 = a9[0]
                    a7 = a9[1]
                    return (1 - a7) * (bj + (bi - bj) * a8) + a7 * (a0 + (aZ - a0) * a8)
                else:
                    if a1 == 3:
                        aP = bg[a2[0]]
                        aO = bg[a2[1]]
                        bn = bg[a2[2]]
                        bm = bg[a2[3]]
                        aK = bg[a2[4]]
                        aJ = bg[a2[5]]
                        bf = bg[a2[6]]
                        be = bg[a2[7]]
                        a8 = a9[0]
                        a7 = a9[1]
                        a5 = a9[2]
                        return (1 - a5) * ((1 - a7) * (aP + (aO - aP) * a8) + a7 * (bn + (bm - bn) * a8)) + a5 * (
                                (1 - a7) * (aK + (aJ - aK) * a8) + a7 * (bf + (be - bf) * a8))
                    else:
                        if a1 == 4:
                            aT = bg[a2[0]]
                            aS = bg[a2[1]]
                            bs = bg[a2[2]]
                            br = bg[a2[3]]
                            aN = bg[a2[4]]
                            aM = bg[a2[5]]
                            bl = bg[a2[6]]
                            bk = bg[a2[7]]
                            bd = bg[a2[8]]
                            bb = bg[a2[9]]
                            aX = bg[a2[10]]
                            aW = bg[a2[11]]
                            a6 = bg[a2[12]]
                            a4 = bg[a2[13]]
                            aR = bg[a2[14]]
                            aQ = bg[a2[15]]
                            a8 = a9[0]
                            a7 = a9[1]
                            a5 = a9[2]
                            a3 = a9[3]
                            return (1 - a3) * ((1 - a5) * (
                                    (1 - a7) * (aT + (aS - aT) * a8) + a7 * (bs + (br - bs) * a8)) + a5 * (
                                                       (1 - a7) * (aN + (aM - aN) * a8) + a7 * (
                                                       bl + (bk - bl) * a8))) + a3 * ((1 - a5) * (
                                    (1 - a7) * (bd + (bb - bd) * a8) + a7 * (aX + (aW - aX) * a8)) + a5 * (
                                                                                              (1 - a7) * (
                                                                                              a6 + (
                                                                                              a4 - a6) * a8) + a7 * (
                                                                                                      aR + (
                                                                                                      aQ - aR) * a8)))
                        else:
                            aV = 1 << a1
                            aY = Float32Array(aV)
                            for bh in range(0, aV, 1):
                                aI = bh
                                aH = 1
                                for aL in range(0, a1, 1):
                                    aH *= (1 - a9[aL]) if (aI % 2 == 0) else a9[aL]
                                    aI /= 2

                                aY[bh] = aH

                            bq = Float32Array(aV)
                            for aU in range(0, aV, 1):
                                bq[aU] = bg[a2[aU]]

                            bc = 0
                            for aU in range(0, aV, 1):
                                bc += aY[aU] * bq[aU]

                            return bc

    @staticmethod
    def _Vr(bV, bW, a5, aI, bC, a3, bX, bH):
        aN = bW._Q2(bV, a5)
        bw = bV._vs()
        a2 = bV._Tr()
        bW._zr(bw, a2, aN)
        aJ = aI * 2
        aQ = bX
        if aN <= 0:
            bI = bw[0]
            bq = bC[bI]
            if bH == 2 and bX == 0:
                UtSystem._jT(bq, 0, a3, 0, aJ)
            else:
                bt = 0
                while bt < aJ:
                    a3[aQ] = bq[bt]
                    bt += 1
                    a3[aQ + 1] = bq[bt]
                    bt += 1
                    aQ += bH
        else:
            if aN == 1:
                bq = bC[bw[0]]
                bp = bC[bw[1]]
                b3 = a2[0]
                bT = 1 - b3
                bt = 0
                # for (bt = 0; bt < aJ;):
                while bt < aJ:
                    a3[aQ] = bq[bt] * bT + bp[bt] * b3
                    bt += 1
                    a3[aQ + 1] = bq[bt] * bT + bp[bt] * b3
                    bt += 1
                    aQ += bH
            else:
                if aN == 2:
                    bq = bC[bw[0]]
                    bp = bC[bw[1]]
                    aZ = bC[bw[2]]
                    aY = bC[bw[3]]
                    b3 = a2[0]
                    b1 = a2[1]
                    bT = 1 - b3
                    bP = 1 - b1
                    b2 = bP * bT
                    b0 = bP * b3
                    bM = b1 * bT
                    bL = b1 * b3
                    bt = 0
                    while bt < aJ:
                        a3[aQ] = b2 * bq[bt] + b0 * bp[bt] + bM * aZ[bt] + bL * aY[bt]
                        bt += 1
                        a3[aQ + 1] = b2 * bq[bt] + b0 * bp[bt] + bM * aZ[bt] + bL * aY[bt]
                        bt += 1
                        aQ += bH
                else:
                    if aN == 3:
                        ba = bC[bw[0]]
                        a9 = bC[bw[1]]
                        aP = bC[bw[2]]
                        aO = bC[bw[3]]
                        a6 = bC[bw[4]]
                        a4 = bC[bw[5]]
                        aL = bC[bw[6]]
                        aK = bC[bw[7]]
                        b3 = a2[0]
                        b1 = a2[1]
                        bZ = a2[2]
                        bT = 1 - b3
                        bP = 1 - b1
                        bN = 1 - bZ
                        b8 = bN * bP * bT
                        b7 = bN * bP * b3
                        bU = bN * b1 * bT
                        bS = bN * b1 * b3
                        b6 = bZ * bP * bT
                        b5 = bZ * bP * b3
                        bQ = bZ * b1 * bT
                        bO = bZ * b1 * b3
                        bt = 0
                        while bt < aJ:
                            a3[aQ] = b8 * ba[bt] + b7 * a9[bt] + bU * aP[bt] + bS * aO[bt] + b6 * a6[bt] + b5 * a4[
                                bt] + bQ * aL[bt] + bO * aK[bt]
                            bt += 1
                            a3[aQ + 1] = b8 * ba[bt] + b7 * a9[bt] + bU * aP[bt] + bS * aO[bt] + b6 * a6[bt] + b5 * a4[
                                bt] + bQ * aL[bt] + bO * aK[bt]
                            bt += 1
                            aQ += bH
                    else:
                        if aN == 4:
                            bD = bC[bw[0]]
                            bB = bC[bw[1]]
                            bo = bC[bw[2]]
                            bm = bC[bw[3]]
                            by = bC[bw[4]]
                            bx = bC[bw[5]]
                            be = bC[bw[6]]
                            bd = bC[bw[7]]
                            bG = bC[bw[8]]
                            bE = bC[bw[9]]
                            bv = bC[bw[10]]
                            bu = bC[bw[11]]
                            bA = bC[bw[12]]
                            bz = bC[bw[13]]
                            bn = bC[bw[14]]
                            bl = bC[bw[15]]
                            b3 = a2[0]
                            b1 = a2[1]
                            bZ = a2[2]
                            bY = a2[3]
                            bT = 1 - b3
                            bP = 1 - b1
                            bN = 1 - bZ
                            bK = 1 - bY
                            bk = bK * bN * bP * bT
                            bi = bK * bN * bP * b3
                            aW = bK * bN * b1 * bT
                            aV = bK * bN * b1 * b3
                            bc = bK * bZ * bP * bT
                            bb = bK * bZ * bP * b3
                            aS = bK * bZ * b1 * bT
                            aR = bK * bZ * b1 * b3
                            bs = bY * bN * bP * bT
                            br = bY * bN * bP * b3
                            a1 = bY * bN * b1 * bT
                            a0 = bY * bN * b1 * b3
                            bh = bY * bZ * bP * bT
                            bf = bY * bZ * bP * b3
                            aU = bY * bZ * b1 * bT
                            aT = bY * bZ * b1 * b3
                            bt = 0
                            while bt < aJ:
                                # for (bt = 0; bt < aJ;):
                                a3[aQ] = bk * bD[bt] + bi * bB[bt] + aW * bo[bt] + aV * bm[bt] + bc * by[bt] + bb * bx[
                                    bt] + aS * be[bt] + aR * bd[bt] + bs * bG[bt] + br * bE[bt] + a1 * bv[bt] + a0 * bu[
                                             bt] + bh * bA[bt] + bf * bz[bt] + aU * bn[bt] + aT * bl[bt]
                                bt += 1
                                a3[aQ + 1] = bk * bD[bt] + bi * bB[bt] + aW * bo[bt] + aV * bm[bt] + bc * by[bt] + bb * \
                                             bx[bt] + aS * be[bt] + aR * bd[bt] + bs * bG[bt] + br * bE[bt] + a1 * bv[
                                                 bt] + a0 * bu[bt] + bh * bA[bt] + bf * bz[bt] + aU * bn[bt] + aT * bl[
                                                 bt]
                                bt += 1
                                aQ += bH
                        else:
                            b4 = 1 << aN
                            bJ = Float32Array(b4)
                            for bj in range(0, b4, 1):
                                aH = bj
                                aM = 1
                                for bF in range(0, aN, 1):
                                    aM *= (1 - a2[bF]) if (aH % 2 == 0) else a2[bF]
                                    aH /= 2

                                bJ[bj] = aM

                            bg = Float32Array(b4)
                            for aX in range(0, b4, 1):
                                bg[aX] = bC[bw[aX]]

                            bt = 0
                            while bt < aJ:
                                a8 = 0
                                a7 = 0
                                bR = bt + 1
                                for aX in range(0, b4, 1):
                                    a8 += bJ[aX] * bg[aX][bt]
                                    a7 += bJ[aX] * bg[aX][bR]

                                bt += 2
                                a3[aQ] = a8
                                a3[aQ + 1] = a7
                                aQ += bH


class LDPointF():

    def __init__(self):
        self.x = None
        self.y = None


class IDrawData1():
    _ur = -2
    _ES = 500
    _wb = 2
    _8S = 3
    _52 = _ES
    _R2 = _ES

    def __init__(self):
        self._gP = None
        self._dr = None
        self._GS = None
        self._qb = None
        self._Lb = None
        self._mS = None
        self.clipID = None
        self.clipIDList = Array()

    def convertClipIDForV2_11(self, aI):
        aH = []
        if aI == None:
            return None

        if len(aI.id) == 0:
            return None

        # if ! /, /.test(aI):
        if not aI.id.find(','):
            aH.append(aI.id)
            return aH

        aH = aI.id.split(",")
        return aH

    def read(self, aH):
        self._gP = aH._nP()
        self._dr = aH._nP()
        self._GS = aH._nP()
        self._qb = aH._6L()
        self._Lb = aH._cS()
        self._mS = aH._Tb()
        if aH.getFormatVersion() >= FileFormat2._T7:
            self.clipID = aH._nP()
            self.clipIDList = self.convertClipIDForV2_11(self.clipID)
        else:
            self.clipIDList = []

        self._MS(self._Lb)

    def getClipIDList(self):
        return self.clipIDList

    def init(self, aH):
        pass

    def setupInterpolate(self, aH, aI):
        aI._IS[0] = False
        aI._Us = aG._Z2(aH, self._GS, aI._IS, self._Lb)
        if Live2D._Zs:
            pass
        else:
            if aI._IS[0]:
                return

        aI._7s = aG._br(aH, self._GS, aI._IS, self._mS)

    def setupTransform(self, aH, aI):
        pass

    def getDrawDataID(self):
        return self._gP

    def _j2(self, aH):
        self._gP = aH

    def getOpacity(self, aH, aI):
        return aI._7s

    def _zS(self, aH, aI):
        return aI._Us

    def _MS(self, aJ):
        for aI in range(len(aJ) - 1, -1, -1):
            aH = aJ[aI]
            if aH < IDrawData1._52:
                IDrawData1._52 = aH
            else:
                if aH > IDrawData1._R2:
                    IDrawData1._R2 = aH

    def getTargetBaseDataID(self):
        return self._dr

    def _gs(self, aH):
        self._dr = aH

    def _32(self):
        return (self._dr != None and (self._dr != BaseDataID._2o()))

    def preDraw(self, aJ, aH, aI):
        pass

    def draw(self, aJ, aH, aI):
        pass

    def getType(self):
        pass

    def _B2(self, aI, aH, aJ):
        pass

    @staticmethod
    def _or():
        return IDrawData1._52

    @staticmethod
    def _Pr():
        return IDrawData1._R2


class DrawParam:
    _ps = 32
    CLIPPING_PROCESS_NONE = 0
    CLIPPING_PROCESS_OVERWRITE_ALPHA = 1
    CLIPPING_PROCESS_MULTIPLY_ALPHA = 2
    CLIPPING_PROCESS_DRAW = 3
    CLIPPING_PROCESS_CLEAR_ALPHA = 4

    def __init__(self):
        self._Eb = DrawParam._ps
        self._lT = 1
        self._C0 = 1
        self._tT = 1
        self._WL = 1
        self.culling = False
        self.matrix4x4 = Float32Array(16)
        self.premultipliedAlpha = False
        self.anisotropy = 0
        self.clippingProcess = DrawParam.CLIPPING_PROCESS_NONE
        self.clipBufPre_clipContextMask = None
        self.clipBufPre_clipContextDraw = None
        self.CHANNEL_COLORS = {}

    def setChannelFlagAsColor(self, aH, aI):
        self.CHANNEL_COLORS[aH] = aI

    def getChannelFlagAsColor(self, aY):
        return self.CHANNEL_COLORS[aY]

    def _ZT(self):
        pass

    def _Uo(self, aM, aK, aJ, aL, aN, aI, aH):
        pass

    def _Rs(self):
        return -1

    def _Ds(self, aH):
        pass

    def _WP(self, aH):
        self.culling = aH

    def setMatrix(self, aH):
        for aI in range(0, 16, 1):
            self.matrix4x4[aI] = aH[aI]

    def _IT(self):
        return self.matrix4x4

    def setPremultipliedAlpha(self, aH):
        self.premultipliedAlpha = aH

    def isPremultipliedAlpha(self):
        return self.premultipliedAlpha

    def setAnisotropy(self, aH):
        self.anisotropy = aH

    def getAnisotropy(self):
        return self.anisotropy

    def getClippingProcess(self):
        return self.clippingProcess

    def setClippingProcess(self, aH):
        self.clippingProcess = aH

    def setClipBufPre_clipContextForMask(self, aH):
        self.clipBufPre_clipContextMask = aH

    def getClipBufPre_clipContextMask(self):
        return self.clipBufPre_clipContextMask

    def setClipBufPre_clipContextForDraw(self, aH):
        self.clipBufPre_clipContextDraw = aH

    def getClipBufPre_clipContextDraw(self):
        return self.clipBufPre_clipContextDraw


class o:

    def __init__(self):
        self.a = 1
        self.r = 1
        self.g = 1
        self.b = 1
        self.scale = 1
        self._ho = 1
        self.blendMode = Live2D.L2D_COLOR_BLEND_MODE_MULT


class IBaseData:
    _ur = -2
    _c2 = 1
    _b_ = 2

    def __init__(self):
        self._kP = None
        self._dr = None
        self._Ai = True
        self._mS = None

    def read(self, aH):
        self._kP = aH._nP()
        self._dr = aH._nP()

    def readV2_opacity(self, aH):
        if aH.getFormatVersion() >= FileFormat2.LIVE2D_FORMAT_VERSION_V2_10_SDK2:
            self._mS = aH._Tb()

    def init(self, aH):
        pass

    def setupInterpolate(self, aI, aH):
        pass

    def interpolateOpacity(self, aJ, aK, aI, aH):
        if self._mS is None:
            aI.setInterpolatedOpacity(1)
        else:
            aI.setInterpolatedOpacity(aG._br(aJ, aK, aH, self._mS))

    def setupTransform(self, aI, aH):
        pass

    def _nb(self, aL, aK, aM, aH, aI, aJ, aN):
        pass

    def getType(self):
        pass

    def _gs(self, aH):
        self._dr = aH

    def _a2(self, aH):
        self._kP = aH

    def getTargetBaseDataID(self):
        return self._dr

    def getBaseDataID(self):
        return self._kP

    def needTransform(self):
        return (self._dr != None and (self._dr != BaseDataID._2o()))


class UtSystem():
    _W2 = 0
    _CS = _W2

    @staticmethod
    def isBigEndian():
        return True

    @staticmethod
    def wait(duration):
        try:
            startTime = UtSystem.getTimeMSec()
            while UtSystem.getTimeMSec() - startTime < duration:
                pass

        except Exception as e:
            print(e)

    @staticmethod
    def getUserTimeMSec():
        return UtSystem.getSystemTimeMSec() if (UtSystem._CS == UtSystem._W2) else UtSystem._CS

    @staticmethod
    def setUserTimeMSec(aH):
        UtSystem._CS = aH

    @staticmethod
    def updateUserTimeMSec():
        UtSystem._CS = UtSystem.getSystemTimeMSec()
        return UtSystem._CS

    @staticmethod
    def getTimeMSec():
        return time.time() * 1000

    @staticmethod
    def getSystemTimeMSec():
        return time.time() * 1000

    @staticmethod
    def _jT(aM, aJ, aI, aL, aH):
        for aK in range(0, aH, 1):
            aI[aL + aK] = aM[aJ + aK]


class ParamPivots:
    _ds = -2

    def __init__(self):
        self._VP = 0
        self._wL = None
        self._GP = None
        self._8o = ParamPivots._ds
        self._2r = -1
        self._O2 = 0
        self._ri = 0

    def read(self, aH):
        self._wL = aH._nP()
        self._VP = aH._6L()
        self._GP = aH._nP()

    def getParamIndex(self, aH):
        if self._2r != aH:
            self._8o = ParamPivots._ds

        return self._8o

    def _Pb(self, aI, aH):
        self._8o = aI
        self._2r = aH

    def getParamID(self):
        return self._wL

    def _yP(self, aH):
        self._wL = aH

    def _N2(self):
        return self._VP

    def _d2(self):
        return self._GP

    def _t2(self, aI, aH):
        self._VP = aI
        self._GP = aH

    def _Lr(self):
        return self._O2

    def _wr(self, aH):
        self._O2 = aH

    def _SL(self):
        return self._ri

    def _AL(self, aH):
        self._ri = aH


class UtString:
    @staticmethod
    def startswith(aJ, aL, aK):
        # aH = aL + aK.length
        aH = aL + len(aK)
        if aH >= len(aJ):
            return False

        # for (aI = aL; aI < aH; aI++):
        for aI in range(aL, aH, 1):
            if UtString.getChar(aJ, aI) != aK[aI - aL]:
                return False

        return True

    @staticmethod
    def getChar(aI, aH):
        return aI[aH]

    @staticmethod
    def createString(aM, aL, aJ):
        return aM[aL:aL + aJ].decode("utf-8")

    @staticmethod
    def strToFloat(aP, aM, aR, aK):
        result = 0
        _n = 10
        _p = False
        neg = chr(aP[aR]) == '-'
        if neg:
            aR += 1
        while aR < aM:
            c = chr(aP[aR])
            if '0' <= c <= '9':
                if _p:
                    result += float(c) / _n
                    _n *= 10
                else:
                    result = result * 10 + eval(c)
            elif c == '.':
                _p = True
            else:
                break

            aR += 1
        if neg:
            result = -result
        aK[0] = aR
        return result

class PivotManager:

    def __init__(self):
        self._Ob = None

    def _zP(self):
        self._Ob = Array()

    def read(self, aH):
        self._Ob = aH._nP()

    def _Ur(self, aK):
        if aK._WS():
            return True

        aH = aK._v2()
        # for (aJ = len(self._Ob) - 1; aJ >= 0; --aJ):
        for aJ in range(len(self._Ob) - 1, -1, -1):
            aI = self._Ob[aJ].getParamIndex(aH)
            if aI == ParamPivots._ds:
                aI = aK.getParamIndex(self._Ob[aJ].getParamID())

            if aK._Xb(aI):
                return True

        return False

    def _Q2(self, aL, aV):
        aX = len(self._Ob)
        aJ = aL._v2()
        aN = 0
        aI = None
        aQ = None
        for aK in range(0, aX, 1):
            aH = self._Ob[aK]
            aI = aH.getParamIndex(aJ)
            if aI == ParamPivots._ds:
                aI = aL.getParamIndex(aH.getParamID())
                aH._Pb(aI, aJ)

            if aI < 0:
                raise Exception("err 23242 : " + aH.getParamID())

            aU = 0 if aI < 0 else aL.getParamFloat(aI)
            aQ = aH._N2()
            aM = aH._d2()
            aP = -1
            aT = 0
            aS = None
            aR = None
            if aQ < 1:
                pass
            else:
                if aQ == 1:
                    aS = aM[0]
                    if aS - DEF.GOSA < aU and aU < aS + DEF.GOSA:
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
                                # for (aO = 1; aO < aQ; ++aO):
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

            aH._wr(aP)
            aH._AL(aT)

        return aN

    def _zr(self, aN, aT, aP):
        aR = 1 << aP
        if aR + 1 > DEF.PIVOT_TABLE_SIZE:
            print("err 23245\n")

        aS = len(self._Ob)
        aK = 1
        aH = 1
        aJ = 0
        # for (aQ = 0; aQ < aR; ++aQ):
        for aQ in range(0, aR, 1):
            aN[aQ] = 0

        # for (aL = 0; aL < aS; ++aL):
        for aL in range(0, aS, 1):
            aI = self._Ob[aL]
            if aI._SL() == 0:
                aO = aI._Lr() * aK
                if aO < 0 and Live2D._3T:
                    raise Exception("err 23246")

                for aQ in range(0, aR, 1):
                    aN[aQ] += aO
            else:
                aO = aK * aI._Lr()
                aM = aK * (aI._Lr() + 1)
                for aQ in range(0, aR, 1):
                    aN[aQ] += aO if (int(aQ / aH) % 2 == 0) else aM

                aT[aJ] = aI._SL()
                aJ += 1
                aH *= 2

            aK *= aI._N2()

        aN[aR] = 65535
        aT[aJ] = -1

    def _h2(self, aJ, aH, aK):
        aM = Float32Array(aH)
        for aL in range(0, aH, 1):
            aM[aL] = aK[aL]

        aI = ParamPivots()
        aI._yP(aJ)
        aI._t2(aH, aM)
        self._Ob.append(aI)

    def _J2(self, aO):
        aN = aO
        aM = len(self._Ob)
        for aK in range(0, aM, 1):
            aI = self._Ob[aK]
            aH = aI._N2()
            aJ = aN % aI._N2()
            aL = aI._d2()[aJ]
            print("%s[%d]=%7.2f / ", aI.getParamID(), aJ, aL)
            aN /= aH

        print("\n")

    def getParamCount(self):
        return len(self._Ob)

    def _zs(self):
        return self._Ob


class LDMatrix44():

    def __init__(self):
        self.m = Float32Array(16)
        self.identity()

    def identity(self):
        for aH in range(0, 16, 1):
            self.m[aH] = 1 if ((aH % 5) == 0) else 0

    def getArray(self):
        return self.m

    def getCopyMatrix(self):
        return Float32Array(len(self.m))

    def setMatrix(self, aI):
        if aI is None or len(aI) != 16:
            return

        for aH in range(0, 16, 1):
            self.m[aH] = aI[aH]

    def mult(self, aH, aJ, aI):
        if aJ == None:
            return None

        if self == aJ:
            self.mult_safe(self.m, aH.m, aJ.m, aI)
        else:
            self.mult_fast(self.m, aH.m, aJ.m, aI)

        return aJ

    def mult_safe(self, aI, aH, aM, aJ):
        if aI == aM:
            aL = Array(16)
            self.mult_fast(aI, aH, aL, aJ)
            for aK in range(15, 0 - 1, -1):
                aM[aK] = aL[aK]
        else:
            self.mult_fast(aI, aH, aM, aJ)

    def mult_fast(self, aI, aH, aK, aJ):
        if aJ:
            aK[0] = aI[0] * aH[0] + aI[4] * aH[1] + aI[8] * aH[2]
            aK[4] = aI[0] * aH[4] + aI[4] * aH[5] + aI[8] * aH[6]
            aK[8] = aI[0] * aH[8] + aI[4] * aH[9] + aI[8] * aH[10]
            aK[12] = aI[0] * aH[12] + aI[4] * aH[13] + aI[8] * aH[14] + aI[12]
            aK[1] = aI[1] * aH[0] + aI[5] * aH[1] + aI[9] * aH[2]
            aK[5] = aI[1] * aH[4] + aI[5] * aH[5] + aI[9] * aH[6]
            aK[9] = aI[1] * aH[8] + aI[5] * aH[9] + aI[9] * aH[10]
            aK[13] = aI[1] * aH[12] + aI[5] * aH[13] + aI[9] * aH[14] + aI[13]
            aK[2] = aI[2] * aH[0] + aI[6] * aH[1] + aI[10] * aH[2]
            aK[6] = aI[2] * aH[4] + aI[6] * aH[5] + aI[10] * aH[6]
            aK[10] = aI[2] * aH[8] + aI[6] * aH[9] + aI[10] * aH[10]
            aK[14] = aI[2] * aH[12] + aI[6] * aH[13] + aI[10] * aH[14] + aI[14]
            aK[3] = aK[7] = aK[11] = 0
            aK[15] = 1
        else:
            aK[0] = aI[0] * aH[0] + aI[4] * aH[1] + aI[8] * aH[2] + aI[12] * aH[3]
            aK[4] = aI[0] * aH[4] + aI[4] * aH[5] + aI[8] * aH[6] + aI[12] * aH[7]
            aK[8] = aI[0] * aH[8] + aI[4] * aH[9] + aI[8] * aH[10] + aI[12] * aH[11]
            aK[12] = aI[0] * aH[12] + aI[4] * aH[13] + aI[8] * aH[14] + aI[12] * aH[15]
            aK[1] = aI[1] * aH[0] + aI[5] * aH[1] + aI[9] * aH[2] + aI[13] * aH[3]
            aK[5] = aI[1] * aH[4] + aI[5] * aH[5] + aI[9] * aH[6] + aI[13] * aH[7]
            aK[9] = aI[1] * aH[8] + aI[5] * aH[9] + aI[9] * aH[10] + aI[13] * aH[11]
            aK[13] = aI[1] * aH[12] + aI[5] * aH[13] + aI[9] * aH[14] + aI[13] * aH[15]
            aK[2] = aI[2] * aH[0] + aI[6] * aH[1] + aI[10] * aH[2] + aI[14] * aH[3]
            aK[6] = aI[2] * aH[4] + aI[6] * aH[5] + aI[10] * aH[6] + aI[14] * aH[7]
            aK[10] = aI[2] * aH[8] + aI[6] * aH[9] + aI[10] * aH[10] + aI[14] * aH[11]
            aK[14] = aI[2] * aH[12] + aI[6] * aH[13] + aI[10] * aH[14] + aI[14] * aH[15]
            aK[3] = aI[3] * aH[0] + aI[7] * aH[1] + aI[11] * aH[2] + aI[15] * aH[3]
            aK[7] = aI[3] * aH[4] + aI[7] * aH[5] + aI[11] * aH[6] + aI[15] * aH[7]
            aK[11] = aI[3] * aH[8] + aI[7] * aH[9] + aI[11] * aH[10] + aI[15] * aH[11]
            aK[15] = aI[3] * aH[12] + aI[7] * aH[13] + aI[11] * aH[14] + aI[15] * aH[15]

    def translate(self, aH, aJ, aI):
        self.m[12] = self.m[0] * aH + self.m[4] * aJ + self.m[8] * aI + self.m[12]
        self.m[13] = self.m[1] * aH + self.m[5] * aJ + self.m[9] * aI + self.m[13]
        self.m[14] = self.m[2] * aH + self.m[6] * aJ + self.m[10] * aI + self.m[14]
        self.m[15] = self.m[3] * aH + self.m[7] * aJ + self.m[11] * aI + self.m[15]

    def scale(self, aJ, aI, aH):
        self.m[0] *= aJ
        self.m[4] *= aI
        self.m[8] *= aH
        self.m[1] *= aJ
        self.m[5] *= aI
        self.m[9] *= aH
        self.m[2] *= aJ
        self.m[6] *= aI
        self.m[10] *= aH
        self.m[3] *= aJ
        self.m[7] *= aI
        self.m[11] *= aH

    def rotateX(self, aH):
        aK = UtMath.fcos(aH)
        aJ = UtMath._9(aH)
        aI = self.m[4]
        self.m[4] = aI * aK + self.m[8] * aJ
        self.m[8] = aI * -aJ + self.m[8] * aK
        aI = self.m[5]
        self.m[5] = aI * aK + self.m[9] * aJ
        self.m[9] = aI * -aJ + self.m[9] * aK
        aI = self.m[6]
        self.m[6] = aI * aK + self.m[10] * aJ
        self.m[10] = aI * -aJ + self.m[10] * aK
        aI = self.m[7]
        self.m[7] = aI * aK + self.m[11] * aJ
        self.m[11] = aI * -aJ + self.m[11] * aK

    def rotateY(self, aH):
        aK = UtMath.fcos(aH)
        aJ = UtMath._9(aH)
        aI = self.m[0]
        self.m[0] = aI * aK + self.m[8] * -aJ
        self.m[8] = aI * aJ + self.m[8] * aK
        aI = self.m[1]
        self.m[1] = aI * aK + self.m[9] * -aJ
        self.m[9] = aI * aJ + self.m[9] * aK
        aI = self.m[2]
        self.m[2] = aI * aK + self.m[10] * -aJ
        self.m[10] = aI * aJ + self.m[10] * aK
        aI = self.m[3]
        self.m[3] = aI * aK + self.m[11] * -aJ
        self.m[11] = aI * aJ + self.m[11] * aK

    def rotateZ(self, aH):
        aK = UtMath.fcos(aH)
        aJ = UtMath._9(aH)
        aI = self.m[0]
        self.m[0] = aI * aK + self.m[4] * aJ
        self.m[4] = aI * -aJ + self.m[4] * aK
        aI = self.m[1]
        self.m[1] = aI * aK + self.m[5] * aJ
        self.m[5] = aI * -aJ + self.m[5] * aK
        aI = self.m[2]
        self.m[2] = aI * aK + self.m[6] * aJ
        self.m[6] = aI * -aJ + self.m[6] * aK
        aI = self.m[3]
        self.m[3] = aI * aK + self.m[7] * aJ
        self.m[7] = aI * -aJ + self.m[7] * aK


class LDMatrix2x3():
    _kS = -1
    _pS = 0
    _hb = 1
    STATE_IDENTITY = 0
    _gb = 1
    _fo = 2
    _go = 4

    def __init__(self):
        self._7 = 1
        self._f = 0
        self._H = 0
        self._g = 1
        self._k = 0
        self._w = 0
        self._hi = self.STATE_IDENTITY
        self._Z = self._pS

    def transform(self, aK, aI, aH):
        # aS, aR, aM, aL, aJ
        aQ = 0
        aN = 0

        _switch_23645 = self._hi

        if _switch_23645 == (LDMatrix2x3._go | LDMatrix2x3._fo | LDMatrix2x3._gb):
            aT = self._7
            aS = self._H
            aR = self._k
            aM = self._f
            aL = self._g
            aJ = self._w
            while --aH >= 0:
                aP = aK[aQ];
                aQ += 1
                aO = aK[aQ];
                aQ += 1
                aI[aN] = (aT * aP + aS * aO + aR);
                aN += 1
                aI[aN] = (aM * aP + aL * aO + aJ);
                aN += 1
        elif _switch_23645 == (LDMatrix2x3._go | LDMatrix2x3._fo):
            aT = self._7
            aS = self._H
            aM = self._f
            aL = self._g
            while --aH >= 0:
                aP = aK[aQ];
                aQ += 1
                aO = aK[aQ];
                aQ += 1
                aI[aN] = (aT * aP + aS * aO);
                aN += 1
                aI[aN] = (aM * aP + aL * aO);
                aN += 1
        elif _switch_23645 == (LDMatrix2x3._go | LDMatrix2x3._gb):
            aS = self._H
            aR = self._k
            aM = self._f
            aJ = self._w
            while --aH >= 0:
                aP = aK[aQ];
                aQ += 1
                aI[aN] = (aS * aK[aQ] + aR);
                aQ += 1;
                aN += 1
                aI[aN] = (aM * aP + aJ);
                aN += 1
        elif _switch_23645 == (LDMatrix2x3._go):
            aS = self._H
            aM = self._f
            while --aH >= 0:
                aP = aK[aQ];
                aQ += 1
                aI[aN] = (aS * aK[aQ]);
                aQ += 1;
                aN += 1
                aI[aN] = (aM * aP);
                aN += 1
        elif _switch_23645 == (LDMatrix2x3._fo | LDMatrix2x3._gb):
            aT = self._7
            aR = self._k
            aL = self._g
            aJ = self._w
            while --aH >= 0:
                aI[aN] = (aT * aK[aQ] + aR);
                aQ += 1;
                aN += 1
                aI[aN] = (aL * aK[aQ] + aJ);
                aQ += 1;
                aN += 1
        elif _switch_23645 == (LDMatrix2x3._fo):
            aT = self._7
            aL = self._g
            while --aH >= 0:
                aI[aN] = (aT * aK[aQ]);
                aQ += 1;
                aN += 1
                aI[aN] = (aL * aK[aQ]);
                aQ += 1;
                aN += 1
        elif _switch_23645 == (LDMatrix2x3._gb):
            aR = self._k
            aJ = self._w
            while --aH >= 0:
                aI[aN] = (aK[aQ] + aR);
                aQ += 1;
                aN += 1
                aI[aN] = (aK[aQ] + aJ);
                aQ += 1;
                aN += 1
        elif _switch_23645 == (LDMatrix2x3.STATE_IDENTITY):
            if aK != aI or aQ != aN:
                UtSystem._jT(aK, aQ, aI, aN, aH * 2)

    def update(self):
        if self._H == 0 and self._f == 0:
            if self._7 == 1 and self._g == 1:
                if self._k == 0 and self._w == 0:
                    self._hi = LDMatrix2x3.STATE_IDENTITY
                    self._Z = LDMatrix2x3._pS
                else:
                    self._hi = LDMatrix2x3._gb
                    self._Z = LDMatrix2x3._hb
            else:
                if self._k == 0 and self._w == 0:
                    self._hi = LDMatrix2x3._fo
                    self._Z = LDMatrix2x3._kS
                else:
                    self._hi = (LDMatrix2x3._fo | LDMatrix2x3._gb)
                    self._Z = LDMatrix2x3._kS
        else:
            if self._7 == 0 and self._g == 0:
                if self._k == 0 and self._w == 0:
                    self._hi = LDMatrix2x3._go
                    self._Z = LDMatrix2x3._kS
                else:
                    self._hi = (LDMatrix2x3._go | LDMatrix2x3._gb)
                    self._Z = LDMatrix2x3._kS
            else:
                if self._k == 0 and self._w == 0:
                    self._hi = (LDMatrix2x3._go | LDMatrix2x3._fo)
                    self._Z = LDMatrix2x3._kS
                else:
                    self._hi = (LDMatrix2x3._go | LDMatrix2x3._fo | LDMatrix2x3._gb)
                    self._Z = LDMatrix2x3._kS

    def _RT(self, aK):
        self._IT(aK)
        aJ = aK[0]
        aH = aK[2]
        aN = aK[1]
        aM = aK[3]
        aI = math.sqrt(aJ * aJ + aN * aN)
        aL = aJ * aM - aH * aN
        if aI == 0:
            if Live2D._so:
                print("affine._RT() / rt==0")
        else:
            aK[0] = aI
            aK[1] = aL / aI
            aK[2] = (aN * aM + aJ * aH) / aL
            aK[3] = math.atan2(aN, aJ)

    def _ho(self, aN, aM, aI, aH):
        aL = Float32Array(6)
        aK = Float32Array(6)
        aN._RT(aL)
        aM._RT(aK)
        aJ = Float32Array(6)
        aJ[0] = aL[0] + (aK[0] - aL[0]) * aI
        aJ[1] = aL[1] + (aK[1] - aL[1]) * aI
        aJ[2] = aL[2] + (aK[2] - aL[2]) * aI
        aJ[3] = aL[3] + (aK[3] - aL[3]) * aI
        aJ[4] = aL[4] + (aK[4] - aL[4]) * aI
        aJ[5] = aL[5] + (aK[5] - aL[5]) * aI
        aH._CT(aJ)

    def _CT(self, aJ):
        aI = math.cos(aJ[3])
        aH = math.sin(aJ[3])
        self._7 = aJ[0] * aI
        self._f = aJ[0] * aH
        self._H = aJ[1] * (aJ[2] * aI - aH)
        self._g = aJ[1] * (aJ[2] * aH + aI)
        self._k = aJ[4]
        self._w = aJ[5]
        self.update()

    def _IT(self, aH):
        aH[0] = self._7
        aH[1] = self._f
        aH[2] = self._H
        aH[3] = self._g
        aH[4] = self._k
        aH[5] = self._w


class Live2DMotionBin(AMotion):
    _cs = "VISIBLE:"
    _ar = "LAYOUT:"
    _Co = 0
    _D2 = []
    _1T = 1

    def __init__(self):

        AMotion.prototype.constructor.call(self)
        self.motions = Array()
        self._7r = None
        self._7r = Live2DMotionBin._Co;
        Live2DMotionBin._Co += 1
        self._D0 = 30
        self._yT = 0
        self._E = True
        self.loopFadeIn = True
        self._AS = -1
        self._a0()

    def getDurationMSec(self):
        return self._AS

    def dump(self):
        for aJ in range(0, len(self.motions), 1):
            aH = self.motions[aJ]
            print("_wL[%s] [%d]. ", aH._4P, len(aH._I0))
            for aI in range(0, 10, 1):
                print("%5.2f ,", aH._I0[aI])

            print("\n")

    def updateParamExe(self, aH, aL, aO, aX):
        aM = aL - aX._z2
        aV = aM * self._D0 / 1000
        aJ = int(aV)
        aP = aV - aJ
        for aU in range(0, len(self.motions), 1):
            aS = self.motions[aU]
            aK = len(aS._I0)
            aQ = aS._4P
            if aS._RP == BufType._hs:
                aT = aS._I0[(aK - 1 if aJ >= aK else aJ)]
                aH.setParamFloat(aQ, aT)
            else:
                if BufType._ws <= aS._RP and aS._RP <= BufType._Ys:
                    pass
                else:
                    aR = aH.getParamFloat(aQ)
                    aY = aS._I0[(aK - 1 if aJ >= aK else aJ)]
                    aW = aS._I0[(aK - 1 if aJ + 1 >= aK else aJ + 1)]
                    aI = aY + (aW - aY) * aP
                    aN = aR + (aI - aR) * aO
                    aH.setParamFloat(aQ, aN)

        if aJ >= self._yT:
            if self._E:
                aX._z2 = aL
                if self.loopFadeIn:
                    aX._bs = aL
            else:
                aX._9L = True

    def _r0(self):
        return self._E

    def _aL(self, aH):
        self._E = aH

    def isLoopFadeIn(self):
        return self.loopFadeIn

    def setLoopFadeIn(self, aH):
        self.loopFadeIn = aH

    @staticmethod
    def loadMotion(aR):
        aM = Live2DMotionBin()
        aI = [0]
        aP = len(aR)
        aM._yT = 0
        aJ = 0
        # for aJ in range(0, aP, 1):
        while aJ < aP:
            aQ = (aR[aJ] & 255)
            if aQ == "\n" or aQ == "\r":
                aJ += 1
                continue

            if aQ == "#":
                # for (; aJ < aP; ++aJ):
                while aJ < aP:
                    if aR[aJ] == "\n" or aR[aJ] == "\r":
                        break
                    aJ += 1

                continue

            if aQ == "":
                aT = aJ
                aK = -1
                # for (; aJ < aP; ++aJ):
                while aJ < aP:
                    aQ = (aR[aJ] & 255)
                    if aQ == "\r" or aQ == "\n":
                        break

                    if aQ == "=":
                        aK = aJ
                        break
                    aJ += 1

                aO = False
                if aK >= 0:
                    if aK == aT + 4 and aR[aT + 1] == "f" and aR[aT + 2] == "p" and aR[aT + 3] == "s":
                        aO = True

                    # for aJ in range(aK + 1, aP, 1):
                    aJ = aK + 1
                    while aJ < aP:
                        aQ = (aR[aJ] & 255)
                        if aQ == "\r" or aQ == "\n":
                            break

                        if aQ == "," or aQ == " " or aQ == "\t":
                            continue

                        aL = UtString.strToFloat(aR, aP, aJ, aI)
                        if aI[0] > 0:
                            if aO and 5 < aL and aL < 121:
                                aM._D0 = aL

                        aJ = aI[0]
                        aK += 1

                # for (; aJ < aP; ++aJ):
                while aJ < aP:
                    if aR[aJ] == "\n" or aR[aJ] == "\r":
                        break
                    aJ += 1

                aJ += 1
                continue

            if ("a" <= aQ and aQ <= "z") or ("A" <= aQ and aQ <= "Z") or aQ == "_":
                aT = aJ
                aK = -1
                while aJ < aP:
                    # for (; aJ < aP; ++aJ):
                    aQ = (aR[aJ] & 255)
                    if aQ == "\r" or aQ == "\n":
                        break

                    if aQ == "=":
                        aK = aJ
                        break
                    aJ += 1

                if aK >= 0:
                    aN = BufType()
                    if UtString.startswith(aR, aT, Live2DMotionBin._cs):
                        aN._RP = BufType._hs
                        aN._4P = str(aR, aT, aK - aT)
                    else:
                        if UtString.startswith(aR, aT, Live2DMotionBin._ar):
                            aN._4P = str(aR, aT + 7, aK - aT - 7)
                            if UtString.startswith(aR, aT + 7, "ANCHOR_X"):
                                aN._RP = BufType._xs
                            else:
                                if UtString.startswith(aR, aT + 7, "ANCHOR_Y"):
                                    aN._RP = BufType._us
                                else:
                                    if UtString.startswith(aR, aT + 7, "SCALE_X"):
                                        aN._RP = BufType._qs
                                    else:
                                        if UtString.startswith(aR, aT + 7, "SCALE_Y"):
                                            aN._RP = BufType._Ys
                                        else:
                                            if UtString.startswith(aR, aT + 7, "AffineEnt"):
                                                aN._RP = BufType._ws
                                            else:
                                                if UtString.startswith(aR, aT + 7, "Y"):
                                                    aN._RP = BufType._Ns
                        else:
                            aN._RP = BufType._Fr
                            aN._4P = str(aR, aT, aK - aT)

                    aM.motions.append(aN)
                    aS = 0
                    Live2DMotionBin._D2.clear()
                    # for aJ in range(aK + 1, aP, 1):
                    aJ = aK + 1
                    while aJ < aP:
                        aQ = (aR[aJ] & 255)
                        if aQ == "\r" or aQ == "\n":
                            break

                        if aQ == "," or aQ == " " or aQ == "\t":
                            continue

                        aL = UtString.strToFloat(aR, aP, aJ, aI)
                        if aI[0] > 0:
                            Live2DMotionBin._D2.append(aL)
                            aS += 1
                            aH = aI[0]
                            if aH < aJ:
                                print("_n0 _hi . @Live2DMotion loadMotion()\n")
                                break

                            aJ = aH
                        aJ += 1

                    aN._I0 = Live2DMotionBin._D2._BL()
                    if aS > aM._yT:
                        aM._yT = aS

            aJ += 1
        aM._AS = int((1000 * aM._yT) / aM._D0)
        return aM


class t():
    _Fr = 0
    _hs = 1
    _ws = 100
    _Ns = 101
    _xs = 102
    _us = 103
    _qs = 104
    _Ys = 105

    def __init__(self):
        self._4P = None
        self._I0 = None
        self._RP = None


class DEF:
    VERTEX_TYPE_OFFSET0_STEP2 = 1
    VERTEX_TYPE_OFFSET2_STEP5 = 2
    VERTEX_OFFSET = 0
    VERTEX_STEP = 2
    VERTEX_TYPE = VERTEX_TYPE_OFFSET0_STEP2
    _Ls = True
    MAX_INTERPOLATION = 5
    PIVOT_TABLE_SIZE = 65
    GOSA = 0.0001
    VALUE_MIN = 0.001
    VALUE_MIN_PRECISION = 3


class FileFormat2():
    _o7 = 6
    _S7 = 7
    _s7 = 8
    _77 = 9
    LIVE2D_FORMAT_VERSION_V2_10_SDK2 = 10
    LIVE2D_FORMAT_VERSION_V2_11_SDK2_1 = 11
    _T7 = LIVE2D_FORMAT_VERSION_V2_11_SDK2_1
    _Is = -2004318072
    _h0 = 0
    _4L = 23
    _7P = 33

    @staticmethod
    def _uT(aH):
        print("_bo :: _6 _mo _E0 : %d\n", aH)

    @staticmethod
    def _9o(aH):
        if aH < 40:
            FileFormat2._uT(aH)
            return None

        elif aH < 50:
            FileFormat2._uT(aH)
            return None

        elif aH < 60:
            FileFormat2._uT(aH)
            return None

        elif aH < 100:
            _switch_27797 = aH
            if _switch_27797 == 65:
                return BDBoxGrid()
            if _switch_27797 == 66:
                return PivotManager()
            if _switch_27797 == 67:
                return ParamPivots()
            if _switch_27797 == 68:
                return BDAffine()
            if _switch_27797 == 69:
                return AffineEnt()
            if _switch_27797 == 70:
                return DDTexture()
            else:
                FileFormat2._uT(aH)
                return None

        elif aH < 150:
            _switch_27907 = aH
            if _switch_27907 == 131:
                return ParamDefF()
            elif _switch_27907 == 133:
                return PartsData()
            elif _switch_27907 == 136:
                return ModelImpl()
            elif _switch_27907 == 137:
                return ParamDefSet()
            elif _switch_27907 == 142:
                return AvatarPartsItem()

        FileFormat2._uT(aH)
        return None


class ModelContext():
    _HP = 0
    __0 = True
    _V2 = -1
    _W0 = -1
    _jr = False
    _ZS = True
    _tr = (-1000000)
    _lr = (1000000)
    _is = 32
    _e = False

    def __init__(self, aH):
        self._QT = True
        self._co = -1
        self._qo = 0
        self._pb = Array(ModelContext._is)
        self.__2 = Float32Array(ModelContext._is)
        self._vr = Float32Array(ModelContext._is)
        self._Rr = Float32Array(ModelContext._is)
        self._Or = Float32Array(ModelContext._is)
        self._fs = Float32Array(ModelContext._is)
        self._Js = Array(ModelContext._is)
        self._3S = Array()
        self._aS = Array()
        self._Bo = None
        self._F2 = Array()
        self._db = Array()
        self._8b = Array()
        self._Hr = Array()
        self._Ws = None
        self._Vs = None
        self._Er = None
        self._Es = Int16Array(DEF.PIVOT_TABLE_SIZE)
        self._ZP = Float32Array(DEF.MAX_INTERPOLATION * 2)
        self._Ri = aH
        self._b0 = ModelContext._HP
        ModelContext._HP += 1
        self.clipManager = None
        self.dp_webgl = None

    def getDrawDataIndex(self, aI):
        for aH in range(len(self._aS) - 1, 0 - 1, -1):
            if self._aS[aH] is not None and self._aS[aH].getDrawDataID().id == aI:
                return aH

        return -1

    def getDrawData(self, aH):
        if isinstance(aH, DrawDataID):
            if self._Bo is None:
                self._Bo = {}
                aJ = len(self._aS)
                for aI in range(0, aJ, 1):
                    aL = self._aS[aI]
                    aK = aL.getDrawDataID()
                    if aK is None:
                        continue

                    self._Bo[aK] = aL

            return self._Bo[id]
        else:
            if aH < len(self._aS):
                return self._aS[aH]
            else:
                return None

    def release(self):
        self._3S.clear()
        self._aS.clear()
        self._F2.clear()
        if self._Bo is not None:
            self._Bo.clear()

        self._db.clear()
        self._8b.clear()
        self._Hr.clear()

    def init(self):
        self._co += 1
        if len(self._F2) > 0:
            self.release()

        aO = self._Ri.getModelImpl()
        partsDataList = aO.getPartsDataList()
        aS = len(partsDataList)
        aH = Array()
        a3 = Array()
        for aV in range(0, aS, 1):
            a4 = partsDataList[aV]
            self._F2.append(a4)
            self._Hr.append(a4.init(self))
            baseDataList = a4.getBaseData()
            aR = len(baseDataList)
            for aU in range(0, aR, 1):
                aH.append(baseDataList[aU])

            for aU in range(0, aR, 1):
                aM = baseDataList[aU].init(self)
                aM._l2(aV)
                a3.append(aM)

            a1 = a4.getDrawData()
            aP = len(a1)
            for aU in range(0, aP, 1):
                aZ = a1[aU]
                a0 = aZ.init(self)
                a0._IP = aV
                self._aS.append(aZ)
                self._8b.append(a0)

        aY = len(aH)
        aN = BaseDataID._2o()
        while True:
            aX = False
            for aV in range(0, aY, 1):
                aL = aH[aV]
                if aL == None:
                    continue

                a2 = aL.getTargetBaseDataID()
                if a2 == None or a2 == aN or self.getBaseDataIndex(a2) >= 0:
                    self._3S.append(aL)
                    self._db.append(a3[aV])
                    aH[aV] = None
                    aX = True

            if not aX:
                break

        aI = aO._E2()
        if aI != None:
            aJ = aI._1s()
            if aJ != None:
                aW = len(aJ)
                for aV in range(0, aW, 1):
                    aQ = aJ[aV]
                    if aQ == None:
                        continue

                    self._02(aQ.getParamID(), aQ.getDefaultValue(), aQ.getMinValue(), aQ.getMaxValue())

        self.clipManager = ClippingManagerWebGL(self.dp_webgl)
        self.clipManager.init(self, self._aS, self._8b)
        self._QT = True

    def update(self):
        if ModelContext._e:
            print("_zL")

        aK = len(self.__2)
        for aW in range(0, aK, 1):
            if self.__2[aW] != self._vr[aW]:
                self._Js[aW] = ModelContext._ZS
                self._vr[aW] = self.__2[aW]

        aX = False
        aQ = len(self._3S)
        aN = len(self._aS)
        aS = IDrawData2._or()
        aZ = IDrawData2._Pr()
        aU = aZ - aS + 1
        if self._Ws == None or len(self._Ws) < aU:
            self._Ws = Int16Array(aU)
            self._Vs = Int16Array(aU)

        for aW in range(0, aU, 1):
            self._Ws[aW] = ModelContext._V2
            self._Vs[aW] = ModelContext._V2

        if self._Er == None or len(self._Er) < aN:
            self._Er = Int16Array(aN)

        for aW in range(0, aN, 1):
            self._Er[aW] = ModelContext._W0

        if ModelContext._e:
            print("_zL")

        if ModelContext._e:
            print("_UL")

        aL = None
        for aV in range(0, aQ, 1):
            aJ = self._3S[aV]
            aH = self._db[aV]
            aJ.setupInterpolate(self, aH)
            aJ.setupTransform(self, aH)

        if aL is not None:
            if ModelContext.__0:
                print(aL)

        if ModelContext._e:
            print("_UL")

        if ModelContext._e:
            print("_DL")

        aR = None
        for aO in range(0, aN, 1):
            aM = self._aS[aO]
            aI = self._8b[aO]
            aM.setupInterpolate(self, aI)
            if aI._u2():
                continue

            aM.setupTransform(self, aI)
            aT = math.floor(aM._zS(self, aI) - aS)
            aP = None

            aP = self._Vs[aT]

            if aP == ModelContext._V2:
                self._Ws[aT] = aO
            else:
                self._Er[aP] = aO

            self._Vs[aT] = aO

        if aR is not None:
            if ModelContext.__0:
                print(aR)

        if ModelContext._e:
            print("_DL")

        if ModelContext._e:
            print("_eL")

        # for (aW = len(self._Js) - 1; aW >= 0; aW--):
        for aW in range(len(self._Js) - 1, -1, -1):
            self._Js[aW] = ModelContext._jr

        self._QT = False
        if ModelContext._e:
            print("_eL")

        return aX

    def preDraw(self, aH):
        if self.clipManager is not None:
            aH._ZT()
            self.clipManager.setupClip(self, aH)

    def draw(self, aM):
        if self._Ws is None:
            print("call _Ri.update() before _Ri.draw() ")
            return

        aP = len(self._Ws)
        aM._ZT()
        for aK in range(0, aP, 1):
            aN = self._Ws[aK]
            if aN == ModelContext._V2:
                continue

            while True:
                aH = self._aS[aN]
                aI = self._8b[aN]
                if aI._yo():
                    aJ = aI._IP
                    aL = self._Hr[aJ]
                    # if aL._e0._NL.id == 'PARTS_01_EYE_BALL_001':
                    #     break
                    # print(aL._e0._NL, aH._gP.id, aH.clipID)
                    aI._VS = aL.getPartsOpacity()
                    aH.draw(aM, self, aI)

                aO = self._Er[aN]
                if aO <= aN or aO == ModelContext._W0:
                    break

                aN = aO
        # exit()

    def getParamIndex(self, aH):
        for aI in range(0, len(self._pb), 1):
            p = self._pb[aI]
            if p == aH:
                return aI

        return self._02(aH, 0, ModelContext._tr, ModelContext._lr)

    def _BS(self, aH):
        return self.getBaseDataIndex(aH)

    def getBaseDataIndex(self, aH):
        # aH: BaseDataID()
        for aI in range(len(self._3S) - 1, 0 - 1, -1):
            if self._3S[aI] is not None and self._3S[aI].getBaseDataID() == aH:
                return aI

        return -1

    def _UT(self, aJ, aH):
        aI = Float32Array(aH)

        UtSystem._jT(aJ, 0, aI, 0, len(aJ))
        return aI

    def _02(self, aN, aM, aL, aH):
        if self._qo >= len(self._pb):
            aK = len(self._pb)
            aJ = Array(aK * 2)
            UtSystem._jT(self._pb, 0, aJ, 0, aK)
            self._pb = aJ
            self.__2 = self._UT(self.__2, aK * 2)
            self._vr = self._UT(self._vr, aK * 2)
            self._Rr = self._UT(self._Rr, aK * 2)
            self._Or = self._UT(self._Or, aK * 2)
            aI = Array(len(aJ))
            UtSystem._jT(self._Js, 0, aI, 0, aK)
            self._Js = aI

        self._pb[self._qo] = aN
        self.__2[self._qo] = aM
        self._vr[self._qo] = aM
        self._Rr[self._qo] = aL
        self._Or[self._qo] = aH
        self._Js[self._qo] = ModelContext._ZS
        ret = self._qo
        self._qo += 1
        return ret

    def _Zo(self, aI, aH):
        self._3S[aI] = aH

    def setParamFloat(self, aH, aI):
        if aI < self._Rr[aH]:
            aI = self._Rr[aH]

        if aI > self._Or[aH]:
            aI = self._Or[aH]

        self.__2[aH] = aI

    def loadParam(self):
        aH = len(self.__2)
        if aH > len(self._fs):
            aH = len(self._fs)

        UtSystem._jT(self._fs, 0, self.__2, 0, aH)

    def saveParam(self):
        aH = len(self.__2)
        if aH > len(self._fs):
            self._fs = Float32Array(aH)

        UtSystem._jT(self.__2, 0, self._fs, 0, aH)

    def _v2(self):
        return self._co

    def _WS(self):
        return self._QT

    def _Xb(self, aH):
        return self._Js[aH] == ModelContext._ZS

    def _vs(self):
        return self._Es

    def _Tr(self):
        return self._ZP

    def getBaseData(self, aH):
        return self._3S[aH]

    def getParamFloat(self, aH):
        return self.__2[aH]

    def getParamMax(self, aH):
        return self._Or[aH]

    def getParamMin(self, aH):
        return self._Rr[aH]

    def setPartsOpacity(self, aJ, aH):
        aI = self._Hr[aJ]
        aI.setPartsOpacity(aH)

    def getPartsOpacity(self, aI):
        aH = self._Hr[aI]
        return aH.getPartsOpacity()

    def getPartsDataIndex(self, aI):
        for aH in range(len(self._F2) - 1, 0 - 1, -1):
            if self._F2[aH] != None and self._F2[aH]._p2() == aI:
                return aH

        return -1

    def _q2(self, aH):
        return self._db[aH]

    def _C2(self, aH):
        return self._8b[aH]

    def _Bb(self, aH):
        return self._Hr[aH]

    def _5s(self, aO, aK):
        aJ = len(self._Ws)
        aN = aO
        for aL in range(0, aJ, 1):
            aI = self._Ws[aL]
            if aI == ModelContext._V2:
                continue

            while True:
                aM = self._8b[aI]
                if aM.isAvailable():
                    aM._GT()._B2(self, aM, aN)
                    aN += aK

                aH = self._Er[aI]
                if aH <= aI or aH == ModelContext._W0:
                    break

                aI = aH

    def setDrawParam(self, aH):
        self.dp_webgl = aH

    def getDrawParam(self):
        return self.dp_webgl


class UtFile():
    @staticmethod
    def _0T(aH):
        # return UtFile._0T(_5(aH))
        pass

    @staticmethod
    def _0T(aJ):
        pass
        # if not aJ.exists():
        #     raise _ls(aJ._3b())
        #
        # aH = aJ.length()
        # aI = Int8Array(aH)
        # aM = _Xs(_kb(aJ), 8192)
        # aK = None
        # aL = 0
        # while (aK = aM.read(aI, aL, aH - aL)) > 0:
        #     aL += aK
        #
        # return aI

    @staticmethod
    def _C(aJ):
        pass
        # aI = None
        # aL = None
        # try:
        #     aI = aJ if (isinstance(aJ, Array)) else _Xs(aJ, 8192)
        #     aL = _js()
        #     aM = 1000
        #     aK = None
        #     aH = Int8Array(aM)
        #     while (aK = aI.read(aH)) > 0:
        #         aL.write(aH, 0, aK)
        #
        #     return aL._TS()
        #
        # finally:
        #     if aJ != None:
        #         aJ.close()
        #
        #     if aL != None:
        #         aL.flush()
        #         aL.close()


class EyeBlinkMotion:

    def __init__(self):
        self._12 = None
        self._bb = None
        self.__L = None
        self._jo = None
        self._iL = None
        self._0L = None
        self._Br = None
        self._Dr = None
        self._Cb = None
        self._mr = None
        self.__L = EYE_STATE.STATE_FIRST
        self._Br = 4000
        self._Dr = 100
        self._Cb = 50
        self._mr = 150
        self._jo = True
        self._iL = "PARAM_EYE_L_OPEN"
        self._0L = "PARAM_EYE_R_OPEN"

    def _T2(self):
        aI = UtSystem.getUserTimeMSec()
        # aH = _10()
        aH = math.pi
        return (aI + aH * (2 * self._Br - 1))

    def _uo(self, aH):
        self._Br = aH

    def _QS(self, aI, aH, aJ):
        self._Dr = aI
        self._Cb = aH
        self._mr = aJ

    def _7T(self, aI):
        aK = UtSystem.getUserTimeMSec()
        aH = None
        aJ = 0

        _switch_32444 = self.__L
        while True:
            if _switch_32444 == EYE_STATE.STATE_CLOSING:
                aJ = (aK - self._bb) / self._Dr
                if aJ >= 1:
                    aJ = 1
                    self.__L = EYE_STATE.STATE_CLOSED
                    self._bb = aK

                aH = 1 - aJ
                break
            if _switch_32444 == EYE_STATE.STATE_CLOSED:
                aJ = (aK - self._bb) / self._Cb
                if aJ >= 1:
                    self.__L = EYE_STATE.STATE_OPENING
                    self._bb = aK

                aH = 0
                break
            if _switch_32444 == EYE_STATE.STATE_OPENING:
                aJ = (aK - self._bb) / self._mr
                if aJ >= 1:
                    aJ = 1
                    self.__L = EYE_STATE.STATE_INTERVAL
                    self._12 = self._T2()

                aH = aJ
                break
            if _switch_32444 == EYE_STATE.STATE_INTERVAL:
                if self._12 < aK:
                    self.__L = EYE_STATE.STATE_CLOSING
                    self._bb = aK

                aH = 1
                break
            if _switch_32444 == EYE_STATE.STATE_FIRST:
                _switch_32444 = None
            else:
                self.__L = EYE_STATE.STATE_INTERVAL
                self._12 = self._T2()
                aH = 1
                break
            break
        if not self._jo:
            aH = -aH

        aI.setParamFloat(self._iL, aH)
        aI.setParamFloat(self._0L, aH)


EYE_STATE = type('', (), {
    "STATE_FIRST": "STATE_FIRST",
    "STATE_INTERVAL": "STATE_INTERVAL",
    "STATE_CLOSING": "STATE_CLOSING",
    "STATE_CLOSED": "STATE_CLOSED",
    "STATE_OPENING": "STATE_OPENING",
})()


class DrawParamOpenGLES2(DrawParam):

    def __init__(self):
        super().__init__()
        self._sb = Int32Array(DrawParamOpenGLES2._As)
        self._U2 = {}
        self.transform = None
        self.gl = None
        if DrawParamOpenGLES2._NT is None:
            DrawParamOpenGLES2._NT = DrawParamOpenGLES2._9r(256)
            DrawParamOpenGLES2._vS = DrawParamOpenGLES2._9r(256)
            DrawParamOpenGLES2._no = DrawParamOpenGLES2._vb(256)

    def setGL(self, aH):
        self.gl = aH

    def setTransform(self, aH):
        self.transform = aH

    def _ZT(self):
        pass

    def _Uo(self, aO, aH, aP, aI, aQ, aM, aK, aJ):
        if aM < 0.01:
            return

        aL = self._U2[aO]
        aN = Live2D.EXPAND_W if aM > 0.9 else 0
        self.gl.drawElements(aL, aP, aI, aQ, aM, aN, self.transform, aJ)

    def _Rs(self):
        raise LDError("_Rs")

    def _Ds(self, aH):
        raise LDError("_Ds")

    def _K2(self):
        for aH in range(0, len(self._sb), 1):
            aI = self._sb[aH]
            if aI != 0:
                self.gl._Sr(1, self._sb, aH)
                self._sb[aH] = 0

    def _nS(self, aH):
        aK = max(len(self._sb) * 2, aH + 1 + 10)
        aI = Int32Array(aK)
        UtSystem._jT(self._sb, 0, aI, 0, len(self._sb))
        self._sb = aI
        aJ = Array()
        UtSystem._jT(self._U2, 0, aJ, 0, len(self._U2))
        self._U2 = aJ

    @staticmethod
    def _9r(aH):
        aI = Float32Array(aH)
        return aI

    @staticmethod
    def _vb(aH):
        aI = Int16Array(aH)
        return aI

    @staticmethod
    def _cr(aI, aH):
        if aI == None or aI._yL() < len(aH):
            aI = DrawParamOpenGLES2._9r(len(aH) * 2)
            aI.put(aH)
            aI._oT(0)
        else:
            aI.clear()
            aI.put(aH)
            aI._oT(0)

        return aI

    @staticmethod
    def _mb(aI, aH):
        if aI == None or aI._yL() < len(aH):
            aI = DrawParamOpenGLES2._vb(len(aH) * 2)
            aI.put(aH)
            aI._oT(0)
        else:
            aI.clear()
            aI.put(aH)
            aI._oT(0)

        return aI

    @staticmethod
    def _Hs():
        return DrawParamOpenGLES2._Gr

    @staticmethod
    def _as(aH):
        DrawParamOpenGLES2._Gr = aH

    _As = 32
    _Gr = False
    _NT = None
    _vS = None
    _no = None

    def setTexture(self, aI, aH):
        if len(self._sb) < aI + 1:
            self._nS(aI)

        self._sb[aI] = aH

    def setTexture(self, aH, aI):
        if len(self._sb) < aH + 1:
            self._nS(aH)

        self._U2[aH] = aI


class BDAffine(IBaseData):
    _Xo = [0.0, 0.0]
    _io = [0.0, 0.0]
    _0o = [0.0, 0.0]
    _Lo = [0.0, 0.0]
    _To = [0.0, 0.0]
    _Po = [0.0, 0.0]
    _gT = [None]

    def __init__(self):
        super().__init__()
        # IBaseData.prototype.constructor.call(self)
        self._GS = None
        self._Y0 = None

    def _zP(self):
        self._GS = PivotManager()
        self._GS._zP()
        self._Y0 = []

    def getType(self):
        return IBaseData._c2

    def read(self, aH):
        super().read(aH)
        self._GS = aH._nP()
        self._Y0 = aH._nP()
        super().readV2_opacity(aH)

    def init(self, aH):
        aI = BDAffineContext(self)
        aI._Yr = AffineEnt()
        if self.needTransform():
            aI._Wr = AffineEnt()

        return aI

    def setupInterpolate(self, bf, bx):
        if not ((self == bx._GT())):
            print("### assert!! ### ")

        bm = bx
        if not self._GS._Ur(bf):
            return

        bw = BDAffine._gT
        bw[0] = False
        a2 = self._GS._Q2(bf, bw)
        bx._Ib(bw[0])
        self.interpolateOpacity(bf, self._GS, bx, bw)
        a3 = bf._vs()
        ba = bf._Tr()
        self._GS._zr(a3, ba, a2)
        if a2 <= 0:
            bn_3 = self._Y0[a3[0]]
            bm._Yr.init(bn_3)
        else:
            if a2 == 1:
                bn_1 = self._Y0[a3[0]]
                bl = self._Y0[a3[1]]
                a9 = ba[0]
                bm._Yr._fL = bn_1._fL + (bl._fL - bn_1._fL) * a9
                bm._Yr._gL = bn_1._gL + (bl._gL - bn_1._gL) * a9
                bm._Yr._B0 = bn_1._B0 + (bl._B0 - bn_1._B0) * a9
                bm._Yr._z0 = bn_1._z0 + (bl._z0 - bn_1._z0) * a9
                bm._Yr._qT = bn_1._qT + (bl._qT - bn_1._qT) * a9
            else:
                if a2 == 2:
                    bn_1 = self._Y0[a3[0]]
                    bl = self._Y0[a3[1]]
                    a1 = self._Y0[a3[2]]
                    a0 = self._Y0[a3[3]]
                    a9 = ba[0]
                    a8 = ba[1]
                    bC = bn_1._fL + (bl._fL - bn_1._fL) * a9
                    bB = a1._fL + (a0._fL - a1._fL) * a9
                    bm._Yr._fL = bC + (bB - bC) * a8
                    bC = bn_1._gL + (bl._gL - bn_1._gL) * a9
                    bB = a1._gL + (a0._gL - a1._gL) * a9
                    bm._Yr._gL = bC + (bB - bC) * a8
                    bC = bn_1._B0 + (bl._B0 - bn_1._B0) * a9
                    bB = a1._B0 + (a0._B0 - a1._B0) * a9
                    bm._Yr._B0 = bC + (bB - bC) * a8
                    bC = bn_1._z0 + (bl._z0 - bn_1._z0) * a9
                    bB = a1._z0 + (a0._z0 - a1._z0) * a9
                    bm._Yr._z0 = bC + (bB - bC) * a8
                    bC = bn_1._qT + (bl._qT - bn_1._qT) * a9
                    bB = a1._qT + (a0._qT - a1._qT) * a9
                    bm._Yr._qT = bC + (bB - bC) * a8
                else:
                    if a2 == 3:
                        aP = self._Y0[a3[0]]
                        aO = self._Y0[a3[1]]
                        bu = self._Y0[a3[2]]
                        bs = self._Y0[a3[3]]
                        aK = self._Y0[a3[4]]
                        aJ = self._Y0[a3[5]]
                        bj = self._Y0[a3[6]]
                        bi = self._Y0[a3[7]]
                        a9 = ba[0]
                        a8 = ba[1]
                        a6 = ba[2]
                        bC = aP._fL + (aO._fL - aP._fL) * a9
                        bB = bu._fL + (bs._fL - bu._fL) * a9
                        bz = aK._fL + (aJ._fL - aK._fL) * a9
                        by = bj._fL + (bi._fL - bj._fL) * a9
                        bm._Yr._fL = (1 - a6) * (bC + (bB - bC) * a8) + a6 * (bz + (by - bz) * a8)
                        bC = aP._gL + (aO._gL - aP._gL) * a9
                        bB = bu._gL + (bs._gL - bu._gL) * a9
                        bz = aK._gL + (aJ._gL - aK._gL) * a9
                        by = bj._gL + (bi._gL - bj._gL) * a9
                        bm._Yr._gL = (1 - a6) * (bC + (bB - bC) * a8) + a6 * (bz + (by - bz) * a8)
                        bC = aP._B0 + (aO._B0 - aP._B0) * a9
                        bB = bu._B0 + (bs._B0 - bu._B0) * a9
                        bz = aK._B0 + (aJ._B0 - aK._B0) * a9
                        by = bj._B0 + (bi._B0 - bj._B0) * a9
                        bm._Yr._B0 = (1 - a6) * (bC + (bB - bC) * a8) + a6 * (bz + (by - bz) * a8)
                        bC = aP._z0 + (aO._z0 - aP._z0) * a9
                        bB = bu._z0 + (bs._z0 - bu._z0) * a9
                        bz = aK._z0 + (aJ._z0 - aK._z0) * a9
                        by = bj._z0 + (bi._z0 - bj._z0) * a9
                        bm._Yr._z0 = (1 - a6) * (bC + (bB - bC) * a8) + a6 * (bz + (by - bz) * a8)
                        bC = aP._qT + (aO._qT - aP._qT) * a9
                        bB = bu._qT + (bs._qT - bu._qT) * a9
                        bz = aK._qT + (aJ._qT - aK._qT) * a9
                        by = bj._qT + (bi._qT - bj._qT) * a9
                        bm._Yr._qT = (1 - a6) * (bC + (bB - bC) * a8) + a6 * (bz + (by - bz) * a8)
                    else:
                        if a2 == 4:
                            aT = self._Y0[a3[0]]
                            aS = self._Y0[a3[1]]
                            bE = self._Y0[a3[2]]
                            bD = self._Y0[a3[3]]
                            aN = self._Y0[a3[4]]
                            aM = self._Y0[a3[5]]
                            bp = self._Y0[a3[6]]
                            bo = self._Y0[a3[7]]
                            bh = self._Y0[a3[8]]
                            bg = self._Y0[a3[9]]
                            aY = self._Y0[a3[10]]
                            aW = self._Y0[a3[11]]
                            a7 = self._Y0[a3[12]]
                            a5 = self._Y0[a3[13]]
                            aR = self._Y0[a3[14]]
                            aQ = self._Y0[a3[15]]
                            a9 = ba[0]
                            a8 = ba[1]
                            a6 = ba[2]
                            a4 = ba[3]
                            bC = aT._fL + (aS._fL - aT._fL) * a9
                            bB = bE._fL + (bD._fL - bE._fL) * a9
                            bz = aN._fL + (aM._fL - aN._fL) * a9
                            by = bp._fL + (bo._fL - bp._fL) * a9
                            bv = bh._fL + (bg._fL - bh._fL) * a9
                            bt = aY._fL + (aW._fL - aY._fL) * a9
                            br = a7._fL + (a5._fL - a7._fL) * a9
                            bq = aR._fL + (aQ._fL - aR._fL) * a9
                            bm._Yr._fL = (1 - a4) * (
                                    (1 - a6) * (bC + (bB - bC) * a8) + a6 * (bz + (by - bz) * a8)) + a4 * (
                                                 (1 - a6) * (bv + (bt - bv) * a8) + a6 * (br + (bq - br) * a8))
                            bC = aT._gL + (aS._gL - aT._gL) * a9
                            bB = bE._gL + (bD._gL - bE._gL) * a9
                            bz = aN._gL + (aM._gL - aN._gL) * a9
                            by = bp._gL + (bo._gL - bp._gL) * a9
                            bv = bh._gL + (bg._gL - bh._gL) * a9
                            bt = aY._gL + (aW._gL - aY._gL) * a9
                            br = a7._gL + (a5._gL - a7._gL) * a9
                            bq = aR._gL + (aQ._gL - aR._gL) * a9
                            bm._Yr._gL = (1 - a4) * (
                                    (1 - a6) * (bC + (bB - bC) * a8) + a6 * (bz + (by - bz) * a8)) + a4 * (
                                                 (1 - a6) * (bv + (bt - bv) * a8) + a6 * (br + (bq - br) * a8))
                            bC = aT._B0 + (aS._B0 - aT._B0) * a9
                            bB = bE._B0 + (bD._B0 - bE._B0) * a9
                            bz = aN._B0 + (aM._B0 - aN._B0) * a9
                            by = bp._B0 + (bo._B0 - bp._B0) * a9
                            bv = bh._B0 + (bg._B0 - bh._B0) * a9
                            bt = aY._B0 + (aW._B0 - aY._B0) * a9
                            br = a7._B0 + (a5._B0 - a7._B0) * a9
                            bq = aR._B0 + (aQ._B0 - aR._B0) * a9
                            bm._Yr._B0 = (1 - a4) * (
                                    (1 - a6) * (bC + (bB - bC) * a8) + a6 * (bz + (by - bz) * a8)) + a4 * (
                                                 (1 - a6) * (bv + (bt - bv) * a8) + a6 * (br + (bq - br) * a8))
                            bC = aT._z0 + (aS._z0 - aT._z0) * a9
                            bB = bE._z0 + (bD._z0 - bE._z0) * a9
                            bz = aN._z0 + (aM._z0 - aN._z0) * a9
                            by = bp._z0 + (bo._z0 - bp._z0) * a9
                            bv = bh._z0 + (bg._z0 - bh._z0) * a9
                            bt = aY._z0 + (aW._z0 - aY._z0) * a9
                            br = a7._z0 + (a5._z0 - a7._z0) * a9
                            bq = aR._z0 + (aQ._z0 - aR._z0) * a9
                            bm._Yr._z0 = (1 - a4) * (
                                    (1 - a6) * (bC + (bB - bC) * a8) + a6 * (bz + (by - bz) * a8)) + a4 * (
                                                 (1 - a6) * (bv + (bt - bv) * a8) + a6 * (br + (bq - br) * a8))
                            bC = aT._qT + (aS._qT - aT._qT) * a9
                            bB = bE._qT + (bD._qT - bE._qT) * a9
                            bz = aN._qT + (aM._qT - aN._qT) * a9
                            by = bp._qT + (bo._qT - bp._qT) * a9
                            bv = bh._qT + (bg._qT - bh._qT) * a9
                            bt = aY._qT + (aW._qT - aY._qT) * a9
                            br = a7._qT + (a5._qT - a7._qT) * a9
                            bq = aR._qT + (aQ._qT - aR._qT) * a9
                            bm._Yr._qT = (1 - a4) * (
                                    (1 - a6) * (bC + (bB - bC) * a8) + a6 * (bz + (by - bz) * a8)) + a4 * (
                                                 (1 - a6) * (bv + (bt - bv) * a8) + a6 * (br + (bq - br) * a8))
                        else:
                            aV = int(pow(2, a2))
                            aZ = Float32Array(aV)
                            for bk in range(0, aV, 1):
                                aI = bk
                                aH = 1
                                for aL in range(0, a2, 1):
                                    aH *= (1 - ba[aL]) if (aI % 2 == 0) else ba[aL]
                                    aI /= 2

                                aZ[bk] = aH

                            bA = Array()
                            for aU in range(0, aV, 1):
                                bA[aU] = self._Y0[a3[aU]]

                            be = 0
                            bc = 0
                            bd = 0
                            bb = 0
                            aX = 0
                            for aU in range(0, aV, 1):
                                be += aZ[aU] * bA[aU]._fL
                                bc += aZ[aU] * bA[aU]._gL
                                bd += aZ[aU] * bA[aU]._B0
                                bb += aZ[aU] * bA[aU]._z0
                                aX += aZ[aU] * bA[aU]._qT

                            bm._Yr._fL = be
                            bm._Yr._gL = bc
                            bm._Yr._B0 = bd
                            bm._Yr._z0 = bb
                            bm._Yr._qT = aX

        bn = self._Y0[a3[0]]
        bm._Yr.reflectX = bn.reflectX
        bm._Yr.reflectY = bn.reflectY

    def setupTransform(self, modelContext, aH):
        if not ((self == aH._GT())):
            print("### assert!! ### ")

        bdAffineContext = aH
        bdAffineContext._hS(True)
        if not self.needTransform():
            bdAffineContext.setTotalScale_notForClient(bdAffineContext._Yr._B0)
            bdAffineContext.setTotalOpacity(bdAffineContext.getInterpolatedOpacity())
        else:
            aT = self.getTargetBaseDataID()
            if bdAffineContext._8r == IBaseData._ur:
                bdAffineContext._8r = modelContext.getBaseDataIndex(aT)

            if bdAffineContext._8r < 0:
                if Live2D._so:
                    print("_L _0P _G :: %s", aT)

                bdAffineContext._hS(False)
            else:
                baseData = modelContext.getBaseData(bdAffineContext._8r)
                if baseData != None:
                    aL = modelContext._q2(bdAffineContext._8r)
                    aS = BDAffine._Xo
                    aS[0] = bdAffineContext._Yr._fL
                    aS[1] = bdAffineContext._Yr._gL
                    aJ = BDAffine._io
                    aJ[0] = 0
                    aJ[1] = -0.1
                    aO = aL._GT().getType()
                    if aO == IBaseData._c2:
                        aJ[1] = -10
                    else:
                        aJ[1] = -0.1

                    aQ = BDAffine._0o
                    self._Jr(modelContext, baseData, aL, aS, aJ, aQ)
                    aP = UtMath._92(aJ, aQ)
                    baseData._nb(modelContext, aL, aS, aS, 1, 0, 2)
                    bdAffineContext._Wr._fL = aS[0]
                    bdAffineContext._Wr._gL = aS[1]
                    bdAffineContext._Wr._B0 = bdAffineContext._Yr._B0
                    bdAffineContext._Wr._z0 = bdAffineContext._Yr._z0
                    bdAffineContext._Wr._qT = bdAffineContext._Yr._qT - aP * UtMath._NS
                    aK = aL.getTotalScale()
                    bdAffineContext.setTotalScale_notForClient(aK * bdAffineContext._Wr._B0)
                    aN = aL.getTotalOpacity()
                    bdAffineContext.setTotalOpacity(aN * bdAffineContext.getInterpolatedOpacity())
                    bdAffineContext._Wr.reflectX = bdAffineContext._Yr.reflectX
                    bdAffineContext._Wr.reflectY = bdAffineContext._Yr.reflectY
                    bdAffineContext._hS(aL.isAvailable())
                else:
                    bdAffineContext._hS(False)

    def _nb(self, aJ, aR, aL, a4, aT, aO, a2):
        if not ((self == aR._GT())):
            print("### assert!! ### ")

        aH = aR
        aU = aH._Wr if aH._Wr != None else aH._Yr
        a0 = math.sin(UtMath._bS * aU._qT)
        aP = math.cos(UtMath._bS * aU._qT)
        a3 = aH.getTotalScale()
        aW = -1 if aU.reflectX else 1
        aV = -1 if aU.reflectY else 1
        aS = aP * a3 * aW
        aQ = -a0 * a3 * aV
        a1 = a0 * a3 * aW
        aZ = aP * a3 * aV
        aY = aU._fL
        aX = aU._gL
        aI = aT * a2
        for aK in range(aO, aI, a2):
            aN = aL[aK]
            aM = aL[aK + 1]
            a4[aK] = aS * aN + aQ * aM + aY
            a4[aK + 1] = a1 * aN + aZ * aM + aX

    def _Jr(self, aP, aK, aI, aR, aQ, aH):
        if not ((aK == aI._GT())):
            print("### assert!! ### ")

        aO = BDAffine._Lo
        BDAffine._Lo[0] = aR[0]
        BDAffine._Lo[1] = aR[1]
        aK._nb(aP, aI, aO, aO, 1, 0, 2)
        aL = BDAffine._To
        aS = BDAffine._Po
        aN = 10
        aJ = 1
        for aM in range(0, aN, 1):
            aS[0] = aR[0] + aJ * aQ[0]
            aS[1] = aR[1] + aJ * aQ[1]
            aK._nb(aP, aI, aS, aL, 1, 0, 2)
            aL[0] -= aO[0]
            aL[1] -= aO[1]
            if aL[0] != 0 or aL[1] != 0:
                aH[0] = aL[0]
                aH[1] = aL[1]
                return

            aS[0] = aR[0] - aJ * aQ[0]
            aS[1] = aR[1] - aJ * aQ[1]
            aK._nb(aP, aI, aS, aL, 1, 0, 2)
            aL[0] -= aO[0]
            aL[1] -= aO[1]
            if aL[0] != 0 or aL[1] != 0:
                aL[0] = -aL[0]
                aL[0] = -aL[0]
                aH[0] = aL[0]
                aH[1] = aL[1]
                return

            aJ *= 0.1

        if Live2D._so:
            print("_L0 to transform _SP\n")


class BDAffineContext(IBaseContext):

    def __init__(self, aH):
        super().__init__(aH)
        # IBaseContext.prototype.constructor.call(self, aH)
        self._8r = IBaseData._ur
        self._Yr = None
        self._Wr = None


class IDrawData2(IDrawData1):
    _ur = -2
    _ES = 500
    _wb = 2
    _8S = 3
    _os = 4
    _52 = _ES
    _R2 = _ES

    def __init__(self):
        # IDrawData1.prototype.constructor.call(self)
        super().__init__()
        self._gP = None
        self._dr = None
        self._GS = None
        self._qb = None
        self._Lb = None
        self._mS = None

    def read(self, aH):
        self._gP = aH._nP()
        self._dr = aH._nP()
        self._GS = aH._nP()
        self._qb = aH._6L()
        self._Lb = aH._cS()
        self._mS = aH._Tb()
        if aH.getFormatVersion() >= FileFormat2._T7:
            self.clipID = aH._nP()
            self.clipIDList = self.convertClipIDForV2_11(self.clipID)
        else:
            self.clipIDList = None

        IDrawData2._Sb(self._Lb)

    def getClipIDList(self):
        return self.clipIDList

    def setupInterpolate(self, aI, aH):
        aH._IS[0] = False
        aH._Us = aG._Z2(aI, self._GS, aH._IS, self._Lb)
        if Live2D._Zs:
            pass
        else:
            if aH._IS[0]:
                return

        aH._7s = aG._br(aI, self._GS, aH._IS, self._mS)

    def setupTransform(self, aH):
        pass

    def getDrawDataID(self):
        return self._gP

    def _j2(self, aH):
        self._gP = aH

    def getOpacity(self, aH, aI):
        return aI._7s

    def _zS(self, aH, aI):
        return aI._Us

    def getTargetBaseDataID(self):
        return self._dr

    def _gs(self, aH):
        self._dr = aH

    def needTransform(self):
        return (self._dr != None and (self._dr != BaseDataID._2o()))

    def getType(self):
        pass

    @staticmethod
    def _Sb(aJ):
        for aI in range(len(aJ) - 1, 0 - 1, -1):
            aH = aJ[aI]
            if aH < IDrawData2._52:
                IDrawData2._52 = aH
            else:
                if aH > IDrawData2._R2:
                    IDrawData2._R2 = aH

    @staticmethod
    def _or():
        return IDrawData2._52

    @staticmethod
    def _Pr():
        return IDrawData2._R2


class AvatarPartsItem():
    _42 = 0

    def __init__(self):
        self._NL = None
        self._3S = None
        self._aS = None
        AvatarPartsItem._42 += 1

    def _1b(self):
        return self._3S

    def getDrawDataList(self):
        return self._aS

    def read(self, aH):
        self._NL = aH._nP()
        self._aS = aH._nP()
        self._3S = aH._nP()

    def _kr(self, aH):
        aH._Zo(self._3S)
        aH._xo(self._aS)
        self._3S = None
        self._aS = None


class ALive2DModel:
    _0s = 1
    _4s = 2
    _42 = 0

    def __init__(self):
        self.modelImpl = None
        self._5S = None
        self._NP = 0
        ALive2DModel._42 += 1
        self._5S = ModelContext(self)

    def _KS(self, aH):
        self.modelImpl = aH

    def getModelImpl(self):
        if self.modelImpl is None:
            self.modelImpl = ModelImpl()
            self.modelImpl.initDirect()

        return self.modelImpl

    def getCanvasWidth(self):
        if self.modelImpl is None:
            return 0

        return self.modelImpl.getCanvasWidth()

    def getCanvasHeight(self):
        if self.modelImpl is None:
            return 0

        return self.modelImpl.getCanvasHeight()

    def getParamFloat(self, aH):
        aH = self._5S.getParamIndex(ParamID.getID(aH))

        return self._5S.getParamFloat(aH)

    def setParamFloat(self, aH, aJ, aI=1):
        aH = self._5S.getParamIndex(ParamID.getID(aH))
        aJ = 0 if aJ is None else aJ
        self._5S.setParamFloat(aH, self._5S.getParamFloat(aH) * (1 - aI) + aJ * aI)

    def addToParamFloat(self, aH, aJ, aI=1):
        aH = self._5S.getParamIndex(ParamID.getID(aH))

        self._5S.setParamFloat(aH, self._5S.getParamFloat(aH) + aJ * aI)

    def multParamFloat(self, aH, aJ, aI=1):
        aH = self._5S.getParamIndex(ParamID.getID(aH))

        self._5S.setParamFloat(aH, self._5S.getParamFloat(aH) * (1 + (aJ - 1) * aI))

    def getParamIndex(self, aH):
        return self._5S.getParamIndex(ParamID.getID(aH))

    def loadParam(self):
        self._5S.loadParam()

    def saveParam(self):
        self._5S.saveParam()

    def init(self):
        self._5S.init()

    def update(self):
        self._5S.update()

    def _Rs(self):
        print("_60 _PT _Rs()")
        return -1

    def _Ds(self, aH):
        print("_60 _PT _SS#_Ds() \n")

    def _K2(self):
        pass

    def draw(self):
        pass

    def getModelContext(self):
        return self._5S

    def _s2(self):
        return self._NP

    def _P7(self, aK, aR, aH, a0):
        aU = -1
        aY = 0
        aM = self
        aJ = 0.5
        aI = 0.15
        aX = True
        if aH == 0:
            for aV in range(0, len(aK), 1):
                aP = aK[aV]
                aO = aR[aV]
                aS = (aM.getParamFloat(aP) != 0)
                aM.setPartsOpacity(aO, (1 if aS else 0))

            return
        else:
            if len(aK) == 1:
                aP = aK[0]
                aT = (aM.getParamFloat(aP) != 0)
                aO = aR[0]
                aQ = aM.getPartsOpacity(aO)
                aW = aH / a0
                if aT:
                    aQ += aW
                    if aQ > 1:
                        aQ = 1
                else:
                    aQ -= aW
                    if aQ < 0:
                        aQ = 0

                aM.setPartsOpacity(aO, aQ)
            else:
                for aV in range(0, len(aK), 1):
                    aP = aK[aV]
                    aS = (aM.getParamFloat(aP) != 0)
                    if aS:
                        if aU >= 0:
                            break

                        aU = aV
                        aO = aR[aV]
                        aY = aM.getPartsOpacity(aO)
                        aY += aH / a0
                        if aY > 1:
                            aY = 1

                if aU < 0:
                    print("No _wi _q0/ _U default[%s]", aK[0])
                    aU = 0
                    aY = 1
                    aM.loadParam()
                    aM.setParamFloat(aK[aU], aY)
                    aM.saveParam()

                for aV in range(0, len(aK), 1):
                    aO = aR[aV]
                    if aU == aV:
                        aM.setPartsOpacity(aO, aY)
                    else:
                        aL = aM.getPartsOpacity(aO)
                        aZ = None
                        if aY < aJ:
                            aZ = aY * (aJ - 1) / aJ + 1
                        else:
                            aZ = (1 - aY) * aJ / (1 - aJ)

                        if aX:
                            aN = (1 - aZ) * (1 - aY)
                            if aN > aI:
                                aZ = 1 - aI / (1 - aY)

                        if aL > aZ:
                            aL = aZ

                        aM.setPartsOpacity(aO, aL)

    def setPartsOpacity(self, aI, aH):
        if not isinstance(aI, int):
            aI = self._5S.getPartsDataIndex(PartsDataID.getID(aI))

        self._5S.setPartsOpacity(aI, aH)

    def getPartsDataIndex(self, aH):
        if not (isinstance(aH, PartsDataID)):
            aH = PartsDataID.getID(aH)

        return self._5S.getPartsDataIndex(aH)

    def getPartsOpacity(self, aH):
        if not isinstance(aH, int):
            aH = self._5S.getPartsDataIndex(PartsDataID.getID(aH))

        if aH < 0:
            return 0

        return self._5S.getPartsOpacity(aH)

    def getDrawParam(self):
        pass

    def getDrawDataIndex(self, aH):
        return self._5S.getDrawDataIndex(DrawDataID.getID(aH))

    def getDrawData(self, aH):
        return self._5S.getDrawData(aH)

    def getTransformedPoints(self, aH):
        aI = self._5S._C2(aH)
        if isinstance(aI, DDTextureContext):
            return (aI).getTransformedPoints()

        return None

    def getIndexArray(self, aI):
        if aI < 0 or aI >= len(self._5S._aS):
            return None

        aH = self._5S._aS[aI]
        if aH is not None and aH.getType() == IDrawData2._wb:
            if isinstance(aH, DDTexture):
                return aH.getIndexArray()

        return None

    @staticmethod
    def loadModel_exe(aQ, aU: bytes):

        if not (isinstance(aU, bytes)):
            raise LDError("_SS#loadModel(b) / b _x be DataView or ArrayBuffer")

        br = BReader(aU)
        aM = br.readByte()
        aK = br.readByte()
        aJ = br.readByte()
        if aM == 109 and aK == 111 and aJ == 99:
            version = br.readByte()
        else:
            raise LDError("Invalid MOC file.")

        br._gr(version)
        if version > FileFormat2._T7:
            aQ._NP |= ALive2DModel._4s
            aR = FileFormat2._T7
            aI = "Unsupported version %d\n" % version
            raise LDError(aI)

        aL = br._nP()
        if version >= FileFormat2._s7:
            aH = br._9T()
            aT = br._9T()
            if aH != -30584 or aT != -30584:
                aQ._NP |= ALive2DModel._0s
                raise LDError("_gi _C _li , _0 _6 _Ui.")

        aQ._KS(aL)
        modelContext = aQ.getModelContext()
        modelContext.setDrawParam(aQ.getDrawParam())
        modelContext.init()


class Live2DModelJS(ALive2DModel):

    def __init__(self):
        super().__init__()
        self._zo = DrawParamOpenGLES2()

    def setGL(self, aH):
        self._zo.setGL(aH)

    def setTransform(self, aH):
        self._zo.setTransform(aH)

    def draw(self):
        self._5S.draw(self._zo)

    def _K2(self):
        self._zo._K2()

    def _Rs(self):
        return self._zo._Rs()

    def _Ds(self, aH):
        self._zo._Ds(aH)

    def getDrawParam(self):
        return self._zo

    @staticmethod
    def loadModel(aI):
        aH = Live2DModelJS()
        ALive2DModel.loadModel_exe(aH, aI)
        return aH

    @staticmethod
    def _to():
        aH = Live2DModelJS()
        return aH

    def setTexture(self, aI, aH):
        if self._zo == None:
            print("_Yi for QT _ki / _XS() is _6 _ui!!")

        self._zo.setTexture(aI, aH)


class Live2DMotion(AMotion):
    _cs = "VISIBLE:"
    _ar = "LAYOUT:"
    MTN_PREFIX_FADEIN = "FADEIN:"
    MTN_PREFIX_FADEOUT = "FADEOUT:"
    _Co = 0
    _1T = 1

    def __init__(self):

        super().__init__()
        self.motions = Array()
        self._o2 = None
        self._7r = Live2DMotion._Co
        Live2DMotion._Co += 1
        self._D0 = 30
        self._yT = 0
        self._E = False
        self.loopFadeIn = True
        self._rr = -1
        self._eP = 0

    def getDurationMSec(self):
        return -1 if self._E else self._rr

    def getLoopDurationMSec(self):
        return self._rr

    def dump(self):
        for aJ in range(0, len(self.motions), 1):
            aH = self.motions[aJ]
            print("_wL[%s] [%d]. ", aH._4P, len(aH._I0))
            for aI in range(0, 10, 1):
                print("%5.2f ,", aH._I0[aI])

            print("\n")

    def updateParamExe(self, aJ, aN, aQ, a3):
        aO = aN - a3._z2
        a0 = aO * self._D0 / 1000
        aK = int(a0)
        aR = a0 - aK
        for aZ in range(0, len(self.motions), 1):
            aV = self.motions[aZ]
            aL = len(aV._I0)
            aT = aV._4P
            if aV._RP == t._hs:
                aX = aV._I0[(aL - 1 if aK >= aL else aK)]
                aJ.setParamFloat(aT, aX)
            else:
                if t._ws <= aV._RP <= t._Ys:
                    pass
                else:
                    aH = aJ.getParamIndex(aT)
                    a4 = aJ.getModelContext()
                    aY = a4.getParamMax(aH)
                    aW = a4.getParamMin(aH)
                    aM = 0.4
                    aS = aM * (aY - aW)
                    aU = a4.getParamFloat(aH)
                    a2 = aV._I0[(aL - 1 if aK >= aL else aK)]
                    a1 = aV._I0[(aL - 1 if aK + 1 >= aL else aK + 1)]
                    if (a2 < a1 and a1 - a2 > aS) or (a2 > a1 and a2 - a1 > aS):
                        aI = a2
                    else:
                        aI = a2 + (a1 - a2) * aR

                    aP = aU + (aI - aU) * aQ
                    aJ.setParamFloat(aT, aP)

        if aK >= self._yT:
            if self._E:
                a3._z2 = aN
                if self.loopFadeIn:
                    a3._bs = aN
            else:
                a3._9L = True

        self._eP = aQ

    def _r0(self):
        return self._E

    def _aL(self, aH):
        self._E = aH

    def _S0(self):
        return self._D0

    def _U0(self, aH):
        self._D0 = aH

    def isLoopFadeIn(self):
        return self.loopFadeIn

    def setLoopFadeIn(self, aH):
        self.loopFadeIn = aH

    @staticmethod
    def loadMotion(aT: bytes):
        aN = Live2DMotion()
        aI = [0]
        aQ = len(aT)
        aN._yT = 0
        # for(aJ = 0; aJ < aQ; ++aJ):
        aJ = 0
        while aJ < aQ:
            aS = p(aT, aJ)
            aL = ord(aS[0])
            if aS == "\n" or aS == "\r":
                aJ += 1
                continue

            if aS == "#":
                # for(; aJ < aQ; ++aJ):
                while aJ < aQ:
                    if p(aT, aJ) == "\n" or p(aT, aJ) == "\r":
                        break
                    aJ += 1

                aJ += 1
                continue

            if aS == "":
                aV = aJ
                aK = -1
                # for(; aJ < aQ; ++aJ):
                while aJ < aQ:
                    aS = p(aT, aJ)
                    if aS == "\r" or aS == "\n":
                        break

                    if aS == "=":
                        aK = aJ
                        break
                    aJ += 1

                aP = False
                if aK >= 0:
                    if aK == aV + 4 and p(aT, aV + 1) == "f" and p(aT, aV + 2) == "p" and p(aT, aV + 3) == "s":
                        aP = True

                    # for(aJ = aK + 1; aJ < aQ; ++aJ):
                    aJ = aK + 1
                    while aJ < aQ:
                        aS = p(aT, aJ)
                        if aS == "\r" or aS == "\n":
                            break

                        if aS == "," or aS == " " or aS == "\t":
                            aJ += 1
                            continue

                        aM = UtString.strToFloat(aT, aQ, aJ, aI)
                        if aI[0] > 0:
                            if aP and 5 < aM < 121:
                                aN._D0 = aM

                        aJ = aI[0]
                        aJ += 1

                # for(; aJ < aQ; ++aJ):
                while aJ < aQ:
                    if p(aT, aJ) == "\n" or p(aT, aJ) == "\r":
                        break
                    aJ += 1

                aJ += 1
                continue

            if (97 <= aL <= 122) or (65 <= aL <= 90) or aS == "_":
                aV = aJ
                aK = -1
                # for(; aJ < aQ; ++aJ):
                while aJ < aQ:
                    aS = p(aT, aJ)
                    if aS == "\r" or aS == "\n":
                        break

                    if aS == "=":
                        aK = aJ
                        break
                    aJ += 1

                if aK >= 0:
                    aO = t()
                    if UtString.startswith(aT, aV, Live2DMotion._cs):
                        aO._RP = t._hs
                        aO._4P = UtString.createString(aT, aV, aK - aV)
                    else:
                        if UtString.startswith(aT, aV, Live2DMotion._ar):
                            aO._4P = UtString.createString(aT, aV + 7, aK - aV - 7)
                            if UtString.startswith(aT, aV + 7, "ANCHOR_X"):
                                aO._RP = t._xs
                            else:
                                if UtString.startswith(aT, aV + 7, "ANCHOR_Y"):
                                    aO._RP = t._us
                                else:
                                    if UtString.startswith(aT, aV + 7, "SCALE_X"):
                                        aO._RP = t._qs
                                    else:
                                        if UtString.startswith(aT, aV + 7, "SCALE_Y"):
                                            aO._RP = t._Ys
                                        else:
                                            if UtString.startswith(aT, aV + 7, "AffineEnt"):
                                                aO._RP = t._ws
                                            else:
                                                if UtString.startswith(aT, aV + 7, "Y"):
                                                    aO._RP = t._Ns
                        else:
                            aO._RP = t._Fr
                            aO._4P = UtString.createString(aT, aV, aK - aV)

                    aN.motions.append(aO)
                    aU = 0
                    aR = []
                    aJ = aK + 1
                    while aJ < aQ:
                        # for(aJ = aK + 1; aJ < aQ; ++aJ):
                        aS = p(aT, aJ)
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
                                print("_n0 _hi . @Live2DMotion loadMotion()\n")
                                break

                            aJ = aH - 1
                        aJ += 1

                    aO._I0 = aR
                    if aU > aN._yT:
                        aN._yT = aU

            aJ += 1

        aN._rr = int((1000 * aN._yT) / aN._D0)
        return aN


def p(aI, aH):
    return chr(aI[aH])


class aE():

    def __init__(self):
        self._P = Float32Array(100)
        self.size = 0

    def clear(self):
        self.size = 0

    def add(self, aI):
        if len(self._P) <= self.size:
            aH = Float32Array(self.size * 2)
            UtSystem._jT(self._P, 0, aH, 0, self.size)
            self._P = aH

        self._P[self.size] = aI
        self.size += 1

    def _BL(self):
        aH = Float32Array(self.size)
        UtSystem._jT(self._P, 0, aH, 0, self.size)
        return aH


class BufType():

    def __init__(self):
        self._4P = None
        self._I0 = None
        self._RP = None

    _Fr = 0
    _hs = 1
    _ws = 100
    _Ns = 101
    _xs = 102
    _us = 103
    _qs = 104
    _Ys = 105


class BDBoxGrid(IBaseData):
    _gT = [None]

    def __init__(self):
        super().__init__()
        # IBaseData.prototype.constructor.call(self)
        self._o = 0
        self._A = 0
        self._GS = None
        self._Eo = None

    def _zP(self):
        self._GS = PivotManager()
        self._GS._zP()

    def read(self, aH):
        super().read(aH)
        self._A = aH._6L()
        self._o = aH._6L()
        self._GS = aH._nP()
        self._Eo = aH._nP()
        super().readV2_opacity(aH)

    def init(self, aH):
        aI = BDBoxGridContext(self)
        aJ = (self._o + 1) * (self._A + 1)
        if aI._Cr != None:
            aI._Cr = None

        aI._Cr = Float32Array(aJ * 2)
        if aI._hr != None:
            aI._hr = None

        if self.needTransform():
            aI._hr = Float32Array(aJ * 2)
        else:
            aI._hr = None

        return aI

    def setupInterpolate(self, aJ, aI):
        aK = aI
        if not self._GS._Ur(aJ):
            return

        aL = self._VT()
        aH = BDBoxGrid._gT
        aH[0] = False
        aG._Vr(aJ, self._GS, aH, aL, self._Eo, aK._Cr, 0, 2)
        aI._Ib(aH[0])
        self.interpolateOpacity(aJ, self._GS, aI, aH)

    def setupTransform(self, aK, aJ):
        aL = aJ
        aL._hS(True)
        if not self.needTransform():
            aL.setTotalOpacity(aL.getInterpolatedOpacity())
        else:
            aH = self.getTargetBaseDataID()
            if aL._8r == IBaseData._ur:
                aL._8r = aK.getBaseDataIndex(aH)

            if aL._8r < 0:
                if Live2D._so:
                    print("_L _0P _G :: %s", aH)

                aL._hS(False)
            else:
                aN = aK.getBaseData(aL._8r)
                aI = aK._q2(aL._8r)
                if aN != None and aI.isAvailable():
                    aM = aI.getTotalScale()
                    aL.setTotalScale_notForClient(aM)
                    aO = aI.getTotalOpacity()
                    aL.setTotalOpacity(aO * aL.getInterpolatedOpacity())
                    aN._nb(aK, aI, aL._Cr, aL._hr, self._VT(), 0, 2)
                    aL._hS(True)
                else:
                    aL._hS(False)

    def _nb(self, aL, aI, aH, aM, aO, aK, aJ):
        aN = aI
        aP = aN._hr if (aN._hr != None) else aN._Cr
        BDBoxGrid.transformPoints_sdk2(aH, aM, aO, aK, aJ, aP, self._o, self._A)

    def _VT(self):
        return (self._o + 1) * (self._A + 1)

    def getType(self):
        return IBaseData._b_

    @staticmethod
    def transformPoints_sdk2(hvs, dst, pointCount, srcOffset, srcStep, grid, row, col):
        aW = pointCount * srcStep
        aT = 0
        aS = 0
        bl = 0
        bk = 0
        bf = 0
        be = 0
        aZ = False
        for ba in range(srcOffset, aW, srcStep):
            a4 = hvs[ba]
            aX = hvs[ba + 1]
            bd = a4 * row
            a7 = aX * col
            if bd < 0 or a7 < 0 or row <= bd or col <= a7:
                a1 = row + 1
                if not aZ:
                    aZ = True
                    aT = 0.25 * (grid[((0) + (0) * a1) * 2] + grid[((row) + (0) * a1) * 2] + grid[
                        ((0) + (col) * a1) * 2] +
                                 grid[((row) + (col) * a1) * 2])
                    aS = 0.25 * (grid[((0) + (0) * a1) * 2 + 1] + grid[((row) + (0) * a1) * 2 + 1] + grid[
                        ((0) + (col) * a1) * 2 + 1] + grid[((row) + (col) * a1) * 2 + 1])
                    aM = grid[((row) + (col) * a1) * 2] - grid[((0) + (0) * a1) * 2]
                    aL = grid[((row) + (col) * a1) * 2 + 1] - grid[((0) + (0) * a1) * 2 + 1]
                    bh = grid[((row) + (0) * a1) * 2] - grid[((0) + (col) * a1) * 2]
                    bg = grid[((row) + (0) * a1) * 2 + 1] - grid[((0) + (col) * a1) * 2 + 1]
                    bl = (aM + bh) * 0.5
                    bk = (aL + bg) * 0.5
                    bf = (aM - bh) * 0.5
                    be = (aL - bg) * 0.5
                    aT -= 0.5 * (bl + bf)
                    aS -= 0.5 * (bk + be)

                if (-2 < a4 and a4 < 3) and (-2 < aX and aX < 3):
                    if a4 <= 0:
                        if aX <= 0:
                            a3 = grid[((0) + (0) * a1) * 2]
                            a2 = grid[((0) + (0) * a1) * 2 + 1]
                            a8 = aT - 2 * bl
                            a6 = aS - 2 * bk
                            aK = aT - 2 * bf
                            aJ = aS - 2 * be
                            aO = aT - 2 * bl - 2 * bf
                            aN = aS - 2 * bk - 2 * be
                            bj = 0.5 * (a4 - (-2))
                            bi = 0.5 * (aX - (-2))
                            if bj + bi <= 1:
                                dst[ba] = aO + (aK - aO) * bj + (a8 - aO) * bi
                                dst[ba + 1] = aN + (aJ - aN) * bj + (a6 - aN) * bi
                            else:
                                dst[ba] = a3 + (a8 - a3) * (1 - bj) + (aK - a3) * (1 - bi)
                                dst[ba + 1] = a2 + (a6 - a2) * (1 - bj) + (aJ - a2) * (1 - bi)
                        else:
                            if aX >= 1:
                                aK = grid[((0) + (col) * a1) * 2]
                                aJ = grid[((0) + (col) * a1) * 2 + 1]
                                aO = aT - 2 * bl + 1 * bf
                                aN = aS - 2 * bk + 1 * be
                                a3 = aT + 3 * bf
                                a2 = aS + 3 * be
                                a8 = aT - 2 * bl + 3 * bf
                                a6 = aS - 2 * bk + 3 * be
                                bj = 0.5 * (a4 - (-2))
                                bi = 0.5 * (aX - (1))
                                if bj + bi <= 1:
                                    dst[ba] = aO + (aK - aO) * bj + (a8 - aO) * bi
                                    dst[ba + 1] = aN + (aJ - aN) * bj + (a6 - aN) * bi
                                else:
                                    dst[ba] = a3 + (a8 - a3) * (1 - bj) + (aK - a3) * (1 - bi)
                                    dst[ba + 1] = a2 + (a6 - a2) * (1 - bj) + (aJ - a2) * (1 - bi)
                            else:
                                aH = int(a7)
                                if aH == col:
                                    aH = col - 1

                                bj = 0.5 * (a4 - (-2))
                                bi = a7 - aH
                                bb = aH / col
                                a9 = (aH + 1) / col
                                aK = grid[((0) + (aH) * a1) * 2]
                                aJ = grid[((0) + (aH) * a1) * 2 + 1]
                                a3 = grid[((0) + (aH + 1) * a1) * 2]
                                a2 = grid[((0) + (aH + 1) * a1) * 2 + 1]
                                aO = aT - 2 * bl + bb * bf
                                aN = aS - 2 * bk + bb * be
                                a8 = aT - 2 * bl + a9 * bf
                                a6 = aS - 2 * bk + a9 * be
                                if bj + bi <= 1:
                                    dst[ba] = aO + (aK - aO) * bj + (a8 - aO) * bi
                                    dst[ba + 1] = aN + (aJ - aN) * bj + (a6 - aN) * bi
                                else:
                                    dst[ba] = a3 + (a8 - a3) * (1 - bj) + (aK - a3) * (1 - bi)
                                    dst[ba + 1] = a2 + (a6 - a2) * (1 - bj) + (aJ - a2) * (1 - bi)
                    else:
                        if 1 <= a4:
                            if aX <= 0:
                                a8 = grid[((row) + (0) * a1) * 2]
                                a6 = grid[((row) + (0) * a1) * 2 + 1]
                                a3 = aT + 3 * bl
                                a2 = aS + 3 * bk
                                aO = aT + 1 * bl - 2 * bf
                                aN = aS + 1 * bk - 2 * be
                                aK = aT + 3 * bl - 2 * bf
                                aJ = aS + 3 * bk - 2 * be
                                bj = 0.5 * (a4 - (1))
                                bi = 0.5 * (aX - (-2))
                                if bj + bi <= 1:
                                    dst[ba] = aO + (aK - aO) * bj + (a8 - aO) * bi
                                    dst[ba + 1] = aN + (aJ - aN) * bj + (a6 - aN) * bi
                                else:
                                    dst[ba] = a3 + (a8 - a3) * (1 - bj) + (aK - a3) * (1 - bi)
                                    dst[ba + 1] = a2 + (a6 - a2) * (1 - bj) + (aJ - a2) * (1 - bi)
                            else:
                                if aX >= 1:
                                    aO = grid[((row) + (col) * a1) * 2]
                                    aN = grid[((row) + (col) * a1) * 2 + 1]
                                    aK = aT + 3 * bl + 1 * bf
                                    aJ = aS + 3 * bk + 1 * be
                                    a8 = aT + 1 * bl + 3 * bf
                                    a6 = aS + 1 * bk + 3 * be
                                    a3 = aT + 3 * bl + 3 * bf
                                    a2 = aS + 3 * bk + 3 * be
                                    bj = 0.5 * (a4 - (1))
                                    bi = 0.5 * (aX - (1))
                                    if bj + bi <= 1:
                                        dst[ba] = aO + (aK - aO) * bj + (a8 - aO) * bi
                                        dst[ba + 1] = aN + (aJ - aN) * bj + (a6 - aN) * bi
                                    else:
                                        dst[ba] = a3 + (a8 - a3) * (1 - bj) + (aK - a3) * (1 - bi)
                                        dst[ba + 1] = a2 + (a6 - a2) * (1 - bj) + (aJ - a2) * (1 - bi)
                                else:
                                    aH = int(a7)
                                    if aH == col:
                                        aH = col - 1

                                    bj = 0.5 * (a4 - (1))
                                    bi = a7 - aH
                                    bb = aH / col
                                    a9 = (aH + 1) / col
                                    aO = grid[((row) + (aH) * a1) * 2]
                                    aN = grid[((row) + (aH) * a1) * 2 + 1]
                                    a8 = grid[((row) + (aH + 1) * a1) * 2]
                                    a6 = grid[((row) + (aH + 1) * a1) * 2 + 1]
                                    aK = aT + 3 * bl + bb * bf
                                    aJ = aS + 3 * bk + bb * be
                                    a3 = aT + 3 * bl + a9 * bf
                                    a2 = aS + 3 * bk + a9 * be
                                    if bj + bi <= 1:
                                        dst[ba] = aO + (aK - aO) * bj + (a8 - aO) * bi
                                        dst[ba + 1] = aN + (aJ - aN) * bj + (a6 - aN) * bi
                                    else:
                                        dst[ba] = a3 + (a8 - a3) * (1 - bj) + (aK - a3) * (1 - bi)
                                        dst[ba + 1] = a2 + (a6 - a2) * (1 - bj) + (aJ - a2) * (1 - bi)
                        else:
                            if aX <= 0:
                                aY = int(bd)
                                if aY == row:
                                    aY = row - 1

                                bj = bd - aY
                                bi = 0.5 * (aX - (-2))
                                bp = aY / row
                                bo = (aY + 1) / row
                                a8 = grid[((aY) + (0) * a1) * 2]
                                a6 = grid[((aY) + (0) * a1) * 2 + 1]
                                a3 = grid[((aY + 1) + (0) * a1) * 2]
                                a2 = grid[((aY + 1) + (0) * a1) * 2 + 1]
                                aO = aT + bp * bl - 2 * bf
                                aN = aS + bp * bk - 2 * be
                                aK = aT + bo * bl - 2 * bf
                                aJ = aS + bo * bk - 2 * be
                                if bj + bi <= 1:
                                    dst[ba] = aO + (aK - aO) * bj + (a8 - aO) * bi
                                    dst[ba + 1] = aN + (aJ - aN) * bj + (a6 - aN) * bi
                                else:
                                    dst[ba] = a3 + (a8 - a3) * (1 - bj) + (aK - a3) * (1 - bi)
                                    dst[ba + 1] = a2 + (a6 - a2) * (1 - bj) + (aJ - a2) * (1 - bi)
                            else:
                                if aX >= 1:
                                    aY = int(bd)
                                    if aY == row:
                                        aY = row - 1

                                    bj = bd - aY
                                    bi = 0.5 * (aX - (1))
                                    bp = aY / row
                                    bo = (aY + 1) / row
                                    aO = grid[((aY) + (col) * a1) * 2]
                                    aN = grid[((aY) + (col) * a1) * 2 + 1]
                                    aK = grid[((aY + 1) + (col) * a1) * 2]
                                    aJ = grid[((aY + 1) + (col) * a1) * 2 + 1]
                                    a8 = aT + bp * bl + 3 * bf
                                    a6 = aS + bp * bk + 3 * be
                                    a3 = aT + bo * bl + 3 * bf
                                    a2 = aS + bo * bk + 3 * be
                                    if bj + bi <= 1:
                                        dst[ba] = aO + (aK - aO) * bj + (a8 - aO) * bi
                                        dst[ba + 1] = aN + (aJ - aN) * bj + (a6 - aN) * bi
                                    else:
                                        dst[ba] = a3 + (a8 - a3) * (1 - bj) + (aK - a3) * (1 - bi)
                                        dst[ba + 1] = a2 + (a6 - a2) * (1 - bj) + (aJ - a2) * (1 - bi)
                                else:
                                    print("_li calc : %.4f , %.4f					@@BDBoxGrid\n", a4, aX)
                else:
                    dst[ba] = aT + a4 * bl + aX * bf
                    dst[ba + 1] = aS + a4 * bk + aX * be
            else:
                bn = bd - int(bd)
                bm = a7 - int(a7)
                aV = 2 * (int(bd) + int(a7) * (row + 1))
                if bn + bm < 1:
                    dst[ba] = grid[aV] * (1 - bn - bm) + grid[aV + 2] * bn + grid[aV + 2 * (row + 1)] * bm
                    dst[ba + 1] = grid[aV + 1] * (1 - bn - bm) + grid[aV + 3] * bn + grid[aV + 2 * (row + 1) + 1] * bm
                else:
                    dst[ba] = grid[aV + 2 * (row + 1) + 2] * (bn - 1 + bm) + grid[aV + 2 * (row + 1)] * (1 - bn) + grid[
                        aV + 2] * (1 - bm)
                    dst[ba + 1] = grid[aV + 2 * (row + 1) + 3] * (bn - 1 + bm) + grid[aV + 2 * (row + 1) + 1] * (
                            1 - bn) + \
                                  grid[aV + 3] * (1 - bm)


class BDBoxGridContext(IBaseContext):

    def __init__(self, aH):
        super().__init__(aH)
        self._8r = IBaseData._ur
        self._Cr = None
        self._hr = None


class PartsData:
    _42 = 0

    def __init__(self):
        self.visible = True
        self._g0 = False
        self._NL = None
        self._3S = None
        self._aS = None
        PartsData._42 += 1

    def _zP(self):
        self._3S = Array()
        self._aS = Array()

    def read(self, aH):
        self._g0 = aH._8L()
        self.visible = aH._8L()
        self._NL = aH._nP()
        self._3S = aH._nP()
        self._aS = aH._nP()

    def init(self, aI):
        aH = PartsDataContext(self)
        aH.setPartsOpacity(1 if self.isVisible() else 0)
        return aH

    def _6o(self, aH):
        if self._3S is None:
            raise LDError("_3S _6 _Wo@_6o")

        self._3S.append(aH)

    def _3o(self, aH):
        if self._aS is None:
            raise LDError("_aS _6 _Wo@_3o")

        self._aS.append(aH)

    def _Zo(self, aH):
        self._3S = aH

    def _xo(self, aH):
        self._aS = aH

    def isVisible(self):
        return self.visible

    def _uL(self):
        return self._g0

    def _KP(self, aH):
        self.visible = aH

    def _ET(self, aH):
        self._g0 = aH

    def getBaseData(self):
        return self._3S

    def getDrawData(self):
        return self._aS

    def _p2(self):
        return self._NL

    def _ob(self, aH):
        self._NL = aH

    def getPartsID(self):
        return self._NL

    def _MP(self, aH):
        self._NL = aH


class PartsDataContext(S):

    def __init__(self, aH):
        super().__init__()
        self._VS = None
        self._e0 = None
        self._e0 = aH

    def getPartsOpacity(self):
        return self._VS

    def setPartsOpacity(self, aH):
        self._VS = aH


class ISerializableV2():

    def __init__(self):
        pass

    def read(self, aH):
        pass


class ParamDefSet():

    def __init__(self):
        self._4S = None

    def _1s(self):
        return self._4S

    def _zP(self):
        self._4S = Array()

    def read(self, aH):
        self._4S = aH._nP()

    def _Ks(self, aH):
        self._4S.append(aH)


class LDTransform():

    def __init__(self):
        self.m = [1, 0, 0, 0, 1, 0, 0, 0, 1]

    def setContext(self, aI):
        aH = self.m
        aI.transform(aH[0], aH[1], aH[3], aH[4], aH[6], aH[7])

    def __str__(self):
        return self.toString()

    def toString(self):
        aI = "LDTransform { "
        for aH in range(0, 9, 1):
            aI += self.m[aH].toFixed(2) + " ,"

        aI += " }"
        return aI

    def identity(self):
        aH = self.m
        aH[0] = aH[4] = aH[8] = 1
        aH[1] = aH[2] = aH[3] = aH[5] = aH[6] = aH[7] = 0

    def _PS(self, aI, aK, aJ):
        if aJ == None:
            aJ = Array(0, 0)

        aH = self.m
        aJ[0] = aH[0] * aI + aH[3] * aK + aH[6]
        aJ[1] = aH[1] * aI + aH[4] * aK + aH[7]
        return aJ

    def _P2(self, aK):
        if not aK:
            aK = LDTransform()

        aI = self.m
        aT = aI[0]
        aS = aI[1]
        aR = aI[2]
        aQ = aI[3]
        aP = aI[4]
        aO = aI[5]
        aN = aI[6]
        aM = aI[7]
        aL = aI[8]
        aJ = aT * aP * aL + aS * aO * aN + aR * aQ * aM - aT * aO * aM - aR * aP * aN - aS * aQ * aL
        if aJ == 0:
            return None
        else:
            aH = 1 / aJ
            aK.m[0] = aH * (aP * aL - aM * aO)
            aK.m[1] = aH * (aM * aR - aS * aL)
            aK.m[2] = aH * (aS * aO - aP * aR)
            aK.m[3] = aH * (aN * aO - aQ * aL)
            aK.m[4] = aH * (aT * aL - aN * aR)
            aK.m[5] = aH * (aQ * aR - aT * aO)
            aK.m[6] = aH * (aQ * aM - aN * aP)
            aK.m[7] = aH * (aN * aS - aT * aM)
            aK.m[8] = aH * (aT * aP - aQ * aS)
            return aK

    def transform(self, aI, aK, aJ):
        if aJ == None:
            aJ = Array(0, 0)

        aH = self.m
        aJ[0] = aH[0] * aI + aH[3] * aK + aH[6]
        aJ[1] = aH[1] * aI + aH[4] * aK + aH[7]
        return aJ

    def translate(self, aI, aJ):
        aH = self.m
        aH[6] = aH[0] * aI + aH[3] * aJ + aH[6]
        aH[7] = aH[1] * aI + aH[4] * aJ + aH[7]
        aH[8] = aH[2] * aI + aH[5] * aJ + aH[8]

    def scale(self, aJ, aI):
        aH = self.m
        aH[0] *= aJ
        aH[1] *= aJ
        aH[2] *= aJ
        aH[3] *= aI
        aH[4] *= aI
        aH[5] *= aI

    def shear(self, aM, aL):
        aH = self.m
        aK = aH[0] + aH[3] * aL
        aJ = aH[1] + aH[4] * aL
        aI = aH[2] + aH[5] * aL
        aH[3] = aH[0] * aM + aH[3]
        aH[4] = aH[1] * aM + aH[4]
        aH[5] = aH[2] * aM + aH[5]
        aH[0] = aK
        aH[1] = aJ
        aH[2] = aI

    def rotate(self, aM):
        aH = self.m
        aN = math.cos(aM)
        aL = math.sin(aM)
        aK = aH[0] * aN + aH[3] * aL
        aJ = aH[1] * aN + aH[4] * aL
        aI = aH[2] * aN + aH[5] * aL
        aH[3] = -aH[0] * aL + aH[3] * aN
        aH[4] = -aH[1] * aL + aH[4] * aN
        aH[5] = -aH[2] * aL + aH[5] * aN
        aH[0] = aK
        aH[1] = aJ
        aH[2] = aI

    def concatenate(self, aL):
        aO = self.m
        aM = aL.m
        aS = aO[0] * aM[0] + aO[3] * aM[1] + aO[6] * aM[2]
        aR = aO[1] * aM[0] + aO[4] * aM[1] + aO[7] * aM[2]
        aQ = aO[2] * aM[0] + aO[5] * aM[1] + aO[8] * aM[2]
        aP = aO[0] * aM[3] + aO[3] * aM[4] + aO[6] * aM[5]
        aN = aO[1] * aM[3] + aO[4] * aM[4] + aO[7] * aM[5]
        aK = aO[2] * aM[3] + aO[5] * aM[4] + aO[8] * aM[5]
        aJ = aO[0] * aM[6] + aO[3] * aM[7] + aO[6] * aM[8]
        aI = aO[1] * aM[6] + aO[4] * aM[7] + aO[7] * aM[8]
        aH = aO[2] * aM[6] + aO[5] * aM[7] + aO[8] * aM[8]
        self.m[0] = aS
        self.m[1] = aR
        self.m[2] = aQ
        self.m[3] = aP
        self.m[4] = aN
        self.m[5] = aK
        self.m[6] = aJ
        self.m[7] = aI
        self.m[8] = aH


class ParamDefF:

    def __init__(self):
        self._TT = None
        self._LT = None
        self._FS = None
        self._wL = None

    def read(self, aH):
        self._TT = aH.readFloat32()
        self._LT = aH.readFloat32()
        self._FS = aH.readFloat32()
        self._wL = aH._nP()

    def getMinValue(self):
        return self._TT

    def getMaxValue(self):
        return self._LT

    def getDefaultValue(self):
        return self._FS

    def getParamID(self):
        return self._wL


class Live2D():
    _2s = "2.1.00_1"
    _Kr = 201001000
    _sP = True
    _so = True
    _cb = False
    _3T = True
    _Ts = True
    _fb = True
    _ts = True
    L2D_DEFORMER_EXTEND = True
    _Wb = False
    _yr = False
    _Zs = False
    L2D_NO_ERROR = 0
    _i7 = 1000
    _9s = 1001
    _es = 1100
    _r7 = 2000
    _07 = 2001
    _b7 = 2002
    _H7 = 4000
    L2D_COLOR_BLEND_MODE_MULT = 0
    L2D_COLOR_BLEND_MODE_ADD = 1
    L2D_COLOR_BLEND_MODE_INTERPOLATE = 2
    _6b = True
    _cT = 0
    clippingMaskBufferSize = 256
    glContext = {}
    frameBuffers = {}
    fTexture = {}
    IGNORE_CLIP = False
    IGNORE_EXPAND = False
    EXPAND_W = 2
    USE_ADJUST_TRANSLATION = True
    USE_CANVAS_TRANSFORM = True
    USE_CACHED_POLYGON_IMAGE = False
    DEBUG_DATA = type('', (), {
    })()
    PROFILE_DESKTOP = type('', (), {
        "PROFILE_NAME": "Desktop",
        "USE_ADJUST_TRANSLATION": False,
        "USE_CACHED_POLYGON_IMAGE": False,
        "EXPAND_W": 2
    })()

    @staticmethod
    def init():
        if Live2D._6b:
            print("Live2D %s" % Live2D._2s)

    @staticmethod
    def getVersionStr():
        return Live2D._2s

    @staticmethod
    def getVersionNo():
        return Live2D._Kr

    @staticmethod
    def _sT(aH):
        Live2D._cT = aH

    @staticmethod
    def getError():
        aH = Live2D._cT
        Live2D._cT = 0
        return aH

    @staticmethod
    def dispose():
        Live2D.glContext = []
        Live2D.frameBuffers = []
        Live2D.fTexture = []

    @staticmethod
    def setGL(aJ, aI=0):
        Live2D.glContext[aI] = aJ

    @staticmethod
    def getGL(aH):
        return Live2D.glContext[aH]

    @staticmethod
    def setClippingMaskBufferSize(aH):
        Live2D.clippingMaskBufferSize = aH

    @staticmethod
    def getClippingMaskBufferSize():
        return Live2D.clippingMaskBufferSize

    @staticmethod
    def deleteBuffer(aI):
        aH = Live2D.getGL(aI)
        aH.deleteFramebuffer(Live2D.frameBuffers[aI].framebuffer)
        del Live2D.frameBuffers[aI]
        del Live2D.glContext[aI]


class UtMotion():
    @staticmethod
    def _r2(aH):
        if aH < 0:
            return 0
        else:
            if aH > 1:
                return 1

        return 0.5 - 0.5 * math.cos(aH * UtMath.PI_F)


class LDError(Exception):
    _fr = -1

    def __init__(self, aH):
        self._ib = aH

    def __str__(self):
        return self._ib


class DDTexture(IDrawData2):
    _42 = 0
    _Os = 30
    _ms = 0
    _ns = 1
    _s_ = 2
    _gT = [None]

    def __init__(self):
        super().__init__()
        self.textureNo = -1
        self.pointCount = 0
        self.polygonCount = 0
        self._JP = None
        self._5P = None
        self.indexArray = None
        self.keyVertexPositions = None
        self.uvs = None
        self._6s = DDTexture._ms
        self.culling = True
        self.gl_cacheImage = None
        self.instanceNo = DDTexture._42
        DDTexture._42 += 1

    def __S(self, aH):
        self.textureNo = aH

    def getTextureNo(self):
        return self.textureNo

    def _ZL(self):
        return self.uvs

    def _H2(self):
        return self._JP

    def getNumPoints(self):
        return self.pointCount

    def getType(self):
        return IDrawData2._wb

    def _B2(self, aL, aH, aO):
        aM = aH
        aN = aM._hr if (aM._hr != None) else aM._Cr
        aK = DEF.VERTEX_TYPE

        _switch_53889 = aK
        if _switch_53889 == DEF.VERTEX_TYPE_OFFSET0_STEP2:
            raise LDError("_L _ro ")
        elif _switch_53889 == DEF.VERTEX_TYPE_OFFSET2_STEP5:
            for aJ in range(self.pointCount - 1, 0 - 1, -1):
                aI = aJ * DEF.VERTEX_STEP
                aN[aI + 4] = aO

    def _zP(self):
        self._GS = PivotManager()
        self._GS._zP()

    def read(self, aK):
        super().read(aK)
        self.textureNo = aK._6L()
        self.pointCount = aK._6L()
        self.polygonCount = aK._6L()
        aH = aK._nP()
        self.indexArray = Int16Array(self.polygonCount * 3)
        for aJ in range(self.polygonCount * 3 - 1, 0 - 1, -1):
            self.indexArray[aJ] = aH[aJ]

        self.keyVertexPositions = aK._nP()
        self.uvs = aK._nP()
        if aK.getFormatVersion() >= FileFormat2._s7:
            self._JP = aK._6L()
            if self._JP != 0:
                if (self._JP & 1) != 0:
                    aI = aK._6L()
                    if self._5P == None:
                        self._5P = {}

                    self._5P._Hb = int(aI)

                if (self._JP & DDTexture._Os) != 0:
                    self._6s = (self._JP & DDTexture._Os) >> 1
                else:
                    self._6s = DDTexture._ms

                if (self._JP & 32) != 0:
                    self.culling = False
        else:
            self._JP = 0

    def init(self, aL):
        aN = DDTextureContext(self)
        aI = self.pointCount * DEF.VERTEX_STEP
        aH = self.needTransform()
        if aN._Cr != None:
            aN._Cr = None

        aN._Cr = Float32Array(aI)
        if aN._hr != None:
            aN._hr = None

        aN._hr = Float32Array(aI) if aH else None
        aM = DEF.VERTEX_TYPE

        _switch_54443 = aM
        if _switch_54443 == DEF.VERTEX_TYPE_OFFSET0_STEP2:
            if DEF._Ls:
                for aJ in range(self.pointCount - 1, 0 - 1, -1):
                    aO = aJ << 1
                    self.uvs[aO + 1] = 1 - self.uvs[aO + 1]
        elif _switch_54443 == DEF.VERTEX_TYPE_OFFSET2_STEP5:
            for aJ in range(self.pointCount - 1, 0 - 1, -1):
                aO = aJ << 1
                aK = aJ * DEF.VERTEX_STEP
                aQ = self.uvs[aO]
                aP = self.uvs[aO + 1]
                aN._Cr[aK] = aQ
                aN._Cr[aK + 1] = aP
                aN._Cr[aK + 4] = 0
                if aH:
                    aN._hr[aK] = aQ
                    aN._hr[aK + 1] = aP
                    aN._hr[aK + 4] = 0

        return aN

    def setupInterpolate(self, aJ, aH):
        aK = aH
        if not ((self == aK._GT())):
            print("### assert!! ### ")

        if not self._GS._Ur(aJ):
            return

        super().setupInterpolate(aJ, aK)
        if aK._IS[0]:
            return

        aI = DDTexture._gT
        aI[0] = False
        aG._Vr(aJ, self._GS, aI, self.pointCount, self.keyVertexPositions, aK._Cr, DEF.VERTEX_OFFSET, DEF.VERTEX_STEP)

    def setupTransform(self, aK, aI):
        if not ((self == aI._GT())):
            print("### assert!! ### ")

        aL = False
        if aI._IS[0]:
            aL = True

        aM = aI
        if not aL:
            super().setupTransform(aK)
            if self.needTransform():
                aH = self.getTargetBaseDataID()
                if aM._8r == IDrawData2._ur:
                    aM._8r = aK.getBaseDataIndex(aH)

                if aM._8r < 0:
                    if Live2D._so:
                        print("_L _0P _G :: %s", aH)
                else:
                    aO = aK.getBaseData(aM._8r)
                    aJ = aK._q2(aM._8r)
                    if aO != None and not aJ._x2():
                        aO._nb(aK, aJ, aM._Cr, aM._hr, self.pointCount, DEF.VERTEX_OFFSET, DEF.VERTEX_STEP)
                        aM._AT = True
                    else:
                        aM._AT = False

                    aM.baseOpacity = aJ.getTotalOpacity()

    def draw(self, aN, aK, aI):
        if not ((self == aI._GT())):
            print("### assert!! ### ")

        if aI._IS[0]:
            return

        aL = aI
        aJ = self.textureNo
        if aJ < 0:
            aJ = 1

        aH = self.getOpacity(aK, aL) * aI._VS * aI.baseOpacity
        aM = aL._hr if (aL._hr is not None) else aL._Cr
        aN.setClipBufPre_clipContextForDraw(aI.clipBufPre_clipContext)
        aN._WP(self.culling)
        aN._Uo(aJ, 3 * self.polygonCount, self.indexArray, aM, self.uvs, aH, self._6s, aL)

    def dump(self):
        print("  _yi( %d ) , _d0( %d ) , _Yo( %d ) \n", self.textureNo, self.pointCount, self.polygonCount)
        print("  _Oi _di = { ")
        for aJ in range(0, len(self.indexArray), 1):
            print("%5d ,", self.indexArray[aJ])

        print("\n  _5i _30")
        for aJ in range(0, len(self.keyVertexPositions), 1):
            print("\n    _30[%d] = ", aJ)
            aH = self.keyVertexPositions[aJ]
            for aI in range(0, len(aH), 1):
                print("%6.2f, ", aH[aI])

        print("\n")

    def _72(self, aH):
        if self._5P == None:
            return None

        return self._5P[aH]

    def getIndexArray(self):
        return self.indexArray


class IDrawContext():

    def __init__(self, aH):
        self._e0 = None
        self._IP = None
        self._Us = None
        self._7s = None
        self._IS = [False]
        self._VS = 0
        self._AT = True
        self.baseOpacity = 1
        self.clipBufPre_clipContext = None
        self._e0 = aH

    def _u2(self):
        return self._IS[0]

    def _yo(self):
        return self._AT and not self._IS[0]

    def _GT(self):
        return self._e0


class DDTextureContext(IDrawContext):

    def __init__(self, aH):
        super().__init__(aH)
        self._8r = IDrawData2._ur
        self._Cr = None
        self._hr = None

    def getTransformedPoints(self):
        return self._hr if (self._hr != None) else self._Cr


class LDPoint():

    def __init__(self):
        self.x = None
        self.y = None


class Live2DModelOpenGL(ALive2DModel):

    def __init__(self, aH):
        super().__init__()
        self.drawParamWebGL = DrawParamWebGL(aH)
        self.drawParamWebGL.setGL(Live2D.getGL(aH))

    def setGL(self, aH):
        Live2D.setGL(aH)

    def setTransform(self, aH):
        self.drawParamWebGL.setTransform(aH)

    def update(self):
        self._5S.update()
        self._5S.preDraw(self.drawParamWebGL)

    def draw(self):
        self._5S.draw(self.drawParamWebGL)

    def _K2(self):
        self.drawParamWebGL._K2()

    def _Rs(self):
        return self.drawParamWebGL._Rs()

    def _Ds(self, aH):
        self.drawParamWebGL._Ds(aH)

    def getDrawParam(self):
        return self.drawParamWebGL

    def setMatrix(self, aH):
        self.drawParamWebGL.setMatrix(aH)

    def setPremultipliedAlpha(self, aH):
        self.drawParamWebGL.setPremultipliedAlpha(aH)

    def isPremultipliedAlpha(self):
        return self.drawParamWebGL.isPremultipliedAlpha()

    def setAnisotropy(self, aH):
        self.drawParamWebGL.setAnisotropy(aH)

    def getAnisotropy(self):
        return self.drawParamWebGL.getAnisotropy()

    @staticmethod
    def loadModel(aI, aK=0):
        aH = Live2DModelOpenGL(aK)
        ALive2DModel.loadModel_exe(aH, aI)
        return aH

    def setTexture(self, aI, aH):
        if self.drawParamWebGL is None:
            print("_Yi for QT _ki / _XS() is _6 _ui!!")

        self.drawParamWebGL.setTexture(aI, aH)


class MotionQueueManager:

    def __init__(self):
        self.motions = None
        self._eb = False
        self.motions = []

    def _tb(self):
        return self.motions

    def startMotion(self, aJ, aI):
        aM = None
        aL = None
        aH = len(self.motions)
        for aK in range(0, aH, 1):
            aL = self.motions[aK]
            if aL == None:
                continue

            aL._qS(aL._w0.getFadeOut())
            if self._eb:
                print("MotionQueueManager[size:%2d]->startMotion() / start _K _3 (m%d)\n", aH, aL._sr)

        if aJ == None:
            return -1

        aL = M()
        aL._w0 = aJ
        self.motions.append(aL)
        aN = aL._sr
        if self._eb:
            print("MotionQueueManager[size:%2d]->startMotion() / new _w0 (m%d)\n", aH, aN)

        return aN

    def updateParam(self, aJ):
        aI = False
        aK = 0
        size = len(self.motions)
        while aK < size:
            aL = self.motions[aK]
            if aL == None:
                self.motions.pop(aK)
                size -= 1
                aK -= 1
                continue

            aH = aL._w0
            if aH is None:
                self.motions.pop(aK)
                size -= 1
                aK -= 1
                continue

            aH.updateParam(aJ, aL)
            aI = True
            if aL.isFinished():
                if self._eb:
                    print("MotionQueueManager[size:%2d]->updateParam() / _T0 _w0 (m%d)\n",
                          len(self.motions) - 1, aL._sr)

                self.motions.pop(aK)
                size -= 1
                aK -= 1
            else:
                pass
            aK += 1

        return aI

    def isFinished(self, aK=None):
        if aK is not None:
            for aI in range(0, len(self.motions), 1):
                aJ = self.motions[aI]
                if aJ == None:
                    continue

                if aJ._sr == aK and not aJ.isFinished():
                    return False

            return True
        else:
            for aI in range(0, len(self.motions), 1):
                aJ = self.motions[aI]
                if aJ == None:
                    self.motions.splice(aI, 1)
                    aI -= 1
                    continue

                aH = aJ._w0
                if aH == None:
                    self.motions.splice(aI, 1)
                    aI -= 1
                    continue

                if not aJ.isFinished():
                    return False

            return True

    def stopAllMotions(self):
        for aI in range(0, len(self.motions), 1):
            aJ = self.motions[aI]
            if aJ == None:
                self.motions.splice(aI, 1)
                aI -= 1
                continue

            aH = aJ._w0
            if aH == None:
                self.motions.splice(aI, 1)
                aI -= 1
                continue

            if True:
                self.motions.splice(aI, 1)
                aI -= 1

    def _Zr(self, aH):
        self._eb = aH

    def _e(self):
        print("-- _R --\n")
        for aH in range(0, len(self.motions), 1):
            aI = self.motions[aH]
            aJ = aI._w0
            print("MotionQueueEnt[%d] :: %s\n", len(self.motions), str(aJ))


class M():

    def __init__(self):
        self._w0 = None
        self._AT = True
        self._9L = False
        self._z2 = -1
        self._bs = -1
        self._Do = -1
        self._sr = None
        self._sr = M._Gs
        M._Gs += 1

    def isFinished(self):
        return self._9L

    def _qS(self, aJ):
        aI = UtSystem.getUserTimeMSec()
        aH = aI + aJ
        if self._Do < 0 or aH < self._Do:
            self._Do = aH

    def _Bs(self):
        return self._sr

    _Gs = 0


class DrawParamWebGL(DrawParam):

    def __init__(self, aH):
        super().__init__()
        self.textures = []
        self.transform = None
        self.gl = None
        self.glno = aH
        self.firstDraw = True
        self.anisotropyExt = None
        self.maxAnisotropy = 0
        self._As = 32
        self._Gr = False
        self._NT = None
        self._vS = None
        self._no = None
        self.vertShader = None
        self.fragShader = None
        self.vertShaderOff = None
        self.fragShaderOff = None

    def getGL(self):
        return self.gl

    def setGL(self, aH):
        self.gl = aH

    def setTransform(self, aH):
        self.transform = aH

    def _ZT(self):
        aH = self.gl
        if self.firstDraw:
            self.initShader()
            self.firstDraw = False
            # self.anisotropyExt = aH.MAX_TEXTURE_MAX_ANISOTROPY
            if self.anisotropyExt:
                self.maxAnisotropy = aH.getParameter(self.anisotropyExt)

        aH.disable(aH.SCISSOR_TEST)
        aH.disable(aH.STENCIL_TEST)
        aH.disable(aH.DEPTH_TEST)
        aH.frontFace(aH.CW)
        aH.enable(aH.BLEND)
        aH.colorMask(1, 1, 1, 1)
        aH.bindBuffer(aH.ARRAY_BUFFER, 0)
        aH.bindBuffer(aH.ELEMENT_ARRAY_BUFFER, 0)

    def _Uo(self, aS, aT, aL, aU, aV, aN, aM, aO):
        if aN < 0.01 and self.clipBufPre_clipContextMask is None:
            return

        aH = Live2D.EXPAND_W if aN > 0.9 else 0
        a0 = self.gl
        if self.gl is None:
            raise LDError("gl is null")

        a1 = False
        aQ = 1
        aP = 1
        a3 = 1
        aZ = 1
        aW = self._C0 * aP * aN
        a2 = self._tT * a3 * aN
        a5 = self._WL * aZ * aN
        a7 = self._lT * aN
        aY = None
        a4 = None
        if self.clipBufPre_clipContextMask is not None:
            # print("=> mask")
            a0.frontFace(a0.CCW)
            a0.useProgram(self.shaderProgram)
            self._vS = ArrayBufferInfo(a0, self._vS, aU)
            self._no = ElementBufferInfo(a0, self._no, aL)
            a0.vertexAttribPointer(self.a_position_Loc, 2, a0.FLOAT, False, 0, None)
            a0.enableVertexAttribArray(self.a_position_Loc)
            self._NT = ArrayBufferInfo(a0, self._NT, aV)
            a0.activeTexture(a0.TEXTURE1)
            a0.bindTexture(a0.TEXTURE_2D, self.textures[aS])
            a0.uniform1i(self.s_texture0_Loc, 1)
            a0.vertexAttribPointer(self.a_texCoord_Loc, 2, a0.FLOAT, False, 0, None)
            a0.enableVertexAttribArray(self.a_texCoord_Loc)
            a0.uniformMatrix4fv(self.u_matrix_Loc, False, self.getClipBufPre_clipContextMask().matrixForMask)
            aY = self.getClipBufPre_clipContextMask().layoutChannelNo
            a4 = self.getChannelFlagAsColor(aY)
            a0.uniform4f(self.u_channelFlag, a4.r, a4.g, a4.b, a4.a)
            aI = self.getClipBufPre_clipContextMask().layoutBounds
            a0.uniform4f(self.u_baseColor_Loc, aI.x * 2.0 - 1.0, aI.y * 2.0 - 1.0, aI._EL() * 2.0 - 1.0,
                         aI._5T() * 2.0 - 1.0)
            a0.uniform1i(self.u_maskFlag_Loc, True)
        else:
            a1 = self.getClipBufPre_clipContextDraw() is not None
            if a1:
                # print("=> mask draw")
                a0.useProgram(self.shaderProgramOff)
                self._vS = ArrayBufferInfo(a0, self._vS, aU)
                self._no = ElementBufferInfo(a0, self._no, aL)
                a0.enableVertexAttribArray(self.a_position_Loc_Off)
                a0.vertexAttribPointer(self.a_position_Loc_Off, 2, a0.FLOAT, False, 0, None)
                self._NT = ArrayBufferInfo(a0, self._NT, aV)
                a0.activeTexture(a0.TEXTURE1)
                a0.bindTexture(a0.TEXTURE_2D, self.textures[aS])
                a0.uniform1i(self.s_texture0_Loc_Off, 1)
                a0.enableVertexAttribArray(self.a_texCoord_Loc_Off)
                a0.vertexAttribPointer(self.a_texCoord_Loc_Off, 2, a0.FLOAT, False, 0, None)
                a0.uniformMatrix4fv(self.u_clipMatrix_Loc_Off, False,
                                    self.getClipBufPre_clipContextDraw().matrixForDraw)
                a0.uniformMatrix4fv(self.u_matrix_Loc_Off, False, self.matrix4x4)
                a0.activeTexture(a0.TEXTURE2)
                a0.bindTexture(a0.TEXTURE_2D, Live2D.fTexture[self.glno])
                a0.uniform1i(self.s_texture1_Loc_Off, 2)
                aY = self.getClipBufPre_clipContextDraw().layoutChannelNo
                a4 = self.getChannelFlagAsColor(aY)
                a0.uniform4f(self.u_channelFlag_Loc_Off, a4.r, a4.g, a4.b, a4.a)
                a0.uniform4f(self.u_baseColor_Loc_Off, aW, a2, a5, a7)
            else:
                # print("=> draw")
                a0.useProgram(self.shaderProgram)
                self._vS = ArrayBufferInfo(a0, self._vS, aU)
                self._no = ElementBufferInfo(a0, self._no, aL)
                a0.enableVertexAttribArray(self.a_position_Loc)
                a0.vertexAttribPointer(self.a_position_Loc, 2, a0.FLOAT, False, 0, None)
                self._NT = ArrayBufferInfo(a0, self._NT, aV)
                a0.activeTexture(a0.TEXTURE1)
                a0.bindTexture(a0.TEXTURE_2D, self.textures[aS])
                a0.uniform1i(self.s_texture0_Loc, 1)
                a0.enableVertexAttribArray(self.a_texCoord_Loc)
                a0.vertexAttribPointer(self.a_texCoord_Loc, 2, a0.FLOAT, False, 0, None)
                a0.uniformMatrix4fv(self.u_matrix_Loc, False, self.matrix4x4)
                a0.uniform4f(self.u_baseColor_Loc, aW, a2, a5, a7)
                a0.uniform1i(self.u_maskFlag_Loc, False)
        if self.culling:
            self.gl.enable(a0.CULL_FACE)
        else:
            self.gl.disable(a0.CULL_FACE)

        self.gl.enable(a0.BLEND)
        a6 = None
        aX = None
        aR = None
        aK = None
        if self.clipBufPre_clipContextMask is not None:
            a6 = a0.ONE
            aX = a0.ONE_MINUS_SRC_ALPHA
            aR = a0.ONE
            aK = a0.ONE_MINUS_SRC_ALPHA
        else:
            _switch_61254 = aM
            if _switch_61254 == DDTexture._ms:
                a6 = a0.ONE
                aX = a0.ONE_MINUS_SRC_ALPHA
                aR = a0.ONE
                aK = a0.ONE_MINUS_SRC_ALPHA
            elif _switch_61254 == DDTexture._ns:
                a6 = a0.ONE
                aX = a0.ONE
                aR = a0.ZERO
                aK = a0.ONE
            elif _switch_61254 == DDTexture._s_:
                a6 = a0.DST_COLOR
                aX = a0.ONE_MINUS_SRC_ALPHA
                aR = a0.ZERO
                aK = a0.ONE

        a0.blendEquationSeparate(a0.FUNC_ADD, a0.FUNC_ADD)
        a0.blendFuncSeparate(a6, aX, aR, aK)
        if self.anisotropyExt:
            a0.texParameteri(a0.TEXTURE_2D, self.anisotropyExt.TEXTURE_MAX_ANISOTROPY_EXT, self.maxAnisotropy)

        aJ = len(aL)
        a0.drawElements(a0.TRIANGLES, aJ, a0.UNSIGNED_SHORT, None)
        a0.bindTexture(a0.TEXTURE_2D, 0)

    def _Rs(self):
        raise LDError("_Rs")

    def _Ds(self, aH):
        raise LDError("_Ds")

    def _K2(self):
        for aH in range(0, len(self.textures), 1):
            aI = self.textures[aH]
            if aI != 0:
                self.gl._K2(1, self.textures, aH)
                self.textures[aH] = None

    def setTexture(self, aH, aI):
        size = len(self.textures)
        if aH >= size:
            for i in range(size, aH + 1):
                self.textures.append(None)
        self.textures[aH] = aI

    def initShader(self):
        aH = self.gl
        self.loadShaders2()
        self.a_position_Loc = aH.getAttribLocation(self.shaderProgram, "a_position")
        self.a_texCoord_Loc = aH.getAttribLocation(self.shaderProgram, "a_texCoord")
        self.u_matrix_Loc = aH.getUniformLocation(self.shaderProgram, "u_mvpMatrix")
        self.s_texture0_Loc = aH.getUniformLocation(self.shaderProgram, "s_texture0")
        self.u_channelFlag = aH.getUniformLocation(self.shaderProgram, "u_channelFlag")
        self.u_baseColor_Loc = aH.getUniformLocation(self.shaderProgram, "u_baseColor")
        self.u_maskFlag_Loc = aH.getUniformLocation(self.shaderProgram, "u_maskFlag")
        self.a_position_Loc_Off = aH.getAttribLocation(self.shaderProgramOff, "a_position")
        self.a_texCoord_Loc_Off = aH.getAttribLocation(self.shaderProgramOff, "a_texCoord")
        self.u_matrix_Loc_Off = aH.getUniformLocation(self.shaderProgramOff, "u_mvpMatrix")
        self.u_clipMatrix_Loc_Off = aH.getUniformLocation(self.shaderProgramOff, "u_clipMatrix")
        self.s_texture0_Loc_Off = aH.getUniformLocation(self.shaderProgramOff, "s_texture0")
        self.s_texture1_Loc_Off = aH.getUniformLocation(self.shaderProgramOff, "s_texture1")
        self.u_channelFlag_Loc_Off = aH.getUniformLocation(self.shaderProgramOff, "u_channelFlag")
        self.u_baseColor_Loc_Off = aH.getUniformLocation(self.shaderProgramOff, "u_baseColor")

    def disposeShader(self):
        aH = self.gl
        if self.shaderProgram:
            aH.deleteProgram(self.shaderProgram)
            self.shaderProgram = None

        if self.shaderProgramOff:
            aH.deleteProgram(self.shaderProgramOff)
            self.shaderProgramOff = None

    def compileShader(self, aJ, aN):
        aM = self.gl
        aH = None
        aL = aN
        aK = aM.createShader(aJ)
        if aK == None:
            print("_L0 to create shader")
            return None

        aM.shaderSource(aK, aL)
        aM.compileShader(aK)
        aH = aM.getShaderParameter(aK, aM.COMPILE_STATUS)
        if not aH:
            aI = aM.getShaderInfoLog(aK)
            print(f"_L0 to compile shader : {aI}")
            aM.deleteShader(aK)
            return None

        return aK

    def loadShaders2(self):
        aN = self.gl
        self.shaderProgram = aN.createProgram()
        if not self.shaderProgram:
            return False

        self.shaderProgramOff = aN.createProgram()
        if not self.shaderProgramOff:
            return False

        aK = ("#version 330 core\n"
              "layout(location = 0) in vec2 a_position;"
              "layout(location = 1) in vec2 a_texCoord;"
              "out vec2 v_texCoord;"
              "out vec4 v_clipPos;"
              "uniform mat4 u_mvpMatrix;"
              "void main(){"
              "    gl_Position = u_mvpMatrix * vec4(a_position, 0.0, 1.0);"
              "    v_clipPos = gl_Position;"
              "    v_texCoord = a_texCoord;"
              "    v_texCoord.y = 1.0 - v_texCoord.y;}")
        aM = ("#version 330 core\n"
              "in vec2       v_texCoord;"
              "in vec4       v_clipPos;"
              "uniform sampler2D  s_texture0;"
              "uniform vec4       u_channelFlag;"
              "uniform vec4       u_baseColor;"
              "uniform bool       u_maskFlag;"
              "void main(){    vec4 smpColor;"
              "     if(u_maskFlag){"
              "        float isInside = "
              "            step(u_baseColor.x, v_clipPos.x/v_clipPos.w)"
              "          * step(u_baseColor.y, v_clipPos.y/v_clipPos.w)"
              "          * step(v_clipPos.x/v_clipPos.w, u_baseColor.z)"
              "          * step(v_clipPos.y/v_clipPos.w, u_baseColor.w);"
              "        smpColor = u_channelFlag * texture(s_texture0, v_texCoord).a * isInside;"
              "    }else{"
              "        smpColor = texture(s_texture0 , v_texCoord) * u_baseColor;"
              "        smpColor.rgb = smpColor.rgb * smpColor.a;"
              "    }"
              "    gl_FragColor = smpColor;}")
        aL = ("#version 330 core\n"
              "layout(location = 0) in vec2     a_position;"
              "layout(location = 1) in vec2     a_texCoord;"
              "out vec2       v_texCoord;"
              "out vec4       v_clipPos;"
              "uniform mat4       u_mvpMatrix;"
              "uniform mat4       u_clipMatrix;"
              "void main(){"
              "    vec4 pos = vec4(a_position, 0, 1.0);"
              "    gl_Position = u_mvpMatrix * pos;"
              "    v_clipPos = u_clipMatrix * pos;"
              "    v_texCoord = a_texCoord;"
              "    v_texCoord.y = 1.0 - v_texCoord.y;}")
        aJ = ("#version 330 core\n"
              "in vec2       v_texCoord;"
              "in vec4       v_clipPos;"
              "uniform sampler2D  s_texture0;"
              "uniform sampler2D  s_texture1;"
              "uniform vec4       u_channelFlag;"
              "uniform vec4       u_baseColor;"
              "void main(){"
              "    vec4 col_formask = texture(s_texture0, v_texCoord) * u_baseColor;"
              "    col_formask.rgb = col_formask.rgb * col_formask.a;"
              "    vec4 clipMask = texture(s_texture1, v_clipPos.xy / v_clipPos.w) * u_channelFlag;"
              "    float maskVal = clipMask.r + clipMask.g + clipMask.b + clipMask.a;"
              "    col_formask = col_formask * maskVal;"
              "    gl_FragColor = col_formask;}")
        self.vertShader = self.compileShader(aN.VERTEX_SHADER, aK)
        if not self.vertShader:
            print("Vertex shader compile _li!")
            return False

        self.vertShaderOff = self.compileShader(aN.VERTEX_SHADER, aL)
        if not self.vertShaderOff:
            print("OffVertex shader compile _li!")
            return False

        self.fragShader = self.compileShader(aN.FRAGMENT_SHADER, aM)
        if not self.fragShader:
            print("Fragment shader compile _li!")
            return False

        self.fragShaderOff = self.compileShader(aN.FRAGMENT_SHADER, aJ)
        if not self.fragShaderOff:
            print("OffFragment shader compile _li!")
            return False

        aN.attachShader(self.shaderProgram, self.vertShader)
        aN.attachShader(self.shaderProgram, self.fragShader)
        aN.attachShader(self.shaderProgramOff, self.vertShaderOff)
        aN.attachShader(self.shaderProgramOff, self.fragShaderOff)
        aN.linkProgram(self.shaderProgram)
        aN.linkProgram(self.shaderProgramOff)
        aH = aN.getProgramParameter(self.shaderProgram, aN.LINK_STATUS)
        aX = aN.getProgramParameter(self.shaderProgramOff, aN.LINK_STATUS)
        if not aH or not aX:
            if aH:
                aI = aN.getProgramInfoLog(self.shaderProgram)
            else:
                aI = aN.getProgramInfoLog(self.shaderProgramOff)
            print(f"failed to link program: {aI}")
            if self.vertShader:
                aN.deleteShader(self.vertShader)
                self.vertShader = 0

            if self.fragShader:
                aN.deleteShader(self.fragShader)
                self.fragShader = 0

            if self.shaderProgram:
                aN.deleteProgram(self.shaderProgram)
                self.shaderProgram = 0

            if self.vertShaderOff:
                aN.deleteShader(self.vertShaderOff)
                self.vertShaderOff = 0

            if self.fragShaderOff:
                aN.deleteShader(self.fragShaderOff)
                self.fragShaderOff = 0

            if self.shaderProgramOff:
                aN.deleteProgram(self.shaderProgramOff)
                self.shaderProgramOff = 0

            return False

        return True

    def createFramebuffer(self):
        aL = self.gl
        aK = Live2D.clippingMaskBufferSize
        aJ = aL.createFramebuffer()
        aL.bindFramebuffer(aL.FRAMEBUFFER, aJ)
        aH = aL.createRenderbuffer()
        aL.bindRenderbuffer(aL.RENDERBUFFER, aH)
        aL.renderbufferStorage(aL.RENDERBUFFER, aL.RGBA4, aK, aK)
        aL.framebufferRenderbuffer(aL.FRAMEBUFFER, aL.COLOR_ATTACHMENT0, aL.RENDERBUFFER, aH)
        aI = aL.createTexture()
        aL.bindTexture(aL.TEXTURE_2D, aI)
        aL.texImage2D(aL.TEXTURE_2D, 0, aL.RGBA, aK, aK, 0, aL.RGBA, aL.UNSIGNED_BYTE, None)
        aL.texParameteri(aL.TEXTURE_2D, aL.TEXTURE_MIN_FILTER, aL.LINEAR)
        aL.texParameteri(aL.TEXTURE_2D, aL.TEXTURE_MAG_FILTER, aL.LINEAR)
        aL.texParameteri(aL.TEXTURE_2D, aL.TEXTURE_WRAP_S, aL.CLAMP_TO_EDGE)
        aL.texParameteri(aL.TEXTURE_2D, aL.TEXTURE_WRAP_T, aL.CLAMP_TO_EDGE)
        aL.framebufferTexture2D(aL.FRAMEBUFFER, aL.COLOR_ATTACHMENT0, aL.TEXTURE_2D, aI, 0)
        aL.bindTexture(aL.TEXTURE_2D, 0)
        aL.bindRenderbuffer(aL.RENDERBUFFER, 0)
        aL.bindFramebuffer(aL.FRAMEBUFFER, 0)
        Live2D.fTexture[self.glno] = aI
        return type('', (), {
            "framebuffer": aJ,
            "renderbuffer": aH,
            "texture": Live2D.fTexture[self.glno]
        })()

    @staticmethod
    def _9r(aH):
        aI = Float32Array(aH)
        return aI

    @staticmethod
    def _vb(aH):
        aI = Int16Array(aH)
        return aI

    @staticmethod
    def _cr(aI, aH):
        if aI == None or aI._yL() < len(aH):
            aI = DrawParamWebGL._9r(len(aH) * 2)
            aI.put(aH)
            aI._oT(0)
        else:
            aI.clear()
            aI.put(aH)
            aI._oT(0)

        return aI

    @staticmethod
    def _mb(aI, aH):
        if aI == None or aI._yL() < len(aH):
            aI = DrawParamWebGL._vb(len(aH) * 2)
            aI.put(aH)
            aI._oT(0)
        else:
            aI.clear()
            aI.put(aH)
            aI._oT(0)

        return aI

    @staticmethod
    def _Hs():
        return DrawParamWebGL._Gr

    @staticmethod
    def _as(aH):
        DrawParamWebGL._Gr = aH


def ArrayBufferInfo(aJ, aH, aI):
    if aH is None:
        aH = aJ.createBuffer()

    aJ.bindBuffer(aJ.ARRAY_BUFFER, aH)
    aJ.bufferData(aJ.ARRAY_BUFFER, aI, aJ.DYNAMIC_DRAW)
    return aH


def ElementBufferInfo(aJ, aH, aI):
    if aH is None:
        aH = aJ.createBuffer()

    aJ.bindBuffer(aJ.ELEMENT_ARRAY_BUFFER, aH)
    aJ.bufferData(aJ.ELEMENT_ARRAY_BUFFER, aI, aJ.DYNAMIC_DRAW)
    return aH


class BReader:

    def __init__(self, aH: bytes):
        self._hL = 0
        self._v0 = 0
        self._S2 = 0
        self._Ko = []
        self._T = aH
        self._F = 0

    def readNumber(self):
        aK = self.readByte()
        if (aK & 128) == 0:
            return aK & 255

        aJ = self.readByte()
        if (aJ & 128) == 0:
            return ((aK & 127) << 7) | (aJ & 127)

        aI = self.readByte()
        if (aI & 128) == 0:
            return ((aK & 127) << 14) | ((aJ & 127) << 7) | (aI & 255)

        aH = self.readByte()
        if (aH & 128) == 0:
            return ((aK & 127) << 21) | ((aJ & 127) << 14) | ((aI & 127) << 7) | (aH & 255)

        raise LDError("_L _0P  _")

    def getFormatVersion(self):
        return self._S2

    def _gr(self, aH):
        self._S2 = aH

    def _3L(self):
        return self.readNumber()

    def _mP(self):
        self._zT()
        ret = self._F
        self._F += 8
        return struct.unpack('>d', self._T[ret:ret + 8])[0]

    def readFloat32(self):
        self._zT()
        ret = self._F
        self._F += 4
        return struct.unpack('>f', self._T[ret:ret + 4])[0]

    def _6L(self):
        self._zT()
        ret = self._F
        self._F += 4
        return struct.unpack('>i', self._T[ret:ret + 4])[0]

    def readByte(self):
        self._zT()
        ret = self._F
        self._F += 1
        return self._T[ret]

    def _9T(self):
        self._zT()
        ret = self._F
        self._F += 2
        return struct.unpack('>h', self._T[ret:ret + 2])[0]

    def _2T(self):
        self._zT()
        self._F += 8
        raise LDError("_L _q read long")

    def _po(self):
        self._zT()
        ret = self._F
        self._F += 1
        return self._T[ret] != 0

    def _bT(self):
        self._zT()
        aH = self._3L()
        result = self._T[self._F:self._F + aH].decode("utf-8")
        self._F += aH
        return result

    def _cS(self):
        self._zT()
        aI = self._3L()
        aH = Int32Array(aI)
        for aJ in range(0, aI, 1):
            aH[aJ] = self._6L()

        return aH

    def _Tb(self):
        self._zT()
        aI = self._3L()
        aH = Float32Array(aI)
        for aJ in range(0, aI, 1):
            aH[aJ] = self.readFloat32()
            # self._F += 4

        return aH

    def _5b(self):
        self._zT()
        aI = self._3L()
        aH = Float64Array(aI)
        for aJ in range(0, aI, 1):
            aH[aJ] = self._mP()
            self._F += 8

        return aH

    def _nP(self):
        return self._Jb(-1)

    def _Jb(self, aJ):
        self._zT()
        if aJ < 0:
            aJ = self._3L()

        if aJ == FileFormat2._7P:
            aH = self._6L()
            if 0 <= aH and aH < len(self._Ko):
                return self._Ko[aH]
            else:
                raise LDError("_sL _4i @_m0")
        else:
            aI = self._4b(aJ)
            self._Ko.append(aI)
            return aI

    def _4b(self, aN):
        if aN == 0:
            return None
        elif aN == 50:
            aK = self._bT()
            aI = DrawDataID.getID(aK)
            return aI
        elif aN == 51:
            aK = self._bT()
            aI = BaseDataID.getID(aK)
            return aI
        elif aN == 134:
            aK = self._bT()
            aI = PartsDataID.getID(aK)
            return aI
        elif aN == 60:
            aK = self._bT()
            aI = ParamID.getID(aK)
            return aI
        elif aN >= 48:
            aL = FileFormat2._9o(aN)
            if aL is not None:
                aL.read(self)
                return aL
            else:
                return None
        elif aN == 1:
            return self._bT()
        elif aN == 10:
            aM = self._6L()
            return LDColor(aM, True)
        elif aN == 11:
            return LDRectF(self._mP(), self._mP(), self._mP(), self._mP())
        elif aN == 12:
            return LDRectF(self.readFloat32(), self.readFloat32(), self.readFloat32(), self.readFloat32())
        elif aN == 13:
            return LDPointF(self._mP(), self._mP())
        elif aN == 14:
            return LDPointF(self.readFloat32(), self.readFloat32())
        elif aN == 15:
            aH = self._3L()
            aI = Array(aH)
            for aJ in range(0, aH, 1):
                aI[aJ] = self._nP()
            return aI
        elif aN == 17:
            aI = LDMatrix2x3(self._mP(), self._mP(), self._mP(), self._mP(), self._mP(), self._mP())
            return aI
        elif aN == 21:
            return LDRect(self._6L(), self._6L(), self._6L(), self._6L())
        elif aN == 22:
            return LDPoint(self._6L(), self._6L())
        elif aN == 23:
            raise Exception("type not implemented")
        elif aN == 16 or aN == 25:
            return self._cS()
        elif aN == 26:
            return self._5b()
        elif aN == 27:
            return self._Tb()
        raise LDError("type error %d" % aN)

    def _8L(self):
        if self._hL == 0:
            self._v0 = self.readByte()
        else:
            if self._hL == 8:
                self._v0 = self.readByte()
                self._hL = 0

        ret = ((self._v0 >> (7 - self._hL)) & 1) == 1
        self._hL += 1
        return ret

    def _zT(self):
        if self._hL != 0:
            self._hL = 0


class ai:

    def __init__(self):
        pass

    def _wP(self, aM, aI, aK):
        for aL in range(0, aK, 1):
            for aH in range(0, aI, 1):
                aJ = 2 * (aH + aL * aI)
                print("(% 7.3f , % 7.3f) , ", aM[aJ], aM[aJ + 1])

            print("\n")

        print("\n")


class UtMath():
    _2S = math.pi / 180
    _bS = (math.pi / 180)
    _wS = 180 / math.pi
    _NS = (180 / math.pi)
    PI_F = math.pi
    _kT = [0, 0.012368, 0.024734, 0.037097, 0.049454, 0.061803, 0.074143, 0.086471, 0.098786, 0.111087, 0.12337,
           0.135634, 0.147877, 0.160098, 0.172295, 0.184465, 0.196606, 0.208718, 0.220798, 0.232844, 0.244854, 0.256827,
           0.268761, 0.280654, 0.292503, 0.304308, 0.316066, 0.327776, 0.339436, 0.351044, 0.362598, 0.374097, 0.385538,
           0.396921, 0.408243, 0.419502, 0.430697, 0.441826, 0.452888, 0.463881, 0.474802, 0.485651, 0.496425, 0.507124,
           0.517745, 0.528287, 0.538748, 0.549126, 0.559421, 0.56963, 0.579752, 0.589785, 0.599728, 0.609579, 0.619337,
           0.629, 0.638567, 0.648036, 0.657406, 0.666676, 0.675843, 0.684908, 0.693867, 0.70272, 0.711466, 0.720103,
           0.72863, 0.737045, 0.745348, 0.753536, 0.76161, 0.769566, 0.777405, 0.785125, 0.792725, 0.800204, 0.807561,
           0.814793, 0.821901, 0.828884, 0.835739, 0.842467, 0.849066, 0.855535, 0.861873, 0.868079, 0.874153, 0.880093,
           0.885898, 0.891567, 0.897101, 0.902497, 0.907754, 0.912873, 0.917853, 0.922692, 0.92739, 0.931946, 0.936359,
           0.940629, 0.944755, 0.948737, 0.952574, 0.956265, 0.959809, 0.963207, 0.966457, 0.96956, 0.972514, 0.97532,
           0.977976, 0.980482, 0.982839, 0.985045, 0.987101, 0.989006, 0.990759, 0.992361, 0.993811, 0.995109, 0.996254,
           0.997248, 0.998088, 0.998776, 0.999312, 0.999694, 0.999924, 1]

    @staticmethod
    def _92(aK, aI):
        aH = math.atan2(aK[1], aK[0])
        aJ = math.atan2(aI[1], aI[0])
        return UtMath._tS(aH, aJ)

    @staticmethod
    def _tS(aI, aH):
        aJ = aI - aH
        while aJ < -math.pi:
            aJ += 2 * math.pi

        while aJ > math.pi:
            aJ -= 2 * math.pi

        return aJ

    @staticmethod
    def _9(aH):
        return math.sin(aH)

    @staticmethod
    def fcos(aH):
        return math.cos(aH)


def Float32Array(size: int):
    if not isinstance(size, int):
        raise Exception("invalid param")

    return [0.0] * size


def Float64Array(size: int):
    return Float32Array(size)


def Int8Array(size: int):
    return Array(size)


def Int16Array(size: int):
    return Array(size)


def Int32Array(size: int = None):
    if size is None:
        return []
    if not isinstance(size, int):
        raise Exception("invalid param")

    return [0] * size


def Array(size: int = None):
    if size is None:
        return []
    if not isinstance(size, int):
        raise Exception("invalid param")

    return [None] * size


class ID:

    def __init__(self, aH):
        self.id = aH

    def __str__(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, ID):
            return id(other) == id(self) or other.id == self.id
        elif isinstance(other, str):
            return other == self.id
        return False

    @staticmethod
    def _L7():
        ParamID._27()
        BaseDataID._27()
        DrawDataID._27()
        PartsDataID._27()


class PartsDataID(ID):
    _tP = {}

    def __init__(self, aH):
        super().__init__(aH)

    @staticmethod
    def _27():
        PartsDataID._tP.clear()

    @staticmethod
    def getID(aH):
        aI = PartsDataID._tP.get(aH, None)
        if aI is None:
            aI = PartsDataID(aH)
            PartsDataID._tP[aH] = aI

        return aI


class ParamID(ID):
    _tP = {}

    def __init__(self, aH):
        super().__init__(aH)

    @staticmethod
    def _27():
        ParamID._tP.clear()

    @staticmethod
    def getID(aH):
        aI = ParamID._tP.get(aH, None)
        if aI is None:
            aI = ParamID(aH)
            ParamID._tP[aH] = aI

        return aI


class DrawDataID(ID):
    _tP = {}

    def __init__(self, aH):
        super().__init__(aH)

    @staticmethod
    def _27():
        DrawDataID._tP.clear()

    @staticmethod
    def getID(aH):
        aI = DrawDataID._tP.get(aH, None)
        if aI is None:
            aI = DrawDataID(aH)
            DrawDataID._tP[aH] = aI

        return aI


class BaseDataID(ID):
    _eT = None
    _tP = {}

    def __init__(self, aH):
        super().__init__(aH)

    @staticmethod
    def _2o():
        if BaseDataID._eT is None:
            BaseDataID._eT = BaseDataID.getID("DST_BASE")

        return BaseDataID._eT

    @staticmethod
    def _27():
        BaseDataID._tP.clear()
        BaseDataID._eT = None

    @staticmethod
    def getID(aH):
        aI = BaseDataID._tP.get(aH, None)
        if aI is None:
            aI = BaseDataID(aH)
            BaseDataID._tP[aH] = aI

        return aI

# window.UtSystem = UtSystem
# window.UtDebug = UtDebug
# window.LDTransform = LDTransform
# window.Live2D = Live2D
# window.Live2DModelWebGL = Live2DModelWebGL
# window.Live2DModelJS = Live2DModelJS
# window.Live2DMotion = Live2DMotion
# window.MotionQueueManager = MotionQueueManager
# window.PhysicsHair = PhysicsHair
# window.AMotion = AMotion
# window.PartsDataID = PartsDataID
# window.DrawDataID = DrawDataID
# window.BaseDataID = BaseDataID
# window.ParamID = ParamID
# Live2D.init()
