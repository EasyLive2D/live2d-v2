import pygame

from core.live2d import Live2D
from framework.Live2DFramework import Live2DFramework
from lapp_model import LAppModel
from platform_manager import PlatformManager

SCR_WIDTH = 300
SCR_HEIGHT = 300

pygame.init()
pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)

Live2D.init()

Live2DFramework.setPlatformManager(PlatformManager())

model = LAppModel()

name = "haru"
model.LoadModelJson(f"../resources/{name}/{name}.model.json")

drag = False
scaling = 1
dx = 0
dy = 0

model.SetAutoBreathEnable(False)
model.SetAutoBlinkEnable(False)

last_part_id: str | None = None


def onEvent(e):
    global scaling, dx, dy, last_part_id
    ds = 0.1
    if e.type == pygame.MOUSEMOTION:
        x, y = pygame.mouse.get_pos()
        model.Drag(x, y)
    elif e.type == pygame.MOUSEBUTTONUP:
        x, y = pygame.mouse.get_pos()
        ids = model.HitPart(x, y)
        print(ids)
        if len(ids) > 0:
            if last_part_id is not None:
                model.SetPartOpacity(partIds.index(last_part_id), 1)
            last_part_id = ids[0]
        # model.Touch(*pygame.mouse.get_pos())
        # model.StartRandomMotion(priority=MotionPriority.FORCE)
    elif e.type == pygame.KEYDOWN:
        if e.key == pygame.K_a:
            dx -= 0.1
            model.SetOffset(dx, dy)
        elif e.key == pygame.K_d:
            dx += 0.1
            model.SetOffset(dx, dy)
        elif e.key == pygame.K_w:
            dy += 0.1
            model.SetOffset(dx, dy)
        elif e.key == pygame.K_s:
            dy -= 0.1
            model.SetOffset(dx, dy)
        elif e.key == pygame.K_EQUALS:
            scaling += ds
            model.SetScale(scaling)
        elif e.key == pygame.K_MINUS:
            scaling = max(scaling - ds, 0.1)
            model.SetScale(scaling)


model.Resize(SCR_WIDTH, SCR_HEIGHT)

for i in range(model.GetParameterCount()):
    print(model.GetParameter(i))

print(model.GetPartCount())
partIds = model.GetPartIds()
print(partIds)
model.SetPartOpacity(partIds.index('PARTS_01_HAIR_BACK_001'), 0.8)

running = True
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
            break
        onEvent(e)

    if not running:
        break

    Live2D.clearBuffer()

    model.Update()
    if last_part_id is not None:
        model.SetPartOpacity(partIds.index(last_part_id), 0.5)
    model.Draw()
    pygame.display.flip()

Live2D.dispose()
pygame.quit()
