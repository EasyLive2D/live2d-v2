class PhysicsPoint:

    def __init__(self):
        self.p_ = 1
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        self.fx = 0
        self.fy = 0
        self.s0_ = 0
        self._70 = 0
        self._7L = 0
        self.HL_ = 0

    def xT_(self):
        self.s0_ = self.x
        self._70 = self.y
        self._7L = self.vx
        self.HL_ = self.vy
