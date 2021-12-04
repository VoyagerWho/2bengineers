import math


class Vector2:

    def __init__(self, x: float = 0.0, y: float = 0.0):
        if (isinstance(x, float) or isinstance(x, int)) and (
                isinstance(y, float) or isinstance(y, int)):  # normalne konstruowanie
            self.x: float = float(x)
            self.y: float = float(y)
        elif (isinstance(x, Vector2) or isinstance(x, list)):  # lista lub inny Vector2
            self.x = float(x[0])
            self.y = float(x[1])
        else:  # nie ma co innego robić
            raise Exception("Invalid constructor argumens", type(x), type(y))

    def __add__(self, v):
        if isinstance(v, Vector2) or isinstance(v, list):
            return Vector2(self.x + v[0], self.y + v[1])
        if isinstance(v, int) or isinstance(v, float):
            return Vector2(self.x + v, self.y + v)
        return None

    def __sub__(self, v):
        if isinstance(v, Vector2) or isinstance(v, list):
            return Vector2(self.x - v[0], self.y - v[1])
        if isinstance(v, int) or isinstance(v, float):
            return Vector2(self.x - v, self.y - v)
        return None

    def __mul__(self, v):
        if isinstance(v, Vector2) or isinstance(v, list):
            return self.x * v[0] + self.y * v[1]  # mnożenie skalarne vector * vector
        if isinstance(v, int) or isinstance(v, float):
            return Vector2(self.x * v, self.y * v)  # mnożenie wektora przez skalar
        return None

    def __truediv__(self, v: float):
        return Vector2(self.x / v, self.y / v)

    def __getitem__(self, index: int):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        return None

    def __pos__(self):
        return copy()

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __iadd__(self, v):
        if isinstance(v, Vector2) or isinstance(v, list):
            self.x += v[0]
            self.y += v[1]
            return self
        if isinstance(v, int) or isinstance(v, float):
            self.x += v
            self.y += v
            return self
        return None

    def __isub__(self, v):
        if isinstance(v, Vector2) or isinstance(v, list):
            self.x -= v[0]
            self.y -= v[1]
            return self
        if isinstance(v, int) or isinstance(v, float):
            self.x -= v
            self.y -= v
            return self
        return None

    def length(self):
        return math.hypot(self.x, self.y)

    def angle(self):
        return math.atan2(self.y, self.x)

    def normal(self):
        l: float = self.length()
        if l == 0:
            return Vector2()
        return Vector2(self.x / l, self.y / l)

    def copy(self):
        return Vector2(self.x, self.y)

    def __str__(self):
        return "[" + str(self.x) + "; " + str(self.y) + "]"


class Matrix2x2:

    def __init__(self, UpRow: Vector2 = None, DownRow: Vector2 = None, LeftCol: Vector2 = None,
                 RightCol: Vector2 = None):
        self.__data = [[0, 0], [0, 0]]
        if UpRow is not None:
            self.setRow(0, UpRow)
        if DownRow is not None:
            self.setRow(1, DownRow)
        if LeftCol is not None:
            self.setCol(0, LeftCol)
        if RightCol is not None:
            self.setCol(1, RightCol)

    @staticmethod
    def identity():
        a = Matrix2x2()
        a.setData(0, 0, 1)
        a.setData(1, 1, 1)
        return a

    @staticmethod
    def rotation(angle: float):
        c: float = math.cos(angle)
        s: float = math.sin(angle)
        a = Matrix2x2()
        a.setData(0, 0, c)
        a.setData(1, 0, -s)
        a.setData(0, 1, s)
        a.setData(1, 1, c)
        return a

    def getRow(self, index: int):
        return Vector2(self.__data[0][index], self.__data[1][index])

    def getCol(self, index: int):
        return Vector2(self.__data[index][0], self.__data[index][1])

    def setRow(self, index: int, value):
        self.__data[0][index] = float(value[0])
        self.__data[1][index] = float(value[1])
        return self

    def setCol(self, index: int, value):
        self.__data[index][0] = float(value[0])
        self.__data[index][1] = float(value[1])
        return self

    def getData(self, colIndex: int, rowIndex: int):
        return self.__data[colIndex][rowIndex]

    def setData(self, colIndex: int, rowIndex: int, value: float):
        self.__data[colIndex][rowIndex] = float(value)
        return self

    def __mul__(self, v):
        if isinstance(v, Vector2):  # mnożenie macierzy przez wektora
            return Vector2(self.getRow(0) * v, self.getRow(1) * v)
        if isinstance(v, Matrix2x2):  # mnożenie macierzy przez macierz
            return Matrix2x2(UpRow=[self.getRow(0) * v.getCol(0), self.getRow(0) * v.getCol(1)],
                             DownRow=[self.getRow(1) * v.getCol(0), self.getRow(1) * v.getCol(1)])
        if isinstance(v, int) or isinstance(v, float):  # mnożenie macierzy przez skalar
            return Matrix2x2(UpRow=self.getRow(0) * v, DownRow=self.getRow(1) * v)
        return None

    def copy(self):
        return Matrix2x2(UpRow=self.getRow(0), DownRow=self.getRow(1))

    def det(self):
        return self.__data[0][0] * self.__data[1][1] - self.__data[1][0] * self.__data[0][1]
