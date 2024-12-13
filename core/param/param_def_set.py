from core.type import Array


class ParamDefSet:

    def __init__(self):
        self._4S = None

    def _1s(self):
        return self._4S

    def zP_(self):
        self._4S = Array()

    def read(self, aH):
        self._4S = aH.readObject()

    def Ks_(self, aH):
        self._4S.append(aH)
