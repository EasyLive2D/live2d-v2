import math

import OpenGL.GL as gl
import PIL.Image as Image
import pygame
from pygame.locals import *

from core.live2d import *
from core.live2d_model_opengl import Live2DModelOpenGL
from core.util import UtSystem


class ModelDef:

    def __init__(self, model, textures):
        self.model = model
        self.textures = textures


def loadImage(filePath):
    image = Image.open(filePath)
    if image.mode != 'RGBA':
        image = image.convert("RGBA")
    image_data = image.tobytes()
    width, height = image.size
    gl.glEnable(gl.GL_TEXTURE_2D)
    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_data
    )
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return texture


# name = "kasumi"
# modelDef = ModelDef(
#     f"../test-data/{name}.moc",
#     [f"../test-data/{name}.png"]
# )

# rendering does not work properly for this model
modelDef = ModelDef(
    "../resources/haru/haru.moc",
    [
        "../resources/haru/haru.1024/texture_00.png",
        "../resources/haru/haru.1024/texture_01.png",
        "../resources/haru/haru.1024/texture_02.png",
    ]
)

SCR_WIDTH = 600
SCR_HEIGHT = 600

pygame.init()
pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)

Live2D.init()

with open(modelDef.model, 'rb') as f:
    live2DModel = Live2DModelOpenGL.loadModel(f.read())

for i, f in enumerate(modelDef.textures):
    live2DModel.setTexture(i, loadImage(f))


def processEvents(running):
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    return running


live2DModel.setAnisotropy(False)
live2DModel.setPremultipliedAlpha(False)

running = True
while True:
    running = processEvents(running)

    if not running:
        break

    gl.glClearColor(0.0, 0.0, 0.0, 0.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    s = 2.0 / live2DModel.getCanvasWidth()
    mat4 = [
        s, 0, 0, 0,
        0, -s, 0, 0,
        0, 0, 1, 0,
        -1, 1, 0, 1
    ]
    live2DModel.setMatrix(mat4)

    t = UtSystem.getUserTimeMSec() * 0.001 * 2 * math.pi
    cycle = 3.0

    live2DModel.setParamFloat("PARAM_ANGLE_X", 30 * math.sin(t / cycle))
    live2DModel.setParamFloat("PARAM_EYE_R_OPEN", 1 * math.sin(t / cycle))
    live2DModel.setParamFloat("PARAM_EYE_L_OPEN", 1 * math.sin(t / cycle))
    live2DModel.setParamFloat("PARAM_BREATH", 1 * math.sin(t / cycle))

    live2DModel.update()
    live2DModel.draw()
    pygame.display.flip()

Live2D.dispose()

pygame.quit()
