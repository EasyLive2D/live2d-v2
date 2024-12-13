from .iphysics_param import IPhysicsParam
from . import physics_constants


class PhysicsTarget(IPhysicsParam):

    def __init__(self, aI, aK, aJ, aH):
        super().__init__(aK, aJ, aH)
        self.YP_ = aI

    def YS_(self, aI, aH):
        if self.YP_ == physics_constants.TARGET_FROM_ANGLE:
            aI.setParamFloat(self.wL_, self.scale * aH._5r(), self.V0_)
        elif self.YP_ == physics_constants.TARGET_FROM_ANGLE_V:
            aI.setParamFloat(self.wL_, self.scale * aH.Cs_(), self.V0_)
