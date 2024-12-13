import math

from core.live2d import UtSystem, Live2D, Live2DMotion, AMotion, Array, Float32Array, MotionQueueManager, PartsDataID, \
    PhysicsHair

import random


class L2DBaseModel:
    texCounter = 0

    def __init__(self):
        self.live2DModel = None
        self.modelMatrix = None
        self.eyeBlink = None
        self.physics = None
        self.pose = None
        self.debugMode = False
        self.initialized = False
        self.updating = False
        self.alpha = 1
        self.accAlpha = 0
        self.lipSync = False
        self.lipSyncValue = 0
        self.accelX = 0
        self.accelY = 0
        self.accelZ = 0
        self.dragX = 0
        self.dragY = 0
        self.startTimeMSec = 0
        self.mainMotionManager = L2DMotionManager()
        self.expressionManager = L2DMotionManager()
        self.motions = {}
        self.expressions = {}
        self.isTexLoaded = False

    def getModelMatrix(self):
        return self.modelMatrix

    def setAlpha(self, a):
        if a > 0.999:
            a = 1
        if a < 0.001:
            a = 0
        self.alpha = a

    def getAlpha(self):
        return self.alpha

    def isInitialized(self):
        return self.initialized

    def setInitialized(self, v):
        self.initialized = v

    def isUpdating(self):
        return self.updating

    def setUpdating(self, v):
        self.updating = v

    def getLive2DModel(self):
        return self.live2DModel

    def setLipSync(self, v):
        self.lipSync = v

    def setLipSyncValue(self, v):
        self.lipSyncValue = v

    def setAccel(self, x, y, z):
        self.accelX = x
        self.accelY = y
        self.accelZ = z

    def setDrag(self, x, y):
        self.dragX = x
        self.dragY = y

    def getMainMotionManager(self):
        return self.mainMotionManager

    def getExpressionManager(self):
        return self.expressionManager

    def loadModelData(self, path):
        pm = Live2DFramework.getPlatformManager()
        if self.debugMode:
            pm.log("Load model : " + path)

        self.live2DModel = pm.loadLive2DModel(path)
        self.live2DModel.saveParam()

        self.modelMatrix = L2DModelMatrix(self.live2DModel.getCanvasWidth(),
                                          self.live2DModel.getCanvasHeight())
        self.modelMatrix.setWidth(2)
        self.modelMatrix.setCenterPosition(0, 0)

        return self.live2DModel

    def loadTexture(self, no, path):
        self.texCounter += 1
        pm = Live2DFramework.getPlatformManager()
        if self.debugMode:
            pm.log("Load Texture : " + path)

        pm.loadTexture(self.live2DModel, no, path)

        self.texCounter -= 1
        if self.texCounter == 0:
            self.isTexLoaded = True

    def loadMotion(self, name, path):
        pm = Live2DFramework.getPlatformManager()
        if self.debugMode:
            pm.log("Load Motion : " + path)

        buf = pm.loadBytes(path)

        motion = Live2DMotion.loadMotion(buf)
        if name is not None:
            self.motions[name] = motion
        return motion

    def loadExpression(self, name, path):
        pm = Live2DFramework.getPlatformManager()
        if self.debugMode:
            pm.log("Load Expression : " + path)


        if name is not None:
            buf = pm.loadBytes(path)
            self.expressions[name] = L2DExpressionMotion.loadJson(buf)

    def loadPose(self, path):
        pm = Live2DFramework.getPlatformManager()
        if self.debugMode:
            pm.log("Load Pose : " + path)
        buf = pm.loadBytes(path)
        self.pose = L2DPose.load(buf)
        return self.pose

    def loadPhysics(self, path):
        pm = Live2DFramework.getPlatformManager()
        if self.debugMode:
            pm.log("Load Physics : " + path)
        buf = pm.loadBytes(path)
        self.physics = L2DPhysics.load(buf)

    def hitTestSimple(self, drawID, testX, testY):
        drawIndex = self.live2DModel.getDrawDataIndex(drawID)
        if drawIndex < 0:
            return False
        points = self.live2DModel.getTransformedPoints(drawIndex)
        left = self.live2DModel.getCanvasWidth()
        right = 0
        top = self.live2DModel.getCanvasHeight()
        bottom = 0
        # for(j = 0; j < points.length; j = j + 2):
        for j in range(0, len(points), 2):
            x = points[j]
            y = points[j + 1]
            if x < left:
                left = x
            if x > right:
                right = x
            if y < top:
                top = y
            if y > bottom:
                bottom = y

        tx = self.modelMatrix.invertTransformX(testX)
        ty = self.modelMatrix.invertTransformY(testY)
        return (left <= tx and tx <= right and top <= ty and ty <= bottom)


