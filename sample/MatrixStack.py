from core.type.array import Array


class MatrixStack:
    matrixStack = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    depth = 0
    currentMatrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    tmp = Array(16)

    @staticmethod
    def reset():
        MatrixStack.depth = 0

    @staticmethod
    def loadIdentity():
        for i in range(16):
            MatrixStack.currentMatrix[i] = 1 if (i % 5 == 0) else 0

    @staticmethod
    def push():
        offset = MatrixStack.depth * 16
        nextOffset = (MatrixStack.depth + 1) * 16
        if len(MatrixStack.matrixStack) < nextOffset + 16:
            MatrixStack.matrixStack += [0] * 16

        for i in range(16):
            MatrixStack.matrixStack[nextOffset + i] = MatrixStack.currentMatrix[i]

        MatrixStack.depth += 1

    @staticmethod
    def pop():
        MatrixStack.depth -= 1
        if MatrixStack.depth < 0:
            MatrixStack.depth = 0
            raise Exception("Invalid matrix stack.")

        offset = MatrixStack.depth * 16
        for i in range(16):
            MatrixStack.currentMatrix[i] = MatrixStack.matrixStack[offset + i]

    @staticmethod
    def getMatrix():
        return MatrixStack.currentMatrix

    @staticmethod
    def multMatrix(matNew):
        for i in range(16):
            MatrixStack.tmp[i] = 0

        for i in range(4):
            for j in range(4):
                for k in range(4):
                    MatrixStack.tmp[i + j * 4] += MatrixStack.currentMatrix[i + k * 4] * matNew[k + j * 4]

        for i in range(16):
            MatrixStack.currentMatrix[i] = MatrixStack.tmp[i]
