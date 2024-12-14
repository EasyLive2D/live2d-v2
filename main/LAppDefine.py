DEBUG_LOG = True
DEBUG_MOUSE_LOG = False

VIEW_MAX_SCALE = 2
VIEW_MIN_SCALE = 0.8

VIEW_LOGICAL_LEFT = -1.0
VIEW_LOGICAL_RIGHT = 1.0

VIEW_LOGICAL_MAX_LEFT = -2.0
VIEW_LOGICAL_MAX_RIGHT = 2.0
VIEW_LOGICAL_MAX_BOTTOM = -2.0
VIEW_LOGICAL_MAX_TOP = 2.0


class MotionPriority:
    NONE = 0
    IDLE = 1
    NORMAL = 2
    FORCE = 3


class MotionGroup:
    IDLE = "idle"
    TAP_BODY = "tap_body"
    FLICK_HEAD = "flick_head"
    PINCH_IN = "pinch_in"
    PINCH_OUT = "pinch_out"
    SHAKE = "shake"


class HitArea:
    HEAD = "head"
    BODY = "body"
