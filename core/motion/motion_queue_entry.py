from core.util import UtSystem


class MotionQueueEntry:

    def __init__(self):
        self.w0_ = None
        self.AT_ = True
        self._9L = False
        self.z2_ = -1
        self.bs_ = -1
        self.Do_ = -1
        self.sr_ = None
        self.sr_ = MotionQueueEntry.Gs_
        MotionQueueEntry.Gs_ += 1

    def isFinished(self):
        return self._9L

    def qS_(self, aJ):
        aI = UtSystem.getUserTimeMSec()
        aH = aI + aJ
        if self.Do_ < 0 or aH < self.Do_:
            self.Do_ = aH

    def Bs_(self):
        return self.sr_

    Gs_ = 0
