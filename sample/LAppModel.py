import math
from random import random, choice

import LAppDefine
from MatrixStack import MatrixStack
from core.live2d import UtSystem
from ModelSettingJson import ModelSettingJson
from framework.Live2DFramework import L2DBaseModel, L2DEyeBlink, Live2DFramework


class LAppModel(L2DBaseModel):

    def __init__(self):
        super().__init__()
        self.modelHomeDir = ""
        self.modelSetting = None
        self.tmpMatrix = []

    def load(self, modelSettingPath: str):
        self.setUpdating(True)
        self.setInitialized(False)
        self.modelHomeDir = modelSettingPath[0: modelSettingPath.rfind("/") + 1]
        self.modelSetting = ModelSettingJson()

        self.modelSetting.loadModelSetting(modelSettingPath)
        
        path = self.modelHomeDir + self.modelSetting.getModelFile()

        self.loadModelData(path)

        for i in range(self.modelSetting.getTextureNum()):
            texPaths = self.modelHomeDir + self.modelSetting.getTextureFile(i)
            self.loadTexture(i, texPaths)

        if self.modelSetting.getExpressionNum() > 0:
            self.expressions = {}
            for j in range(self.modelSetting.getExpressionNum()):
                expName = self.modelSetting.getExpressionName(j)
                expFilePath = self.modelHomeDir + self.modelSetting.getExpressionFile(j)
                self.loadExpression(expName, expFilePath)
        else:
            self.expressionManager = None
            self.expressions = {}

        if self.eyeBlink is None:
            self.eyeBlink = L2DEyeBlink()

        if self.modelSetting.getPhysicsFile() is not None:
            self.loadPhysics(self.modelHomeDir + self.modelSetting.getPhysicsFile())
        else:
            self.physics = None

        if self.modelSetting.getPoseFile() is not None:
            pose = self.loadPose(self.modelHomeDir + self.modelSetting.getPoseFile())
            pose.updateParam(self.live2DModel)

        if self.modelSetting.getLayout() is not None:
            layout = self.modelSetting.getLayout()
            if layout.get("width", None) is not None:
                self.modelMatrix.setWidth(layout["width"])
            if layout.get("height", None) is not None:
                self.modelMatrix.setHeight(layout["height"])
            if layout.get("x", None) is not None:
                self.modelMatrix.setX(layout["x"])
            if layout.get("y", None) is not None:
                self.modelMatrix.setY(layout["y"])
            if layout.get("center_x", None) is not None:
                self.modelMatrix.centerX(layout["center_x"])
            if layout.get("center_y", None) is not None:
                self.modelMatrix.centerY(layout["center_y"])
            if layout.get("top", None) is not None:
                self.modelMatrix.top(layout["top"])
            if layout.get("bottom", None) is not None:
                self.modelMatrix.bottom(layout["bottom"])
            if layout.get("left", None) is not None:
                self.modelMatrix.left(layout["left"])
            if layout.get("right", None) is not None:
                self.modelMatrix.right(layout["right"])

        for j in range(self.modelSetting.getInitParamNum()):
            self.live2DModel.setParamFloat(self.modelSetting.getInitParamID(j),
                                              self.modelSetting.getInitParamValue(j))

        for j in range(self.modelSetting.getInitPartsVisibleNum()):
            self.live2DModel.setPartsOpacity(self.modelSetting.getInitPartsVisibleID(j),
                                                self.modelSetting.getInitPartsVisibleValue(j))

        self.live2DModel.saveParam()
        self.preloadMotionGroup(LAppDefine.MOTION_GROUP_IDLE)
        self.mainMotionManager.stopAllMotions()
        self.setUpdating(False)
        self.setInitialized(True)
        self.live2DModel.setPremultipliedAlpha(False)

    def release(self, gl):
        pm = Live2DFramework.getPlatformManager()
        gl.deleteTexture(pm.texture)

    def preloadMotionGroup(self, name):
        for i in range(self.modelSetting.getMotionNum(name)):
            file = self.modelSetting.getMotionFile(name, i)
            motion = self.loadMotion(file, self.modelHomeDir + file)

            motion.setFadeIn(self.modelSetting.getMotionFadeIn(name, i))
            motion.setFadeOut(self.modelSetting.getMotionFadeOut(name, i))

    def update(self):
        timeMSec = UtSystem.getUserTimeMSec() - self.startTimeMSec
        timeSec = timeMSec / 1000.0
        t = timeSec * 2 * math.pi
        if self.mainMotionManager.isFinished():
            self.startRandomMotion()
            pass

        self.live2DModel.loadParam()
        update = self.mainMotionManager.updateParam(self.live2DModel)
        if not update:
            if self.eyeBlink is not None:
                self.eyeBlink.updateParam(self.live2DModel)

        self.live2DModel.saveParam()
        if self.expressionManager is not None and self.expressions is not None and not self.expressionManager.isFinished():
            self.expressionManager.updateParam(self.live2DModel)

        self.live2DModel.addToParamFloat("PARAM_ANGLE_X", self.dragX * 30, 1)
        self.live2DModel.addToParamFloat("PARAM_ANGLE_Y", self.dragY * 30, 1)
        self.live2DModel.addToParamFloat("PARAM_ANGLE_Z", (self.dragX * self.dragY) * -30, 1)
        self.live2DModel.addToParamFloat("PARAM_BODY_ANGLE_X", self.dragX * 10, 1)
        self.live2DModel.addToParamFloat("PARAM_EYE_BALL_X", self.dragX, 1)
        self.live2DModel.addToParamFloat("PARAM_EYE_BALL_Y", self.dragY, 1)
        self.live2DModel.addToParamFloat("PARAM_ANGLE_X", float((15 * math.sin(t / 6.5345))), 0.5)
        self.live2DModel.addToParamFloat("PARAM_ANGLE_Y", float((8 * math.sin(t / 3.5345))), 0.5)
        self.live2DModel.addToParamFloat("PARAM_ANGLE_Z", float((10 * math.sin(t / 5.5345))), 0.5)
        self.live2DModel.addToParamFloat("PARAM_BODY_ANGLE_X", float((4 * math.sin(t / 15.5345))), 0.5)
        self.live2DModel.setParamFloat("PARAM_BREATH", float((0.5 + 0.5 * math.sin(t / 3.2345))), 1)
        if self.physics is not None:
            self.physics.updateParam(self.live2DModel)

        if self.lipSync is None:
            self.live2DModel.setParamFloat("PARAM_MOUTH_OPEN_Y", self.lipSyncValue)

        if self.pose is not None:
            self.pose.updateParam(self.live2DModel)

        self.live2DModel.update()

    def setRandomExpression(self):
        tmp = []
        for name in self.expressions:
            tmp.append(name)

        no = int(random() * len(tmp))
        self.setExpression(tmp[no])

    def startRandomMotion(self, name = None, priority = LAppDefine.PRIORITY_IDLE):
        if name is None:
            names = self.modelSetting.getMotionNames()
            if names is not None:
                name = choice(names)
            else:
                name = LAppDefine.MOTION_GROUP_IDLE
        max = self.modelSetting.getMotionNum(name)
        no = int(random() * max)
        self.startMotion(name, no, priority)

    def startMotion(self, name, no, priority):
        motionName = self.modelSetting.getMotionFile(name, no)
        if motionName is None or motionName == "":
            return

        if priority == LAppDefine.PRIORITY_FORCE:
            self.mainMotionManager.setReservePriority(priority)
        elif not self.mainMotionManager.reserveMotion(priority):
            if LAppDefine.DEBUG_LOG:
                print("Motion is running.")
                return

        if self.motions.get(name) is None:
            mtn = self.loadMotion(None, self.modelHomeDir + motionName)
            self.setFadeInFadeOut(name, no, priority, mtn)
        else:
            motion = self.motions[name]
            self.setFadeInFadeOut(name, no, priority, motion)

    def setFadeInFadeOut(self, name, no, priority, motion):
        motionName = self.modelSetting.getMotionFile(name, no)
        motion.setFadeIn(self.modelSetting.getMotionFadeIn(name, no))
        motion.setFadeOut(self.modelSetting.getMotionFadeOut(name, no))
        if LAppDefine.DEBUG_LOG:
            print("Start motion : " + motionName)
        if self.modelSetting.getMotionSound(name, no) is None:
            self.mainMotionManager.startMotionPrio(motion, priority)
        else:
            soundName = self.modelSetting.getMotionSound(name, no)
            # snd = document.createElement("audio")
            # snd.src = self.modelHomeDir + soundName
            if LAppDefine.DEBUG_LOG:
                print("Start sound : " + soundName)
            # snd.play()
            self.mainMotionManager.startMotionPrio(motion, priority)

    def setExpression(self, name):
        motion = self.expressions[name]
        if LAppDefine.DEBUG_LOG:
            print("Expression : " + name)
        self.expressionManager.startMotion(motion, False)

    def draw(self):
        MatrixStack.push()
        MatrixStack.multMatrix(self.modelMatrix.getArray())
        self.tmpMatrix = MatrixStack.getMatrix()
        self.live2DModel.setMatrix(self.tmpMatrix)
        self.live2DModel.draw()
        MatrixStack.pop()

    def hitTest(self, id, testX, testY):
        size = self.modelSetting.getHitAreaNum()
        for i in range(size):
            if id == self.modelSetting.getHitAreaName(i):
                drawID = self.modelSetting.getHitAreaID(i)
                return self.hitTestSimple(drawID, testX, testY)

        return False
