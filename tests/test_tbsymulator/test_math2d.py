import tbutils.math2d as m2
import math


def test_ConstructorVector2():
    v = m2.Vector2(3, 4)
    assert v.x == 3
    assert v.y == 4

    v = m2.Vector2([7, 8])
    assert v.x == 7
    assert v.y == 8

    v2 = m2.Vector2(v)
    assert v2.x == 7
    assert v2.y == 8

    try:
        v = m2.Vector2("asd")
        assert False
    except:
        assert True

    v = m2.Vector2(0, 0)
    assert v.x == 0
    assert v.y == 0

    assert str(v) == "[0.0; 0.0]"


def test_AddVector2():
    v1 = m2.Vector2(1, 2)
    v2 = m2.Vector2(3, 7)
    v = v1 + v2
    assert v.x == 4
    assert v.y == 9

    v = v1 + 2
    assert v.x == 3
    assert v.y == 4

    v = v1 + [3, 7]
    assert v.x == 4
    assert v.y == 9


def test_SubVector2():
    v1 = m2.Vector2(1, 2)
    v2 = m2.Vector2(3, 7)
    v = v1 - v2
    assert v.x == -2
    assert v.y == -5

    v = v1 - 2
    assert v.x == -1
    assert v.y == 0

    v = v1 - [3, 7]
    assert v.x == -2
    assert v.y == -5


def test_MulVector2():
    v1 = m2.Vector2(1, 2)
    v2 = m2.Vector2(3, 7)
    v = v1 * v2
    assert v == 17

    v = v1 * 2
    assert v.x == 2
    assert v.y == 4

    v = v1 * [3, 7]
    assert v == 17


def test_DivVector2():
    v1 = m2.Vector2(1, 2)
    v2 = v1 / 2
    assert v2.x == 0.5
    assert v2.y == 1


def test_GetItemVector2():
    v = m2.Vector2(1, 2)
    assert v.x == v[0]
    assert v.y == v[1]


def test_IAddVector2():
    v1 = m2.Vector2(1, 2)
    v2 = m2.Vector2(3, 7)
    v = v1.copy()
    v += v2
    assert v.x == 4
    assert v.y == 9

    v = v1.copy()
    v += 2
    assert v.x == 3
    assert v.y == 4

    v = v1.copy()
    v += [3, 7]
    assert v.x == 4
    assert v.y == 9

    assert v1.x == 1
    assert v1.y == 2


def test_ISubVector2():
    v1 = m2.Vector2(1, 2)
    v2 = m2.Vector2(3, 7)
    v = v1.copy()
    v -= v2
    assert v.x == -2
    assert v.y == -5

    v = v1.copy()
    v -= 2
    assert v.x == -1
    assert v.y == 0

    v = v1.copy()
    v -= [3, 7]
    assert v.x == -2
    assert v.y == -5

    assert v1.x == 1
    assert v1.y == 2


def test_LengthVector2():
    v = m2.Vector2(3, 4)
    assert v.length() == 5


def test_NormalVector2():
    v = m2.Vector2(3, 4)
    assert v.normal().length() == 1
    assert v.x == 3
    assert v.y == 4

    v = m2.Vector2(0, 0)
    assert v.normal().length() == 0


def test_AngleVector2():
    v = m2.Vector2(3, 4)
    r = v.length()
    a = v.angle()
    v2 = m2.Vector2(r * math.cos(a), r * math.sin(a))
    assert (v - v2).length() < 1e-12


def test_ConstructorMatrix2x2():
    m = m2.Matrix2x2()  # check if no error

    m = m2.Matrix2x2([1, 2], [3, 4])
    assert m.getData(0, 0) == 1 and m.getData(1, 0) == 2 and m.getData(0, 1) == 3 and m.getData(1, 1) == 4

    m = m2.Matrix2x2(UpRow=[1, 2], DownRow=[3, 4])
    assert m.getData(0, 0) == 1 and m.getData(1, 0) == 2 and m.getData(0, 1) == 3 and m.getData(1, 1) == 4

    m = m2.Matrix2x2(LeftCol=[1, 2], RightCol=[3, 4])
    assert m.getData(0, 0) == 1 and m.getData(1, 0) == 3 and m.getData(0, 1) == 2 and m.getData(1, 1) == 4

    m = m2.Matrix2x2.identity()
    assert m.getData(0, 0) == 1 and m.getData(1, 0) == 0 and m.getData(0, 1) == 0 and m.getData(1, 1) == 1


def test_SetDataMatrix2x2():
    m = m2.Matrix2x2.identity()
    assert m.getData(0, 0) == 1 and m.getData(1, 0) == 0 and m.getData(0, 1) == 0 and m.getData(1, 1) == 1
    m.setData(0, 0, 3)
    assert m.getData(0, 0) == 3 and m.getData(1, 0) == 0 and m.getData(0, 1) == 0 and m.getData(1, 1) == 1


def test_GetRowColMatrix2x2():
    m = m2.Matrix2x2([1, 2], [3, 4])
    v = m.getRow(0)
    assert v.x == 1 and v.y == 2
    v = m.getRow(1)
    assert v.x == 3 and v.y == 4
    v = m.getCol(0)
    assert v.x == 1 and v.y == 3
    v = m.getCol(1)
    assert v.x == 2 and v.y == 4


def test_SetRowColMatrix2x2():
    m = m2.Matrix2x2()
    m.setRow(0, [1, 2])
    v = m.getRow(0)
    assert v.x == 1 and v.y == 2
    v = m.getRow(1)
    assert v.x == 0 and v.y == 0
    m.setRow(1, [3, 4])
    v = m.getRow(1)
    assert v.x == 3 and v.y == 4

    m = m2.Matrix2x2()
    m.setCol(0, [1, 3])
    v = m.getCol(0)
    assert v.x == 1 and v.y == 3
    v = m.getCol(1)
    assert v.x == 0 and v.y == 0

    m.setCol(1, [2, 4])
    v = m.getCol(0)
    assert v.x == 1 and v.y == 3
    v = m.getCol(1)
    assert v.x == 2 and v.y == 4


def test_MulMatrix2x2():
    m = m2.Matrix2x2([1, 2], [3, 4])
    v = m2.Vector2(5, 6)

    r = m * v
    assert r.x == 17 and r.y == 39

    r = m * m
    assert r.getData(0, 0) == 7 and r.getData(1, 0) == 10 and r.getData(0, 1) == 15 and r.getData(1, 1) == 22

    r = m * 5
    assert r.getData(0, 0) == 5 and r.getData(1, 0) == 10 and r.getData(0, 1) == 15 and r.getData(1, 1) == 20


def test_CopyMatrix2x2():
    m = m2.Matrix2x2([1, 2], [3, 4])
    c = m.copy()
    c.identity()
    assert m.getData(0, 0) == 1 and m.getData(1, 0) == 2 and m.getData(0, 1) == 3 and m.getData(1, 1) == 4
    assert c.getData(0, 0) == 1 and c.getData(1, 0) == 0 and c.getData(0, 1) == 0 and c.getData(1, 1) == 1


def test_DetMatrix2x2():
    assert m2.Matrix2x2([1, 2], [3, 4]).det() == -2
