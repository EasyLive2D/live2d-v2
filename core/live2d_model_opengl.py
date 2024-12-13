from core.alive2d_model import ALive2DModel
from core.graphics import DrawParamOpenGL
from core.live2d import Live2D


class Live2DModelOpenGL(ALive2DModel):

    def __init__(self, aH):
        super().__init__()
        self.drawParamWebGL = DrawParamOpenGL(aH)
        self.drawParamWebGL.setGL(Live2D.getGL(aH))

    def setGL(self, aH):
        Live2D.setGL(aH)

    def setTransform(self, aH):
        self.drawParamWebGL.setTransform(aH)

    def update(self):
        self.modelContext.update()
        self.modelContext.preDraw(self.drawParamWebGL)

    def draw(self):
        self.modelContext.draw(self.drawParamWebGL)

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
            print("_Yi for QT ki_ / XS_() is _6 ui_!!")

        self.drawParamWebGL.setTexture(aI, aH)
