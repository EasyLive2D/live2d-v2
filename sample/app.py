import pygame

from LAppModel import LAppModel
from PlatformManager import PlatformManager
import LAppDefine
from MatrixStack import MatrixStack
from core.live2d import Live2D
from core.live2d_gl_wrapper import Live2DGLWrapper
from framework.Live2DFramework import Live2DFramework, L2DTargetPoint, L2DViewMatrix, L2DMatrix44

SCR_WIDTH = 300
SCR_HEIGHT = 300

pygame.init()
pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)

gl = Live2DGLWrapper(SCR_WIDTH, SCR_HEIGHT)
Live2D.init()
Live2D.setGL(gl)

Live2DFramework.setPlatformManager(PlatformManager())

model = LAppModel()

name = "haru"
model.load(f"../resources/{name}/{name}.model.json")

dragMgr = L2DTargetPoint()
ratio = SCR_HEIGHT / SCR_WIDTH
left = LAppDefine.VIEW_LOGICAL_LEFT
right = LAppDefine.VIEW_LOGICAL_RIGHT
bottom = -ratio
top = ratio
viewMatrix = L2DViewMatrix()
viewMatrix.setScreenRect(left, right, bottom, top)
viewMatrix.setMaxScreenRect(
    LAppDefine.VIEW_LOGICAL_MAX_LEFT,
    LAppDefine.VIEW_LOGICAL_MAX_RIGHT,
    LAppDefine.VIEW_LOGICAL_MAX_BOTTOM,
    LAppDefine.VIEW_LOGICAL_MAX_TOP
)

viewMatrix.setMaxScale(10)
viewMatrix.setMinScale(0.1)
projMatrix = L2DMatrix44()
projMatrix.multScale(1, (SCR_WIDTH / SCR_HEIGHT))

deviceToScreen = L2DMatrix44()
deviceToScreen.multTranslate(-SCR_WIDTH / 2.0, -SCR_HEIGHT / 2.0)
deviceToScreen.multScale(2 / SCR_WIDTH, -2 / SCR_WIDTH)

drag = False

lastMouseX = 0
lastMouseY = 0


def lookFront():
    global drag
    drag = False

    dragMgr.setPoint(0.0, 0.0)

scaling = 1

def mouseEvent(e):
    global scaling
    ds = 0.1
    if e.type == pygame.MOUSEWHEEL:
        if e.y > 0:
            scaling += ds
            viewMatrix.adjustScale(0, 0, scaling)
        else:
            scaling = max(scaling - ds, 0.1)
            viewMatrix.adjustScale(0, 0, scaling)
    elif e.type == pygame.MOUSEMOTION:
        x, y = pygame.mouse.get_pos()
        sx = deviceToScreen.transformX(x)
        vx = viewMatrix.invertTransformX(sx)
        sy = deviceToScreen.transformY(y)
        vy = viewMatrix.invertTransformY(sy)

        dragMgr.setPoint(vx, vy)
    elif e.type == pygame.MOUSEBUTTONUP:
        model.startRandomMotion(priority=LAppDefine.PRIORITY_FORCE)

running = True
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
            break
        mouseEvent(e)

    if not running:
        break

    MatrixStack.reset()
    MatrixStack.loadIdentity()

    dragMgr.update()

    model.setDrag(dragMgr.getX(), dragMgr.getY())

    gl.clear(gl.COLOR_BUFFER_BIT)

    MatrixStack.multMatrix(projMatrix.getArray())
    MatrixStack.multMatrix(viewMatrix.getArray())
    MatrixStack.push()

    model.update()
    model.draw()

    MatrixStack.pop()
    pygame.display.flip()

Live2D.dispose()
pygame.quit()