class L2DExpressionMotion(AMotion):
    EXPRESSION_DEFAULT = "DEFAULT"
    TYPE_SET = 0
    TYPE_ADD = 1
    TYPE_MULT = 2

    def __init__(self):
        super().__init__()
        self.paramList = Array()

    def updateParamExe(self, model, timeMSec, weight, motionQueueEnt):
        # for(i = len(this.paramList) - 1; i >= 0; --i):
        for i in range(len(self.paramList) - 1, -1, -1):
            param = self.paramList[i]
            if param.type == L2DExpressionMotion.TYPE_ADD:
                model.addToParamFloat(param.id, param.value, weight)
            elif param.type == L2DExpressionMotion.TYPE_MULT:
                model.multParamFloat(param.id, param.value, weight)
            elif param.type == L2DExpressionMotion.TYPE_SET:
                model.setParamFloat(param.id, param.value, weight)

    @staticmethod
    def loadJson(buf):
        ret = L2DExpressionMotion()
        pm = Live2DFramework.getPlatformManager()
        js = pm.jsonParseFromBytes(buf)
        ret.setFadeIn(int(js.get("fade_in", 0)) if int(js.get("fade_in", 0)) > 0 else 1000)
        ret.setFadeOut(int(js.get("fade_out", 0)) if int(js.get("fade_out", 0)) > 0 else 1000)
        if js.get("params", None) is None:
            return ret

        params = js["params"]
        paramNum = len(params)
        ret.paramList = []
        # for(i = 0; i < paramNum; i++):
        for i in range(0, paramNum, 1):
            param = params[i]
            paramID = str(param["id"])
            value = float(param["val"])
            calcTypeInt = L2DExpressionMotion.TYPE_ADD
            calc = str(param.get("calc", "add"))
            if calc == "add":
                calcTypeInt = L2DExpressionMotion.TYPE_ADD
            elif calc == "mult":
                calcTypeInt = L2DExpressionMotion.TYPE_MULT
            elif calc == "set":
                calcTypeInt = L2DExpressionMotion.TYPE_SET
            else:
                calcTypeInt = L2DExpressionMotion.TYPE_ADD

            if calcTypeInt == L2DExpressionMotion.TYPE_ADD:
                defaultValue = float(param.get("def", 0))
                value = value - defaultValue
            elif calcTypeInt == L2DExpressionMotion.TYPE_MULT:
                defaultValue = float(param.get("def", 1))
                if defaultValue == 0:
                    defaultValue = 1
                value = value / defaultValue

            item = L2DExpressionParam()
            item.id = paramID
            item.type = calcTypeInt
            item.value = value
            ret.paramList.append(item)

        return ret


class L2DExpressionParam:

    def __init__(self):
        self.id = ""
        self.type = -1
        self.value = None


