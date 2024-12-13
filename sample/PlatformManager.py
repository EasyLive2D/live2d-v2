import json

from PIL import Image

from core.live2d_model_opengl import Live2DModelOpenGL
import OpenGL.GL as gl


class PlatformManager:

    def loadBytes(self, path):
        with open(path, 'rb') as f:
            return f.read()

    def loadLive2DModel(self, path):
        with open(path, 'rb') as f:
            return Live2DModelOpenGL.loadModel(f.read())

    def loadTexture(self, live2DModel, no, path):
        image = Image.open(path)
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
        live2DModel.setTexture(no, texture)

    def jsonParseFromBytes(self, path):
        return json.loads(path)
