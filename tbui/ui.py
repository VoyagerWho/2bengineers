from tbutils.builder import Builder
import tbutils.math2d as m2d
from vpython import *
import tbneuralnetwork.nueralnetworkfunctions as nnf

canvasWidth = 1600
canvasHeight = 480
pickingPoints = True
numberOfStaticPoints = 0
staticPoints = []
generatedCurves = []

def stopPickingPoints(b):
    global pickingPoints
    pickingPoints = False
    if pickingPoints:
        b.text = "Click here if you already picked points"
    else:
        b.text = "Points picked, making calculations"

def deletePoints(b):
    global staticPoints
    print("staticPoints")
    print(staticPoints)
    numberOfSphere = len(staticPoints)
    print("numberOfSphere")
    print(numberOfSphere)
    for i in range(0, numberOfSphere, 1):
        staticPoints[0].visible = False
        del staticPoints[0]

    print("after delete: ")
    print(staticPoints)

def deleteCurves():
    global generatedCurves
    numberOfCurves = len(generatedCurves)
    for i in range(0, numberOfCurves, 1):
        generatedCurves[0].visible = False
        del generatedCurves[0]
    # print("after delete: ")
    # print(generatedCurves)

def ui():
    global pickingPoints, staticPoints

    point1 = None
    point2 = None
    addedStaticPoints = []

    scene = canvas(width=canvasWidth, height=canvasHeight,
                   center=vector(canvasWidth / 2.0, canvasHeight / 2.0, 0), background=color.white,
                   resizable=False)
    button(text="Click here if you already picked points", bind=stopPickingPoints)
    button(text="Delete points", bind=deletePoints)

    title = "Click and drag the mouse to insert static point."
    scene.title = title

    b = box(pos=vector(0, 0, 0), color=color.green)
    b.visible = False

    drag = True
    s = None

    def grab(evt):
        if pickingPoints:
            nonlocal s, drag
            scene.title = 'Drag the point'
            drag = True
            s = sphere(pos=evt.pos, radius=2, color=color.red)
            staticPoints.append(s)
            print("grab ")
            print(evt.pos)
            print(evt.pos.x)


    def move(evt):
        if pickingPoints:
            nonlocal drag
            if drag:
                s.pos = scene.mouse.pos  # evt.pos
                print("move")
                print(s.pos.x)

    def drop(evt):
        if pickingPoints:
            nonlocal drag
            scene.title = title
            s.color = color.cyan
            drag = False
            s.pos = scene.mouse.pos
            print("DROP")
            print(s.pos.x)
            print(evt.pos.x)

    def pickLines(bridge):
        l = []
        for connection in bridge.connections:
            if not connection.broken:
                l.append((connection.jointA.position.x, connection.jointA.position.y,
                          connection.jointB.position.x, connection.jointB.position.y,
                          connection.getStrain()))
        return l

    def showBridge(bridge, l):
        for ln in l:
            list_of_points = []
            list_of_points.append(vector(ln[0], ln[1], 0))
            list_of_points.append(vector(ln[2], ln[3], 0))
            c = curve(pos=list_of_points, color=color.red)
            generatedCurves.append(c)

    scene.bind('mousedown', grab)
    scene.bind('mousemove', move)
    scene.bind('mouseup', drop)

    while pickingPoints:
        rate(10)

    print(staticPoints)
    if len(staticPoints) >= 1:
        point1 = m2d.Vector2(staticPoints[0].pos.x, staticPoints[0].pos.y)
    if len(staticPoints) >= 2:
        point2 = m2d.Vector2(staticPoints[1].pos.x, staticPoints[1].pos.y)
    if len(staticPoints) > 2:
        it = 0
        while it < len(staticPoints)-2:
            addedStaticPoints.append(m2d.Vector2(staticPoints[it].pos.x, staticPoints[it].pos.y))
            it = it+1

    numberOfExtraStaticPoints = len(staticPoints)-2
    pickingPoints = False

    print("pickingPoints")
    print(pickingPoints)

    materials = Builder.createMaterialsList()
    print("Arguments passed to the function: ")
    print(point1)
    print(point2)

    if len(staticPoints) == 2:
        print("inside else")
        bridge = Builder.buildInitial(materials, point1, point2)
        print("after1")
    elif len(staticPoints) > 2:
        print("inside else")
        print(numberOfExtraStaticPoints)
        print(addedStaticPoints)
        print(addedStaticPoints[0].x)
        print(addedStaticPoints[0].y)
        bridge = Builder.buildInitial(materials, point1, point2, numberOfExtraStaticPoints, addedStaticPoints)
        print("after2")

    l = pickLines(bridge)

    # p = list(bridge.points)

    scene.center = vector(canvasWidth / 2.0, canvasHeight / 2.0, 0)
    scene.camera.axis.z = 900
    showBridge(bridge, l)

    # below - functionality demo
    sleep(2)
    print("changeConnectionMaterial")
    nnf.changeConnectionMaterial(bridge, 10, 0.1)
    l = pickLines(bridge)
    deleteCurves()
    showBridge(bridge, l)

    sleep(1)
    print("removeConnection")
    nnf.removeConnection(bridge, 7, 0.3)
    l = pickLines(bridge)
    deleteCurves()
    showBridge(bridge, l)

    sleep(1)
    print("removeJoint")
    nnf.removeJoint(bridge, 8, 0.3, 0.6)
    l = pickLines(bridge)
    deleteCurves()
    showBridge(bridge, l)

    sleep(1)
    print("removeJoint")
    nnf.removeJoint(bridge, 4, 0.3, 0.6)
    l = pickLines(bridge)
    deleteCurves()
    showBridge(bridge, l)

    sleep(1)
    print("addJoint")
    nnf.addJoint(bridge, 10, 0.5, 0.1)
    l = pickLines(bridge)
    deleteCurves()
    showBridge(bridge, l)

    sleep(1)
    print("addJoint")
    nnf.addJoint(bridge, 12, 0.5, 0.1)
    l = pickLines(bridge)
    deleteCurves()
    showBridge(bridge, l)

    sleep(1)
    print("moveJoint")
    nnf.moveJoint(bridge, 6, 0.3, 0.6)
    l = pickLines(bridge)
    deleteCurves()
    showBridge(bridge, l)

    sleep(1)
    print("moveJoint")
    nnf.moveJoint(bridge, 7, 0.3, 0.6)
    l = pickLines(bridge)
    deleteCurves()
    showBridge(bridge, l)

    sleep(1)
    print("moveJoint")
    nnf.moveJoint(bridge, 10, 0.3, 0.6)
    l = pickLines(bridge)
    deleteCurves()
    showBridge(bridge, l)

    sleep(1)
    print("addConnection")
    nnf.addConnection(bridge, 3, 0.9, 0.3)
    nnf.addConnection(bridge, 2, 0.9, 0.3)
    nnf.addConnection(bridge, 1, 0.9, 0.3)
    nnf.addConnection(bridge, 4, 0.9, 0.3)
    l = pickLines(bridge)
    deleteCurves()
    showBridge(bridge, l)

    print("END")
