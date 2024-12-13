from .iphysics_param import IPhysicsParam
from . import physics_constants

class PhysicsSrc(IPhysicsParam):

    def __init__(self, aJ, aK, aI, aH):
        super().__init__(aK, aI, aH)
        self.tL_ = None
        self.tL_ = aJ

    def oP_(self, aJ, aH):
        aK = self.scale * aJ.getParamFloat(self.wL_)
        aL = aH.getPhysicsPoint1()

        switch = self.tL_
        if switch == physics_constants.SRC_TO_X:
            aL.x = aL.x + (aK - aL.x) * self.V0_
        elif switch == physics_constants.SRC_TO_Y:
            aL.y = aL.y + (aK - aL.y) * self.V0_
        elif switch == physics_constants.SRC_TO_G_ANGLE:
            aI = aH.qr_()
            aI = aI + (aK - aI) * self.V0_
            aH.pr_(aI)
