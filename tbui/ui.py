import threading

from tbneuralnetwork import ai
from tbutils.builder import Builder
import tbutils.math2d as m2d
from vpython import *
import os

canvasWidth = 1600
canvasHeight = 480
picking_points = True
numberOfStaticPoints = 0
staticPoints = []
generatedCurves = []


def stop_picking_points(b):
    if len(staticPoints) >= 2:
        global picking_points
        picking_points = False
        if picking_points:
            b.text = "Build initial (pick at least 2 points)"
        else:
            b.text = "Points picked, making calculations"


def delete_points(b):
    global staticPoints
    print("staticPoints")
    print(staticPoints)
    number_of_sphere = len(staticPoints)
    print("number_of_sphere")
    print(number_of_sphere)
    for i in range(0, number_of_sphere, 1):
        staticPoints[0].visible = False
        del staticPoints[0]

    print("after delete: ")
    print(staticPoints)


def delete_curves():
    global generatedCurves
    number_of_curves = len(generatedCurves)
    for i in range(0, number_of_curves, 1):
        generatedCurves[0].visible = False
        del generatedCurves[0]
    # print("after delete: ")
    # print(generatedCurves)


def async_crazy_stuff():
    chamber2 = ai.BridgeEvolution((os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tbneuralnetwork'))))
    chamber2.load()
    chamber2.upgrade("what_should_I_type_in_here", 200)


def ui():
    t1 = threading.Thread(target=async_crazy_stuff)
    global picking_points, staticPoints

    point1 = None
    point2 = None
    added_static_points = []

    scene = canvas(width=canvasWidth, height=canvasHeight,
                   center=vector(canvasWidth / 2.0, canvasHeight / 2.0, 0), background=color.white,
                   resizable=False)
    materials = Builder.createMaterialsList()
    button(text="Build initial (pick at least 2 points)", bind=stop_picking_points)
    button(text="Delete points", bind=delete_points)

    title = "Click and drag the mouse to insert static point."
    scene.title = title

    b = box(pos=vector(0, 0, 0), color=color.green)
    b.visible = False

    drag = True
    s = None

    def grab(evt):
        if picking_points:
            nonlocal s, drag
            scene.title = 'Drag the point'
            drag = True
            s = sphere(pos=evt.pos, radius=2, color=color.red)
            staticPoints.append(s)
            print("grab ")
            print(evt.pos)
            print(evt.pos.x)

    def move(evt):
        if picking_points:
            nonlocal drag
            if drag:
                s.pos = scene.mouse.pos  # evt.pos
                print("move")
                print(s.pos.x)

    def drop(evt):
        if picking_points:
            nonlocal drag
            scene.title = title
            s.color = color.cyan
            drag = False
            s.pos = scene.mouse.pos
            print("DROP")
            print(s.pos.x)
            print(evt.pos.x)

    def pick_lines(bridge):
        l = []
        for connection in bridge.connections:
            if not connection.broken:
                l.append((connection.jointA.position.x, connection.jointA.position.y,
                          connection.jointB.position.x, connection.jointB.position.y,
                          connection.getStrain()))
        return l

    def show_bridge(bridge, l):
        print("SHOW BRIDGE")
        for ln in l:
            list_of_points = []
            list_of_points.append(vector(ln[0], ln[1], 0))
            list_of_points.append(vector(ln[2], ln[3], 0))
            c = curve(pos=list_of_points, color=color.red)
            generatedCurves.append(c)

    scene.bind('mousedown', grab)
    scene.bind('mousemove', move)
    scene.bind('mouseup', drop)

    while picking_points:
        rate(10)

    print(staticPoints)
    if len(staticPoints) >= 1:
        point1 = m2d.Vector2(staticPoints[0].pos.x, staticPoints[0].pos.y)
    if len(staticPoints) >= 2:
        point2 = m2d.Vector2(staticPoints[1].pos.x, staticPoints[1].pos.y)
    if len(staticPoints) > 2:
        it = 0
        while it < len(staticPoints)-2:
            added_static_points.append(m2d.Vector2(staticPoints[it].pos.x, staticPoints[it].pos.y))
            it = it+1

    number_of_extra_static_points = len(staticPoints)-2

    print("Arguments passed to the function: ")
    print(point1)
    print(point2)

    if len(staticPoints) == 2:
        bridge = Builder.buildInitial(materials, point1, point2)
    elif len(staticPoints) > 2:
        print(number_of_extra_static_points)
        print(added_static_points)
        print(added_static_points[0].x)
        print(added_static_points[0].y)
        bridge = Builder.buildInitial(materials, point1, point2, number_of_extra_static_points, added_static_points)

    picked_lines = pick_lines(bridge)

    scene.center = vector(canvasWidth / 2.0, canvasHeight / 2.0, 0)
    scene.camera.axis.z = 900
    show_bridge(bridge, picked_lines)
    ai.BridgeEvolution.bridge = bridge

    ai.BridgeEvolution.upgrade_still_running = True
    t1.start()
    number = 0

    while ai.BridgeEvolution.upgrade_still_running:
        picked_lines = pick_lines(bridge)
        delete_curves()
        show_bridge(ai.BridgeEvolution.bridge, picked_lines)
        number = number+1
        rate(1)

    print("END")
