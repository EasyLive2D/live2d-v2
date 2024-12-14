from framework.matrix.l2d_matrix44 import L2DMatrix44
from framework.matrix.l2d_view_matrix import L2DViewMatrix
from main import LAppDefine


class MatrixManager:

    def __init__(self):
        self.__projection = L2DMatrix44()
        self.__viewMatrix = L2DViewMatrix()
        self.__viewMatrix.setMinScale(0.1)
        self.__screenToScene = L2DMatrix44()
        self.__tmpMatrix = L2DViewMatrix()

    def onResize(self, width: int, height: int):
        ratio = width / height
        left = LAppDefine.VIEW_LOGICAL_LEFT
        right = LAppDefine.VIEW_LOGICAL_RIGHT
        bottom = -ratio
        top = ratio
        self.__viewMatrix.setScreenRect(left, right, bottom, top)
        self.__viewMatrix.setMaxScreenRect(
            LAppDefine.VIEW_LOGICAL_MAX_LEFT,
            LAppDefine.VIEW_LOGICAL_MAX_RIGHT,
            LAppDefine.VIEW_LOGICAL_MAX_BOTTOM,
            LAppDefine.VIEW_LOGICAL_MAX_TOP
        )

        self.__projection.identity()
        self.__projection.multScale(1.0, width / height)

        self.__screenToScene.identity()
        self.__screenToScene.multTranslate(-width / 2.0, -height / 2.0)
        self.__screenToScene.multScale(2 / width, -2 / width)

    def screenToScene(self, scr_x: float, scr_y: float) -> tuple[float, float]:
        return self.__screenToScene.transformX(scr_x), self.__screenToScene.transformY(scr_y)

    def invertTransform(self, sx: float, sy: float):
        return self.__viewMatrix.invertTransformX(sx), self.__viewMatrix.invertTransformY(sy)

    def setScale(self, cx, cy, scale: float):
        self.__viewMatrix.adjustScale(cx, cy, scale)

    def getMvp(self, modelMatrix) -> list:
        self.__tmpMatrix.identity()
        self.__tmpMatrix.mul(self.__tmpMatrix.getArray(), self.__projection.getArray(), self.__tmpMatrix.getArray())
        self.__tmpMatrix.mul(self.__tmpMatrix.getArray(), self.__viewMatrix.getArray(), self.__tmpMatrix.getArray())
        self.__tmpMatrix.mul(self.__tmpMatrix.getArray(), modelMatrix.getArray(), self.__tmpMatrix.getArray())
        return self.__tmpMatrix.getArray()