class L2DEyeBlink:

    def __init__(self):
        self.nextBlinkTime = None
        self.stateStartTime = None
        self.blinkIntervalMsec = None
        self.eyeState = EYE_STATE.STATE_FIRST
        self.blinkIntervalMsec = 4000
        self.closingMotionMsec = 100
        self.closedMotionMsec = 50
        self.openingMotionMsec = 150
        self.closeIfZero = True
        self.eyeID_L = "PARAM_EYE_L_OPEN"
        self.eyeID_R = "PARAM_EYE_R_OPEN"

    def calcNextBlink(self):
        time = UtSystem.getUserTimeMSec()
        r = random.random()
        return (time + r * (2 * self.blinkIntervalMsec - 1))

    def setInterval(self, blinkIntervalMsec):
        self.blinkIntervalMsec = blinkIntervalMsec

    def setEyeMotion(self, closingMotionMsec, closedMotionMsec, openingMotionMsec):
        self.closingMotionMsec = closingMotionMsec
        self.closedMotionMsec = closedMotionMsec
        self.openingMotionMsec = openingMotionMsec

    def updateParam(self, model):
        time = UtSystem.getUserTimeMSec()
        eyeParamValue = None
        t = 0

        _switch_2297 = self.eyeState
        while True:
            if _switch_2297 == EYE_STATE.STATE_CLOSING:
                t = (time - self.stateStartTime) / self.closingMotionMsec
                if t >= 1:
                    t = 1
                    self.eyeState = EYE_STATE.STATE_CLOSED
                    self.stateStartTime = time

                eyeParamValue = 1 - t
                break
            if _switch_2297 == EYE_STATE.STATE_CLOSED:
                t = (time - self.stateStartTime) / self.closedMotionMsec
                if t >= 1:
                    self.eyeState = EYE_STATE.STATE_OPENING
                    self.stateStartTime = time

                eyeParamValue = 0
                break
            if _switch_2297 == EYE_STATE.STATE_OPENING:
                t = (time - self.stateStartTime) / self.openingMotionMsec
                if t >= 1:
                    t = 1
                    self.eyeState = EYE_STATE.STATE_INTERVAL
                    self.nextBlinkTime = self.calcNextBlink()

                eyeParamValue = t
                break
            if _switch_2297 == EYE_STATE.STATE_INTERVAL:
                if self.nextBlinkTime < time:
                    self.eyeState = EYE_STATE.STATE_CLOSING
                    self.stateStartTime = time

                eyeParamValue = 1
                break
            if _switch_2297 == EYE_STATE.STATE_FIRST:
                _switch_2297 = None
            else:
                self.eyeState = EYE_STATE.STATE_INTERVAL
                self.nextBlinkTime = self.calcNextBlink()
                eyeParamValue = 1
                break
            break
        if not self.closeIfZero:
            eyeParamValue = -eyeParamValue
        model.setParamFloat(self.eyeID_L, eyeParamValue)
        model.setParamFloat(self.eyeID_R, eyeParamValue)


class EYE_STATE:
    STATE_FIRST = "STATE_FIRST"
    STATE_INTERVAL = "STATE_INTERVAL"
    STATE_CLOSING = "STATE_CLOSING"
    STATE_CLOSED = "STATE_CLOSED"
    STATE_OPENING = "STATE_OPENING"


