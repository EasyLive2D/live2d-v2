from core.motion.motion_queue_entry import MotionQueueEntry


class MotionQueueManager:

    def __init__(self):
        self.eb_ = False
        self.motions = []

    def tb_(self):
        return self.motions

    def startMotion(self, aJ, aI):
        aH = len(self.motions)
        for aK in range(0, aH, 1):
            aL = self.motions[aK]
            if aL is None:
                continue

            aL.qS_(aL.w0_.getFadeOut())
            if self.eb_:
                print("MotionQueueManager[size:%2d]->startMotion() / start _K _3 (m%d)\n", aH, aL.sr_)

        if aJ is None:
            return -1

        aL = MotionQueueEntry()
        aL.w0_ = aJ
        self.motions.append(aL)
        aN = aL.sr_
        if self.eb_:
            print("MotionQueueManager[size:%2d]->startMotion() / new w0_ (m%d)\n", aH, aN)

        return aN

    def updateParam(self, aJ):
        aI = False
        aK = 0
        size = len(self.motions)
        while aK < size:
            aL = self.motions[aK]
            if aL is None:
                self.motions.pop(aK)
                size -= 1
                continue

            aH = aL.w0_
            if aH is None:
                self.motions.pop(aK)
                size -= 1
                continue

            aH.updateParam(aJ, aL)
            aI = True
            if aL.isFinished():
                if self.eb_:
                    print("MotionQueueManager[size:%2d]->updateParam() / T0_ w0_ (m%d)\n",
                          len(self.motions) - 1, aL.sr_)

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
                if aJ is None:
                    continue

                if aJ.sr_ == aK and not aJ.isFinished():
                    return False

            return True
        else:
            aI = 0
            size = len(self.motions)
            while aI < size:
                aJ = self.motions[aI]
                if aJ is None:
                    self.motions.pop(aI)
                    size -= 1
                    continue

                aH = aJ.w0_
                if aH is None:
                    self.motions.pop(aI)
                    size -= 1
                    continue

                if not aJ.isFinished():
                    return False
                aI += 1

            return True

    def stopAllMotions(self):
        size = len(self.motions)
        aI = 0
        while aI < size:
            aJ = self.motions[aI]
            if aJ is None:
                self.motions.pop(aI)
                size -= 1
                continue

            aH = aJ.w0_
            if aH is None:
                self.motions.pop(aI)
                size -= 1
                continue

            self.motions.pop(aI)
            size -= 1

    def Zr_(self, aH):
        self.eb_ = aH

    def _e(self):
        print("-- _R --\n")
        for aH in range(0, len(self.motions), 1):
            aI = self.motions[aH]
            aJ = aI.w0_
            print("MotionQueueEnt[%d] :: %s\n", len(self.motions), str(aJ))
