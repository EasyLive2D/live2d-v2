from abc import ABC, abstractmethod

from core import DEF
from core.draw import MeshContext, IDrawData, Mesh
from core.id import ParamID, PartsDataID, DrawDataID
from core.io.binary_reader import BinaryReader
from core.model import ModelImpl
from core.model_context import ModelContext


class ALive2DModel(ABC):
    _0s = 1
    _4s = 2
    _42 = 0

    def __init__(self):
        self.modelImpl = None
        self.modelContext = None
        self.NP_ = 0
        ALive2DModel._42 += 1
        self.modelContext = ModelContext(self)

    def setModelImpl(self, aH):
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
        aH = self.modelContext.getParamIndex(ParamID.getID(aH))

        return self.modelContext.getParamFloat(aH)

    def setParamFloat(self, aH, aJ, aI=1):
        aH = self.modelContext.getParamIndex(ParamID.getID(aH))
        aJ = 0 if aJ is None else aJ
        self.modelContext.setParamFloat(aH, self.modelContext.getParamFloat(aH) * (1 - aI) + aJ * aI)

    def addToParamFloat(self, aH, aJ, aI=1):
        aH = self.modelContext.getParamIndex(ParamID.getID(aH))

        self.modelContext.setParamFloat(aH, self.modelContext.getParamFloat(aH) + aJ * aI)

    def multParamFloat(self, aH, aJ, aI=1):
        aH = self.modelContext.getParamIndex(ParamID.getID(aH))

        self.modelContext.setParamFloat(aH, self.modelContext.getParamFloat(aH) * (1 + (aJ - 1) * aI))

    def getParamIndex(self, aH):
        return self.modelContext.getParamIndex(ParamID.getID(aH))

    def loadParam(self):
        self.modelContext.loadParam()

    def saveParam(self):
        self.modelContext.saveParam()

    def init(self):
        self.modelContext.init()

    def update(self):
        self.modelContext.update()

    @abstractmethod
    def draw(self):
        pass

    def getModelContext(self):
        return self.modelContext

    def setPartsOpacity(self, aI, aH):
        if not isinstance(aI, int):
            aI = self.modelContext.getPartsDataIndex(PartsDataID.getID(aI))

        self.modelContext.setPartsOpacity(aI, aH)

    def getPartsDataIndex(self, aH):
        if not (isinstance(aH, PartsDataID)):
            aH = PartsDataID.getID(aH)

        return self.modelContext.getPartsDataIndex(aH)

    def getPartsOpacity(self, aH):
        if not isinstance(aH, int):
            aH = self.modelContext.getPartsDataIndex(PartsDataID.getID(aH))

        if aH < 0:
            return 0

        return self.modelContext.getPartsOpacity(aH)

    @abstractmethod
    def getDrawParam(self):
        pass

    def getDrawDataIndex(self, aH):
        return self.modelContext.getDrawDataIndex(DrawDataID.getID(aH))

    def getDrawData(self, aH):
        return self.modelContext.getDrawData(aH)

    def getTransformedPoints(self, aH):
        aI = self.modelContext.getDrawContext(aH)
        if isinstance(aI, MeshContext):
            return aI.getTransformedPoints()

        return None

    def getIndexArray(self, aI):
        if aI < 0 or aI >= len(self.modelContext.drawDataList):
            return None

        aH = self.modelContext.drawDataList[aI]
        if aH is not None and aH.getType() == IDrawData.TYPE_MESH:
            if isinstance(aH, Mesh):
                return aH.getIndexArray()

        return None

    @staticmethod
    def loadModel_exe(model, buf: bytes):

        if not (isinstance(buf, bytes)):
            raise RuntimeError("param error")

        br = BinaryReader(buf)
        aM = br.readByte()
        aK = br.readByte()
        aJ = br.readByte()
        if aM == 109 and aK == 111 and aJ == 99:
            version = br.readByte()
        else:
            raise RuntimeError("Invalid MOC file.")

        br.setFormatVersion(version)
        if version > DEF.LIVE2D_FORMAT_VERSION_AVAILABLE:
            model.NP_ |= ALive2DModel._4s
            aR = DEF.LIVE2D_FORMAT_VERSION_AVAILABLE
            aI = "Unsupported version %d\n" % version
            raise RuntimeError(aI)

        aL = br.readObject()
        if version >= DEF.LIVE2D_FORMAT_VERSION_V2_8_TEX_OPTION:
            aH = br.readUShort()
            aT = br.readUShort()
            if aH != -30584 or aT != -30584:
                model.NP_ |= ALive2DModel._0s
                raise RuntimeError("_gi _C li_ , _0 _6 Ui_.")

        model.setModelImpl(aL)
        modelContext = model.getModelContext()
        modelContext.setDrawParam(model.getDrawParam())
        modelContext.init()
