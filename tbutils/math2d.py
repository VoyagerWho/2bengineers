from __future__ import annotations
from typing import List
import math


class Vector2:
    """
    Utility class representing vector 2D
    """
    def __init__(self, x: float or int or Vector2 or List = 0.0, y: float or int= 0.0):
        if (isinstance(x, float) or isinstance(x, int)) and (
                isinstance(y, float) or isinstance(y, int)):
            self.x: float = float(x)
            self.y: float = float(y)
        elif isinstance(x, Vector2) or isinstance(x, list):
            self.x = float(x[0])
            self.y = float(x[1])
        else:
            raise Exception("Invalid constructor arguments", type(x), type(y))

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
        return self.copy()

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

    def __imul__(self, v):
        if isinstance(v, int) or isinstance(v, float):
            self.x *= v
            self.y *= v  
            return self
        return None
    
    def __itruediv__(self, v):
        if isinstance(v, int) or isinstance(v, float):
            self.x /= v
            self.y /= v  
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
