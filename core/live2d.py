class Live2D:
    versionString = "2.1.00_1"
    versionNo = 201001000
    L2D_VERBOSE = True
    L2D_DEFORMER_EXTEND = True
    L2D_OUTSIDE_PARAM_AVAILABLE = False
    L2D_NO_ERROR = 0
    L2D_ERROR_LIVE2D_INIT_FAILED = 1000
    L2D_ERROR_FILE_LOAD_FAILED = 1001
    L2D_ERROR_MEMORY_ERROR = 1100
    L2D_ERROR_MODEL_DATA_VERSION_MISMATCH = 2000
    L2D_ERROR_MODEL_DATA_EOF_ERROR = 2001
    L2D_COLOR_BLEND_MODE_MULT = 0
    L2D_COLOR_BLEND_MODE_ADD = 1
    L2D_COLOR_BLEND_MODE_INTERPOLATE = 2
    __firstInit = True
    clippingMaskBufferSize = 256
    glContext = {}
    frameBuffers = {}
    frameTexture = {}
    IGNORE_CLIP = False
    IGNORE_EXPAND = False

    @staticmethod
    def init():
        if Live2D.__firstInit:
            print("Live2D %s" % Live2D.versionString)
            Live2D.__firstInit = False

    @staticmethod
    def getVersionStr():
        return Live2D.versionString

    @staticmethod
    def getVersionNo():
        return Live2D.versionNo

    @staticmethod
    def sT_(aH):
        Live2D.cT_ = aH

    @staticmethod
    def dispose():
        Live2D.glContext = []
        Live2D.frameBuffers = []
        Live2D.frameTexture = []

    @staticmethod
    def setGL(aJ, aI=0):
        Live2D.glContext[aI] = aJ

    @staticmethod
    def getGL(aH):
        return Live2D.glContext[aH]

    @staticmethod
    def setClippingMaskBufferSize(aH):
        Live2D.__clippingMaskBufferSize = aH

    @staticmethod
    def getClippingMaskBufferSize():
        return Live2D.__clippingMaskBufferSize

    @staticmethod
    def deleteBuffer(aI):
        aH = Live2D.getGL(aI)
        aH.deleteFramebuffer(Live2D.frameBuffers[aI].framebuffer)
        del Live2D.frameBuffers[aI]
        del Live2D.glContext[aI]
