import ctypes
import threading
import time

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
# for double bridge
generatedCurves1 = []
generatedCurves2 = []
generatedRoad = []
generatedPoints = []
generatedTerrain = []
static_load = 2000
show_natural = True
run_showing_bridge_next_steps = True
wait_for_click = False


class thread_with_exception(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.some_number = 0

    def run(self):
        # target function of the thread class
        try:
            chamber2 = ai.BridgeEvolution(
                (os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tbneuralnetwork'))))
            chamber2.load()
            chamber2.upgrade("", 1)

        finally:
            print('ended')

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


def stop_picking_points(b):
    if len(staticPoints) >= 2:
        global picking_points
        picking_points = False
        if picking_points:
            b.text = "Build initial (pick at least 2 points)"
        else:
            b.text = "Points picked, making calculations"


def delete_points():
    global staticPoints
    number_of_sphere = len(staticPoints)
    for i in range(0, number_of_sphere, 1):
        staticPoints[0].visible = False
        del staticPoints[0]


def delete_curves_1():
    global generatedCurves1, generatedPoints
    number_of_curves = len(generatedCurves1)
    number_of_points = len(generatedPoints)
    for i in range(0, number_of_curves, 1):
        generatedCurves1[0].visible = False
        del generatedCurves1[0]

    # for i in range(0, number_of_points, 1):
    #     generatedPoints[0].visible = False
    #     del generatedPoints[0]


def delete_curves_2():
    global generatedCurves2, generatedPoints
    number_of_curves = len(generatedCurves2)
    number_of_points = len(generatedPoints)
    for i in range(0, number_of_curves, 1):
        generatedCurves2[0].visible = False
        del generatedCurves2[0]

    # for i in range(0, number_of_points, 1):
    #     generatedPoints[0].visible = False
    #     del generatedPoints[0]


def delete_road():
    global generatedRoad
    number_of_boxes = len(generatedRoad)
    for i in range(0, number_of_boxes, 1):
        generatedRoad[0].visible = False
        del generatedRoad[0]


def delete_terrain():
    global generatedTerrain
    number_of_stuff = len(generatedTerrain)
    for i in range(0, number_of_stuff, 1):
        generatedTerrain[0].visible = False
        del generatedTerrain[0]

def async_crazy_stuff():
    chamber2 = ai.BridgeEvolution((os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tbneuralnetwork'))))
    chamber2.load()
    chamber2.upgrade("", 1)


def add_static_load(wi):
    global static_load

    print("STATIC LOAD (old): %d", static_load)
    try:
        static_load = float(wi.text)
    except:
        static_load = 0.0
    print("STATIC LOAD (new): %d", static_load)

def clear_my_scene():
    global run_showing_bridge_next_steps
    run_showing_bridge_next_steps = False
    delete_road()
    delete_curves_1()
    delete_curves_2()
    delete_points()
    delete_terrain()


def ui():
    # t1 = threading.Thread(target=async_crazy_stuff)
    first_start = True
    t1 = None
    global picking_points, staticPoints, wait_for_click

    added_static_points = []

    def change_way_to_present_bridge(b):
        global show_natural
        if b.checked:
            print("CHANGE WAY TO PRESENT BRIDGE!")
            show_natural = b.natural
        for i in range(len(radio_buttons)):
            if i != b.i:
                radio_buttons[i].checked = False

    def restart_this():
        global picking_points, wait_for_click, run_showing_bridge_next_steps
        nonlocal t1
        run_showing_bridge_next_steps = False
        wait_for_click = True

        print("RESTART_THIS")
        if t1 is not None:
            print("INSIDE")
            t1.raise_exception()
            t1.join()

        time.sleep(1)
        picking_points = True
        start_everything()


    scene = canvas(width=canvasWidth, height=canvasHeight,
                   center=vector(canvasWidth / 2.0, canvasHeight / 2.0, 0), background=vec(0.9, 0.9, 1),
                   resizable=False)
    materials = Builder.createMaterialsList()
    wtext(text="\n\nMenu: \n\n")
    button(text="Build initial (pick at least 2 points)", bind=stop_picking_points)
    button(text="Delete points", bind=delete_points)
    button(text="RESTART", bind=restart_this)
    wtext(text="\n\nStatic load: ")
    winput(text="", bind=add_static_load, width=300)
    wtext(text=" kg per meter\n\n")
    radio_strain = radio(bind=change_way_to_present_bridge, text="Show strain", i=0, natural=False)
    radio_natural = radio(bind=change_way_to_present_bridge, text="Show used materials\n\n", i=1, natural=True)
    radio_buttons = [radio_strain, radio_natural]
    wtext_status = wtext(text="\n\nStatus: picking points ")
    wtext_progress = wtext(text="\n\nProgress: -")
    title = "Click and drag the mouse to insert static point."
    scene.title = title

    b = box(pos=vector(0, 0, 0), color=color.green)
    b.visible = False

    drag = True
    s = None
    print("scene axis: ")
    print(scene.axis)

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
            points.append(point.copy())
        return points

    def show_bridge(bridge, position_z, version):
        picked_lines = pick_lines(bridge)
        # picked_points = pick_points(bridge)
        if version == 1:
            delete_curves_1()
            delete_road()
        else:
            delete_curves_2()

        print("SHOW BRIDGE")
        for ln in picked_lines:
            list_of_points = []
            list_of_points.append(vector(ln[0], ln[1], position_z))
            list_of_points.append(vector(ln[2], ln[3], position_z))
            if show_natural:
                param = vec(0, 1, 0)
                rad = 2
                if ln[5].name == "Asphalt Road":
                    param = vec(0.2, 0.2, 0.2)
                    rad = 3
                    if version == 1:
                        if ln[0] < ln[2]:
                            road_posX = ln[0]
                        else:
                            road_posX = ln[2]

                        if ln[1] < ln[3]:
                            road_posY = ln[1]
                        else:
                            road_posY = ln[3]

                        road_length_x = ln[2] - ln[0]
                        road_length_y = ln[3] - ln[1]
                        road_position_x = abs(road_length_x) / 2 + road_posX
                        road_position_y = abs(road_length_y) / 2 + road_posY
                        road_box_width = sqrt(road_length_x * road_length_x + road_length_y * road_length_y)
                        road = box(pos=vec(road_position_x, road_position_y, 0), length=100, height=2,
                                   width=road_box_width, axis=vec(road_length_x, road_length_y, 0), color=param)
                        generatedRoad.append(road)

                elif ln[5].name == "Steel Beam":
                    param = vec(0.55, 0.55, 0.55)
                    rad = 1
                elif ln[5].name == "Wooden Beam":
                    param = vec(0.6, 0.25, 0.02)
                    rad = 2

                c = curve(pos=list_of_points, color=param, radius=rad)
                if version == 1:
                    generatedCurves1.append(c)
                else:
                    generatedCurves2.append(c)

            else:
                c = curve(pos=list_of_points, color=vec(ln[4], 1.0 - ln[4], ln[4]), radius=1.5)
                if version == 1:
                    generatedCurves1.append(c)
                else:
                    generatedCurves2.append(c)

        # Picking points is right now too slow
        # p1_shape = shapes.circle(radius=5)
        # for p in picked_points:
        #     p1_path = [vec(p.position[0], p.position[1], 0),
        #                    vec(p.position[0], p.position[1], 2)]
        #
        #     p1 = extrusion(path=p1_path, shape=p1_shape, color=vec(0.2, 0.2, 0.2))
        #     generatedPoints.append(p1)

    def show_double_bridge(bridge):
        show_bridge(bridge, -50, 1)
        show_bridge(bridge, 50, 2)

    scene.bind('mousedown', grab)
    scene.bind('mousemove', move)
    scene.bind('mouseup', drop)

    def start_everything():
        clear_my_scene()
        scene.axis = vector(0, 0, -1)
        scene.center = vector(canvasWidth / 2.0, canvasHeight / 2.0, 0)
        nonlocal first_start
        first_start = False
        print("START_EVERYTHING")
        global run_showing_bridge_next_steps, wait_for_click
        nonlocal t1

        t1 = thread_with_exception('Thread 1')
        bridge_obj = None
        point1 = None
        point2 = None

        while picking_points:
            wait_for_click = False
            rate(10)

        print(staticPoints)
        if len(staticPoints) >= 1:
            point1 = m2d.Vector2(staticPoints[0].pos.x, staticPoints[0].pos.y)
        if len(staticPoints) >= 2:
            point2 = m2d.Vector2(staticPoints[1].pos.x, staticPoints[1].pos.y)
        if len(staticPoints) > 2:
            it = 0
            while it < len(staticPoints) - 2:
                added_static_points.append(m2d.Vector2(staticPoints[it + 2].pos.x, staticPoints[it + 2].pos.y))
                it = it + 1

        number_of_extra_static_points = len(staticPoints) - 2

        if len(staticPoints) == 2:
            bridge_obj = Builder.buildInitial(materials, point1, point2)
            bridge_obj.roadStrains = static_load
            bridge_obj.render("renderCheck.png")
        elif len(staticPoints) > 2:
            bridge_obj = Builder.buildInitial(materials, point1, point2, number_of_extra_static_points,
                                              added_static_points)
            bridge_obj.roadStrains = static_load
            bridge_obj.render("renderCheck.png")

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

        depth = 400

        terrain_shape = shapes.points(
            pos=[[0, 0], [0, -length_y - 200], [-length_x, -length_y - 200], [-length_x, -length_y],
                 [-length_x - 1000, -length_y],
                 [-length_x - 1000, -length_y - depth], [1000, -length_y - depth], [1000, 0]])

        terrain_path = [vec(position_x, position_y, 0),
                        vec(position_x, position_y, 1000)]

        scene.center = vector(canvasWidth / 2.0, canvasHeight / 2.0, 0)
        scene.camera.axis.z = 900
        show_double_bridge(bridge_obj)
        scene.autoscale = False
        terrain = extrusion(path=terrain_path, shape=terrain_shape, visible=False)
        generatedTerrain.append(terrain)
        # terrain.rotate(angle=pi, axis=vec(position_x, 0, 0))
        print("POINTS: ")
        print(staticPoints[0].pos)
        print(staticPoints[1].pos)

        if (staticPoints[0].pos.x < staticPoints[1].pos.x) and (staticPoints[0].pos.y < staticPoints[1].pos.y):
            terrain.rotate(angle=pi, axis=vec(0, position_y, 0))
        elif (staticPoints[1].pos.x < staticPoints[0].pos.x) and (staticPoints[1].pos.y < staticPoints[0].pos.y):
            terrain.rotate(angle=pi, axis=vec(0, position_y, 0))

        terrain.pos = vec(position_x, position_y - depth / 2, 0)
        terrain.color = vec(0.6, 0.25, 0.02)

        terrain.visible = True
        ai.BridgeEvolution.bridge = bridge_obj
        ai.BridgeEvolution.upgrade_still_running = True

        t1.start()
        wtext_status.text = "\n\nStatus: simulation in progres."
        scene.axis = vector(-0.449187, -0.572867, -0.685605)
        scene.center = vector(position_x, position_y, 0)
        i = 0
        run_showing_bridge_next_steps = True
        while run_showing_bridge_next_steps:
            i = i + 1
            wtext_progress.text = "\n\nProgress: already done %d simulations" % mechanics.executedSimulation
            show_double_bridge(ai.BridgeEvolution.bridge)
            print(scene.center)
            # print(scene.position)
            if ai.BridgeEvolution.upgrade_still_running:
                wtext_status.text = "\n\nStatus: simulation in progres"
            elif mechanics.road_broke:
                wtext_status.text = "\n\nStatus: simulation ended, bridge broken."
            else:
                wtext_status.text = "\n\nStatus: bridge simulation completed successfully, bridge stable."
            rate(2)

    if first_start:
        start_everything()

    while True:
        print(".", sep=" ")
        rate(2)


    print("END")
