from tbutils.builder import Builder
import tbutils.math2d as m2d
from vpython import *

running = False
bridgeWidth = 1600
bridgeHeight = 480
pickingPoints = True


def Run(b):
    global pickingPoints
    pickingPoints = False
    if pickingPoints:
        b.text = "Click here if you already picked points"
    else:
        b.text = "Points picked, making calculations"


def ui():
    global pickingPoints

    point1 = m2d.Vector2(0.0, 0.0)
    point2 = m2d.Vector2(10.0, 0.0)
    addedStaticPoints = []

    scene = canvas(width=bridgeWidth, height=bridgeHeight,
                   center=vector(bridgeWidth / 2.0, bridgeHeight / 2.0, 0), background=color.white,
                   resizable=False)
    button(text="Click here if you already picked points", bind=Run)

    title = "Click and drag the mouse in the 3D canvas to insert and drag a small sphere."
    scene.title = title
    # scene.range = 3
    b = box(pos=vector(0, 0, 0), color=color.green)

    iterator = 0;
    numberOfExtraStaticPoints = 0;

    drag = True
    s = None

    def grab(evt):
        if pickingPoints:
            nonlocal s, drag, iterator
            scene.title = 'Drag the sphere.'
            drag = True
            s = sphere(pos=evt.pos, radius=2, color=color.red)
            print("grab ")
            print(evt.pos)
            print(evt.pos.x)
            iterator = iterator + 1

    def move(evt):
        if pickingPoints:
            nonlocal drag, iterator
            if drag:
                s.pos = scene.mouse.pos  # evt.pos
                print("move")
                print(s.pos.x)

    def drop(evt):
        if pickingPoints:
            nonlocal drag, iterator, point1, point2, addedStaticPoints, numberOfExtraStaticPoints
            scene.title = title
            s.color = color.cyan
            drag = False
            s.pos = scene.mouse.pos
            print("DROP")
            print(s.pos.x)
            print(evt.pos.x)
            if iterator == 1:
                nonlocal point1
                point1 = m2d.Vector2(s.pos.x, s.pos.y)
            elif iterator == 2:
                nonlocal point2
                point2 = m2d.Vector2(s.pos.x, s.pos.y)
            elif iterator > 2:
                nonlocal addedStaticPoints, numberOfExtraStaticPoints
                addedStaticPoints.append(m2d.Vector2(s.pos.x, s.pos.y))
                numberOfExtraStaticPoints = numberOfExtraStaticPoints + 1

    scene.bind('mousedown', grab)
    scene.bind('mousemove', move)
    scene.bind('mouseup', drop)

    while pickingPoints and (iterator < 5 or drag):
        print("Iterator ")
        print(iterator)
        rate(10)

    pickingPoints = False

    print("pickingPoints")
    print(pickingPoints)

    # [l, p] = bridge.getModelForRender((bridgeWidth, bridgeHeight))
    materials = Builder.createMaterialsList()
    print("Arguments passed to the function: ")
    print(point1)
    print(point2)
    print(numberOfExtraStaticPoints)
    print(addedStaticPoints)

    if numberOfExtraStaticPoints == 0:
        bridge = Builder.buildInitial(materials, point1, point2)
        print("after1")
    else:
        bridge = Builder.buildInitial(materials, point1, point2, numberOfExtraStaticPoints, addedStaticPoints)
        print("after2")

    l = []
    for connection in bridge.connections:
        if not connection.broken:
            l.append((connection.jointA.position.x, connection.jointA.position.y,
                      connection.jointB.position.x, connection.jointB.position.y,
                      connection.getStrain()))
    print("Result: ")
    print(l)

    p = list(bridge.points)

    # print(scene.camera.pos)
    # print(scene.camera.axis)
    # print(scene.center)

    scene.center = vector(bridgeWidth / 2.0, bridgeHeight / 2.0, 0)
    scene.camera.axis.z = 900

    # print(scene.camera.pos)
    # print(scene.camera.axis)
    # print(scene.center)

    for ln in l:
        list_of_points = []
        list_of_points.append(vector(ln[0], ln[1], 0))
        list_of_points.append(vector(ln[2], ln[3], 0))
        curve(pos=list_of_points, color=color.red)

    print("END")