class L2DMatrix44():

    def __init__(self):
        self.tr = Float32Array(16)
        self.identity()

    def identity(self):
        for i in range(16):
            self.tr[i] = 1 if ((i % 5) == 0) else 0

    def getArray(self):
        return self.tr

    def getCopyMatrix(self):
        return Float32Array(self.tr)

    def setMatrix(self, tr):
        if self.tr is None or self.tr.length != self.tr.length:
            return
        for i in range(16):
            self.tr[i] = tr[i]

    def getScaleX(self):
        return self.tr[0]

    def getScaleY(self):
        return self.tr[5]

    def transformX(self, src):
        return self.tr[0] * src + self.tr[12]

    def transformY(self, src):
        return self.tr[5] * src + self.tr[13]

    def invertTransformX(self, src):
        return (src - self.tr[12]) / self.tr[0]

    def invertTransformY(self, src):
        return (src - self.tr[13]) / self.tr[5]

    def multTranslate(self, shiftX, shiftY):
        tr1 = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, shiftX, shiftY, 0, 1]
        L2DMatrix44.mul(tr1, self.tr, self.tr)

    def translate(self, x, y):
        self.tr[12] = x
        self.tr[13] = y

    def translateX(self, x):
        self.tr[12] = x

    def translateY(self, y):
        self.tr[13] = y

    def multScale(self, scaleX, scaleY):
        tr1 = [scaleX, 0, 0, 0, 0, scaleY, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        L2DMatrix44.mul(tr1, self.tr, self.tr)

    def scale(self, scaleX, scaleY):
        self.tr[0] = scaleX
        self.tr[5] = scaleY

    @staticmethod
    def mul(a, b, dst):
        c = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        n = 4
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    c[i + j * 4] += a[i + k * 4] * b[k + j * 4]

        for i in range(16):
            dst[i] = c[i]


class L2DModelMatrix(L2DMatrix44):

    def __init__(self, w, h):
        super().__init__()
        self.width = w
        self.height = h

    def setPosition(self, x, y):
        self.translate(x, y)

    def setCenterPosition(self, x, y):
        w = self.width * self.getScaleX()
        h = self.height * self.getScaleY()
        self.translate(x - w / 2, y - h / 2)

    def top(self, y):
        self.setY(y)

    def bottom(self, y):
        h = self.height * self.getScaleY()
        self.translateY(y - h)

    def left(self, x):
        self.setX(x)

    def right(self, x):
        w = self.width * self.getScaleX()
        self.translateX(x - w)

    def centerX(self, x):
        w = self.width * self.getScaleX()
        self.translateX(x - w / 2)

    def centerY(self, y):
        h = self.height * self.getScaleY()
        self.translateY(y - h / 2)

    def setX(self, x):
        self.translateX(x)

    def setY(self, y):
        self.translateY(y)

    def setHeight(self, h):
        scaleX = h / self.height
        scaleY = -scaleX
        self.scale(scaleX, scaleY)

    def setWidth(self, w):
        scaleX = w / self.width
        scaleY = -scaleX
        self.scale(scaleX, scaleY)


class L2DMotionManager(MotionQueueManager):

    def __init__(self):
        super().__init__()
        self.currentPriority = 0
        self.reservePriority = 0

    def getCurrentPriority(self):
        return self.currentPriority

    def getReservePriority(self):
        return self.reservePriority

    def reserveMotion(self, priority):
        if self.reservePriority >= priority:
            return False

        if self.currentPriority >= priority:
            return False

        self.reservePriority = priority
        return True

    def setReservePriority(self, val):
        self.reservePriority = val

    def updateParam(self, model):
        updated = super().updateParam(model)
        if self.isFinished():
            self.currentPriority = 0

        return updated

    def startMotionPrio(self, motion, priority):
        if priority == self.reservePriority:
            self.reservePriority = 0

        self.currentPriority = priority
        return self.startMotion(motion, False)


class L2DPhysics():

    def __init__(self):
        self.physicsList = Array()
        self.startTimeMSec = UtSystem.getUserTimeMSec()

    def updateParam(self, model):
        timeMSec = UtSystem.getUserTimeMSec() - self.startTimeMSec
        for i in range(len(self.physicsList)):
            self.physicsList[i].update(model, timeMSec)

    @staticmethod
    def load(buf):
        ret = L2DPhysics()
        pm = Live2DFramework.getPlatformManager()
        json = pm.jsonParseFromBytes(buf)
        params = json.get("physics_hair")
        paramNum = len(params)
        for i in range(paramNum):
            param = params[i]
            physics = PhysicsHair()
            setup = param.get("setup")
            length = float(len(setup))
            resist = float(setup.get("regist"))
            mass = float(setup.get("mass"))
            physics.setup(length, resist, mass)
            srcList = param.get("src")
            srcNum = len(srcList)
            for j in range(srcNum):
                src = srcList[j]
                id = src.get("id")
                type = PhysicsHair.Src.SRC_TO_X
                typeStr = src.get("ptype")
                if typeStr == "x":
                    type = PhysicsHair.Src.SRC_TO_X
                elif typeStr == "y":
                    type = PhysicsHair.Src.SRC_TO_Y
                elif typeStr == "angle":
                    type = PhysicsHair.Src.SRC_TO_G_ANGLE
                else:
                    raise Exception("error")

                scale = float(src.get("scale"))
                weight = float(src.get("weight"))
                physics.addSrcParam(type, id, scale, weight)

            targetList = param.get("targets")
            targetNum = len(targetList)
            for j in range(targetNum):
                target = targetList[j]
                id = target.get("id")
                type = PhysicsHair.Target.TARGET_FROM_ANGLE
                typeStr = target.get("ptype")
                if typeStr == "angle":
                    type = PhysicsHair.Target.TARGET_FROM_ANGLE
                elif typeStr == "angle_v":
                    type = PhysicsHair.Target.TARGET_FROM_ANGLE_V
                else:
                    raise Exception("live2d", "Invalid parameter:PhysicsHair.Target")

                scale = float(target.get("scale"))
                weight = float(target.get("weight"))
                physics.addTargetParam(type, id, scale, weight)

            ret.physicsList.append(physics)

        return ret


class L2DPose():

    def __init__(self):
        self.lastTime = 0
        self.lastModel = None
        self.partsGroups = Array()

    def updateParam(self, model):
        if model == None:
            return
        if not (model == self.lastModel):
            self.initParam(model)

        self.lastModel = model
        curTime = UtSystem.getUserTimeMSec()
        deltaTimeSec = (0 if (self.lastTime == 0) else (curTime - self.lastTime) / 1000.0)
        self.lastTime = curTime
        if deltaTimeSec < 0:
            deltaTimeSec = 0
        for i in range(len(self.partsGroups)):
            self.normalizePartsOpacityGroup(model, self.partsGroups[i], deltaTimeSec)
            self.copyOpacityOtherParts(model, self.partsGroups[i])

    def initParam(self, model):
        if model == None:
            return
        for i in range(len(self.partsGroups)):
            partsGroup = self.partsGroups[i]
            for j in range(len(partsGroup)):
                partsGroup[j].initIndex(model)
                partsIndex = partsGroup[j].partsIndex
                paramIndex = partsGroup[j].paramIndex
                if partsIndex < 0:
                    continue
                v = (model.getParamFloat(paramIndex) != 0)
                model.setPartsOpacity(partsIndex, (1.0 if v else 0.0))
                model.setParamFloat(paramIndex, (1.0 if v else 0.0))
                if partsGroup[j].link == None:
                    continue
                for k in range(len(partsGroup[j].link)):
                    partsGroup[j].link[k].initIndex(model)

    def normalizePartsOpacityGroup(self, model, partsGroup, deltaTimeSec):
        visibleParts = -1
        visibleOpacity = 1.0
        CLEAR_TIME_SEC = 0.5
        phi = 0.5
        maxBackOpacity = 0.15
        for i in range(len(partsGroup)):
            partsIndex = partsGroup[i].partsIndex
            paramIndex = partsGroup[i].paramIndex
            if partsIndex < 0:
                continue
            if model.getParamFloat(paramIndex) != 0:
                if visibleParts >= 0:
                    break

                visibleParts = i
                visibleOpacity = model.getPartsOpacity(partsIndex)
                visibleOpacity += deltaTimeSec / CLEAR_TIME_SEC
                if visibleOpacity > 1:
                    visibleOpacity = 1

        if visibleParts < 0:
            visibleParts = 0
            visibleOpacity = 1

        for i in range(len(partsGroup)):
            partsIndex = partsGroup[i].partsIndex
            if partsIndex < 0:
                continue
            if visibleParts == i:
                model.setPartsOpacity(partsIndex, visibleOpacity)
            else:
                opacity = model.getPartsOpacity(partsIndex)
                a1 = None
                if visibleOpacity < phi:
                    a1 = visibleOpacity * (phi - 1) / phi + 1
                else:
                    a1 = (1 - visibleOpacity) * phi / (1 - phi)

                backOp = (1 - a1) * (1 - visibleOpacity)
                if backOp > maxBackOpacity:
                    a1 = 1 - maxBackOpacity / (1 - visibleOpacity)

                if opacity > a1:
                    opacity = a1

                model.setPartsOpacity(partsIndex, opacity)

    def copyOpacityOtherParts(self, model, partsGroup):
        for i_group in range(len(partsGroup)):
            partsParam = partsGroup[i_group]
            if partsParam.link == None:
                continue
            if partsParam.partsIndex < 0:
                continue
            opacity = model.getPartsOpacity(partsParam.partsIndex)
            for i_link in range(len(partsParam.link)):
                linkParts = partsParam.link[i_link]
                if linkParts.partsIndex < 0:
                    continue
                model.setPartsOpacity(linkParts.partsIndex, opacity)

    @staticmethod
    def load(buf):
        ret = L2DPose()
        pm = Live2DFramework.getPlatformManager()
        json = pm.jsonParseFromBytes(buf)
        poseListInfo = json.get("parts_visible")
        poseNum = len(poseListInfo)
        for i_pose in range(poseNum):
            poseInfo = poseListInfo[i_pose]
            idListInfo = poseInfo.get("group")
            idNum = len(idListInfo)
            partsGroup = Array()
            for i_group in range(idNum):
                partsInfo = idListInfo[i_group]
                parts = L2DPartsParam(partsInfo["id"])
                partsGroup.append(parts)
                if partsInfo.get("link") is None:
                    continue
                linkListInfo = partsInfo.get("link")
                linkNum = len(linkListInfo)
                parts.link = Array()
                for i_link in range(linkNum):
                    linkParts = L2DPartsParam(linkListInfo[i_link])
                    parts.link.append(linkParts)

            ret.partsGroups.append(partsGroup)

        return ret


class L2DPartsParam():

    def __init__(self, id):
        self.paramIndex = -1
        self.partsIndex = -1
        self.link = None
        self.id = id

    def initIndex(self, model):
        self.paramIndex = model.getParamIndex("VISIBLE:" + self.id)
        self.partsIndex = model.getPartsDataIndex(PartsDataID.getID(self.id))
        model.setParamFloat(self.paramIndex, 1)


class L2DTargetPoint():
    FRAME_RATE = 30

    def __init__(self):
        self.EPSILON = 0.01
        self.faceTargetX = 0
        self.faceTargetY = 0
        self.faceX = 0
        self.faceY = 0
        self.faceVX = 0
        self.faceVY = 0
        self.lastTimeSec = 0

    def setPoint(self, x, y):
        self.faceTargetX = x
        self.faceTargetY = y

    def getX(self):
        return self.faceX

    def getY(self):
        return self.faceY

    def update(self):
        TIME_TO_MAX_SPEED = 0.15
        FACE_PARAM_MAX_V = 40.0 / 7.5
        MAX_V = FACE_PARAM_MAX_V / L2DTargetPoint.FRAME_RATE
        if self.lastTimeSec == 0:
            self.lastTimeSec = UtSystem.getUserTimeMSec()
            return

        curTimeSec = UtSystem.getUserTimeMSec()
        deltaTimeWeight = (curTimeSec - self.lastTimeSec) * L2DTargetPoint.FRAME_RATE / 1000.0
        self.lastTimeSec = curTimeSec
        FRAME_TO_MAX_SPEED = TIME_TO_MAX_SPEED * L2DTargetPoint.FRAME_RATE
        MAX_A = deltaTimeWeight * MAX_V / FRAME_TO_MAX_SPEED
        dx = (self.faceTargetX - self.faceX)
        dy = (self.faceTargetY - self.faceY)
        if abs(dx) <= self.EPSILON and abs(dy) <= self.EPSILON:
            return
        d = math.sqrt(dx * dx + dy * dy)
        vx = MAX_V * dx / d
        vy = MAX_V * dy / d
        ax = vx - self.faceVX
        ay = vy - self.faceVY
        a = math.sqrt(ax * ax + ay * ay)
        if a < -MAX_A or a > MAX_A:
            ax *= MAX_A / a
            ay *= MAX_A / a
            a = MAX_A

        self.faceVX += ax
        self.faceVY += ay

        max_v = 0.5 * (math.sqrt(MAX_A * MAX_A + 16 * MAX_A * d - 8 * MAX_A * d) - MAX_A)
        cur_v = math.sqrt(self.faceVX * self.faceVX + self.faceVY * self.faceVY)
        if cur_v > max_v:
            self.faceVX *= max_v / cur_v
            self.faceVY *= max_v / cur_v

        self.faceX += self.faceVX
        self.faceY += self.faceVY


class L2DViewMatrix(L2DMatrix44):

    def __init__(self):
        super().__init__()
        self.screenLeft = None
        self.screenRight = None
        self.screenTop = None
        self.screenBottom = None
        self.maxLeft = None
        self.maxRight = None
        self.maxTop = None
        self.maxBottom = None
        self.max = float('inf')
        self.min = 0

    def getMaxScale(self):
        return self.max

    def getMinScale(self):
        return self.min

    def setMaxScale(self, v):
        self.max = v

    def setMinScale(self, v):
        self.min = v

    def isMaxScale(self):
        return self.getScaleX() == self.max

    def isMinScale(self):
        return self.getScaleX() == self.min

    def adjustTranslate(self, shiftX, shiftY):
        if self.tr[0] * self.maxLeft + (self.tr[12] + shiftX) > self.screenLeft:
            shiftX = self.screenLeft - self.tr[0] * self.maxLeft - self.tr[12]
        if self.tr[0] * self.maxRight + (self.tr[12] + shiftX) < self.screenRight:
            shiftX = self.screenRight - self.tr[0] * self.maxRight - self.tr[12]
        if self.tr[5] * self.maxTop + (self.tr[13] + shiftY) < self.screenTop:
            shiftY = self.screenTop - self.tr[5] * self.maxTop - self.tr[13]
        if self.tr[5] * self.maxBottom + (self.tr[13] + shiftY) > self.screenBottom:
            shiftY = self.screenBottom - self.tr[5] * self.maxBottom - self.tr[13]
        tr1 = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, shiftX, shiftY, 0, 1]
        L2DMatrix44.mul(tr1, self.tr, self.tr)

    def adjustScale(self, cx, cy, scale):
        targetScale = scale * self.tr[0]
        if targetScale < self.min:
            if self.tr[0] > 0:
                scale = self.min / self.tr[0]
        elif targetScale > self.max:
            if self.tr[0] > 0:
                scale = self.max / self.tr[0]

        tr1 = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, cx, cy, 0, 1]
        tr2 = [scale, 0, 0, 0, 0, scale, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        tr3 = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -cx, -cy, 0, 1]
        L2DMatrix44.mul(tr3, self.tr, self.tr)
        L2DMatrix44.mul(tr2, self.tr, self.tr)
        L2DMatrix44.mul(tr1, self.tr, self.tr)

    def setScreenRect(self, left, right, bottom, top):
        self.screenLeft = left
        self.screenRight = right
        self.screenTop = top
        self.screenBottom = bottom

    def setMaxScreenRect(self, left, right, bottom, top):
        self.maxLeft = left
        self.maxRight = right
        self.maxTop = top
        self.maxBottom = bottom

    def getScreenLeft(self):
        return self.screenLeft

    def getScreenRight(self):
        return self.screenRight

    def getScreenBottom(self):
        return self.screenBottom

    def getScreenTop(self):
        return self.screenTop

    def getMaxLeft(self):
        return self.maxLeft

    def getMaxRight(self):
        return self.maxRight

    def getMaxBottom(self):
        return self.maxBottom

    def getMaxTop(self):
        return self.maxTop


class Live2DFramework():
    platformManager = None

    @staticmethod
    def getPlatformManager():
        return Live2DFramework.platformManager

    @staticmethod
    def setPlatformManager(platformManager):
        Live2DFramework.platformManager = platformManager
