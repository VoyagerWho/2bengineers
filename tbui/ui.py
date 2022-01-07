import threading

from tbneuralnetwork import ai
from tbsymulator import mechanics
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
static_load = 2000
show_natural = True


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
    number_of_sphere = len(staticPoints)
    for i in range(0, number_of_sphere, 1):
        staticPoints[0].visible = False
        del staticPoints[0]


def delete_curves():
    global generatedCurves
    number_of_curves = len(generatedCurves)
    for i in range(0, number_of_curves, 1):
        generatedCurves[0].visible = False
        del generatedCurves[0]


def async_crazy_stuff():
    chamber2 = ai.BridgeEvolution((os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tbneuralnetwork'))))
    chamber2.load()
    chamber2.upgrade("", 1)


def add_static_load(wi):
    global static_load
    print("STATIC LOAD: %d", static_load)
    static_load = wi.text


def ui():
    t1 = threading.Thread(target=async_crazy_stuff)
    global picking_points, staticPoints

    bridge = None
    point1 = None
    point2 = None
    added_static_points = []

    def change_way_to_present_bridge(b):
        global show_natural
        if b.checked:
            print("CHANGE WAY TO PRESENT BRIDGE!")
            show_natural = b.natural
        for i in range(len(radio_buttons)):
            if i != b.i:
                radio_buttons[i].checked = False

    scene = canvas(width=canvasWidth, height=canvasHeight,
                   center=vector(canvasWidth / 2.0, canvasHeight / 2.0, 0), background=color.white,
                   resizable=False)
    materials = Builder.createMaterialsList()
    wtext(text="\n\nMenu: \n\n")
    button(text="Build initial (pick at least 2 points)", bind=stop_picking_points)
    button(text="Delete points", bind=delete_points)
    wtext(text="\n\nStatic load: ")
    winput(text="", bind=add_static_load, width=300)
    wtext(text=" kg per meter\n\n")
    radio_strain = radio(bind=change_way_to_present_bridge, text="Show strain", i=0, natural=False)
    radio_natural = radio(bind=change_way_to_present_bridge, text="Show used materials\n\n", i=1, natural=True)
    radio_buttons = [radio_strain, radio_natural]
    wtext_status = wtext(text="\n\nStatus: picking points ")
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

    def move(evt):
        if picking_points:
            nonlocal drag
            if drag:
                s.pos = scene.mouse.pos  # evt.pos

    def drop(evt):
        if picking_points:
            nonlocal drag
            scene.title = title
            s.color = color.cyan
            drag = False
            s.pos = scene.mouse.pos

    def pick_lines(bridge):
        lines = []
        for connection in bridge.connections:
            if not connection.broken:
                lines.append((connection.jointA.position.x, connection.jointA.position.y,
                              connection.jointB.position.x, connection.jointB.position.y,
                              connection.getStrain(), connection.material))
        return lines

    def pick_points(bridge):
        points = []
        for point in bridge.points:
            print(point)
            points.append(point)
        return points

    def show_bridge(bridge):
        picked_lines = pick_lines(bridge)
        delete_curves()
        print("SHOW BRIDGE")
        for ln in picked_lines:
            list_of_points = []
            list_of_points.append(vector(ln[0], ln[1], 0))
            list_of_points.append(vector(ln[2], ln[3], 0))
            if show_natural:
                param = vec(0, 1, 0)
                rad = 2
                if ln[5].name == "Asphalt Road":
                    param = vec(0.2, 0.2, 0.2)
                    rad = 3
                elif ln[5].name == "Steel Beam":
                    param = vec(0.55, 0.55, 0.55)
                    rad = 1
                elif ln[5].name == "Wooden Beam":
                    param = vec(0.6, 0.25, 0.02)
                    rad = 2

                c = curve(pos=list_of_points, color=param, radius=rad)
                generatedCurves.append(c)
            else:
                print("HERE: %5.2f %5.2f" % (ln[4], 1.0 - ln[4]))
                print(list_of_points)
                c = curve(pos=list_of_points, color=vec(ln[4], 1.0 - ln[4], ln[4]), radius=1.5)
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
        while it < len(staticPoints) - 2:
            added_static_points.append(m2d.Vector2(staticPoints[it].pos.x, staticPoints[it].pos.y))
            it = it + 1

    number_of_extra_static_points = len(staticPoints) - 2

    if len(staticPoints) == 2:
        bridge = Builder.buildInitial(materials, point1, point2)
        bridge.roadStrains = static_load
    elif len(staticPoints) > 2:
        bridge = Builder.buildInitial(materials, point1, point2, number_of_extra_static_points, added_static_points)
        bridge.roadStrains = static_load

    print("%f %f %f %f %f %f", staticPoints[0].pos.x, staticPoints[0].pos.y, staticPoints[1].pos.x,
          staticPoints[1].pos.y)
    print(point1)

    length_x = abs(staticPoints[1].pos.x - staticPoints[0].pos.x)
    length_y = abs(staticPoints[1].pos.y - staticPoints[0].pos.y)

    posX = 0
    posY = 0
    if staticPoints[0].pos.x < staticPoints[1].pos.x:
        posX = staticPoints[0].pos.x
    else:
        posX = staticPoints[1].pos.x

    if staticPoints[0].pos.y < staticPoints[1].pos.y:
        posY = staticPoints[0].pos.y
    else:
        posY = staticPoints[1].pos.y

    position_x = length_x / 2 + posX
    position_y = length_y / 2 + posY

    # terrain_shape = shapes.points(
    #     pos=[[length_x, length_y], [length_x, length_y + 200], [0, length_y + 200], [0, 0]])

    depth = 400

    terrain_shape = shapes.points(
        pos=[[0, 0], [0, length_y + 200], [length_x, length_y + 200], [length_x, length_y], [length_x + 1000, length_y],
             [length_x + 1000, length_y + depth], [-1000, length_y + depth], [-1000, 0]])

    terrain_path = [vec(position_x, position_y, 0),
                    vec(position_x, position_y, depth/2)]

    terrain = extrusion(path=terrain_path, shape=terrain_shape)

    sleep(1)
    terrain.rotate(angle=pi, axis=vec(position_x, 0, 0))

    if staticPoints[0].pos.y > staticPoints[1].pos.y and staticPoints[0].pos.x < staticPoints[1].pos.x:
        terrain.rotate(angle=pi, axis=vec(0, position_y, 0))

    # terrain.rotate(angle=pi, axis=vec(0, position_y, 0))
    # terrain.rotate(angle=pi, axis=vec(position_x, 0, 0))
    # terrain.rotate(angle=pi, axis=vec(0, position_y, 0))

    terrain.pos = vec(position_x, position_y - depth/2, 0)
    terrain.color = color.red

    scene.center = vector(canvasWidth / 2.0, canvasHeight / 2.0, 0)
    scene.camera.axis.z = 900
    pick_points(bridge)
    show_bridge(bridge)
    ai.BridgeEvolution.bridge = bridge
    ai.BridgeEvolution.upgrade_still_running = True

    t1.start()
    wtext_status.text = "Status: simulation in progres."

    while ai.BridgeEvolution.upgrade_still_running:
        wtext_status.text = "Status: simulation in progres. Already done %d simulations" % mechanics.it
        show_bridge(ai.BridgeEvolution.bridge)
        rate(5)

    wtext_status.text = "Status: simulation ended"
    print("END")
