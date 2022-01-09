import ctypes
import threading
import time

from tbneuralnetwork import ai
from tbsymulator import mechanics
from tbutils.builder import Builder
import tbutils.math2d as m2d
from vpython import *
import os

canvasWidth = 1200
canvasHeight = 480
picking_points = True
staticPoints = []

static_load = 0
show_natural = True
run_showing_bridge_next_steps = True
wait_for_click = False

#
generated_curves = []
generatedRoad = []
generatedPoints = []
generatedTerrain = []
generatedExtraPoles = []

# colors
color_background = vec(0.9, 0.9, 1)
color_asphalt = vec(0.2, 0.2, 0.2)
color_steel = vec(0.55, 0.55, 0.55)
color_wood = vec(0.6, 0.25, 0.02)
color_green = vec(0.3, 0.9, 0.3)
color_blue = vec(0.6, 0.6, 1)
color_concrete = vec(0.5, 0.5, 0.5)

hight_of_terrain = 400
hight_of_cliff = 200

posX = 0
posY = 0
length_x = 0
length_y = 0
position_x = 0
position_y = 0


class thread_with_exception(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.some_number = 0

    def run(self):
        # target function of the thread class
        try:
            bridge_evolution = ai.BridgeEvolution(
                (os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tbneuralnetwork'))))
            bridge_evolution.load()
            bridge_evolution.upgrade("", 1)

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
        points.append(point)
    return points


def stop_picking_points(b):
    global staticPoints
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


def delete_curves():
    global generated_curves, generatedPoints
    number_of_curves = len(generated_curves)
    number_of_points = len(generatedPoints)
    for i in range(0, number_of_curves, 1):
        generated_curves[0].visible = False
        del generated_curves[0]

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


def delete_extra_poles():
    global generatedExtraPoles
    number_of_stuff = len(generatedExtraPoles)
    for i in range(0, number_of_stuff, 1):
        generatedExtraPoles[0].visible = False
        del generatedExtraPoles[0]


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
    delete_curves()
    delete_points()
    delete_terrain()
    delete_extra_poles()


def generate_terrain():
    global staticPoints, hight_of_terrain, hight_of_cliff, posX, posY, length_x, length_y, position_x, position_y
    left_point = None
    rigth_point = None
    depth = 1000

    if staticPoints[0].pos.x < staticPoints[1].pos.x:
        left_point = staticPoints[0]
        rigth_point = staticPoints[1]
    else:
        left_point = staticPoints[1]
        rigth_point = staticPoints[0]

    length_x_not_abs = staticPoints[1].pos.x - staticPoints[0].pos.x
    length_y_not_abs = staticPoints[1].pos.y - staticPoints[0].pos.y
    length_x = abs(length_x_not_abs)
    length_y = abs(length_y_not_abs)

    grass_left_position_x = left_point.pos.x - 500
    grass_left_position_y = left_point.pos.y
    grass_right_position_x = rigth_point.pos.x + 500
    grass_right_position_y = rigth_point.pos.y

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

    terrain_shape = shapes.points(
        pos=[[0, 0], [0, -length_y - 200], [-length_x, -length_y - 200], [-length_x, -length_y],
             [-length_x - 1000, -length_y],
             [-length_x - 1000, -length_y - hight_of_terrain], [1000, -length_y - hight_of_terrain], [1000, 0]])

    terrain_path = [vec(position_x, position_y, 0),
                    vec(position_x, position_y, depth)]

    grass1_front = box(pos=vec(grass_left_position_x, grass_left_position_y, 275),
                       length=1000,
                       height=1, width=450, color=color_green)
    grass2_front = box(pos=vec(grass_right_position_x, grass_right_position_y, 275),
                       length=1000,
                       height=1, width=450, color=color_green)

    grass1_back = box(pos=vec(grass_left_position_x, grass_left_position_y, -275),
                      length=1000,
                      height=1, width=450, color=color_green)
    grass2_back = box(pos=vec(grass_right_position_x, grass_right_position_y, -275),
                      length=1000,
                      height=1, width=450, color=color_green)

    river = box(pos=vec(position_x, posY - hight_of_cliff, 0),
                length=length_x,
                height=1, width=depth, color=color_blue)

    road_terrain1 = box(pos=vec(grass_left_position_x, grass_left_position_y, 0),
                        length=1000,
                        height=1, width=100, color=color_asphalt)

    road_terrain2 = box(pos=vec(grass_right_position_x, grass_right_position_y, 0),
                        length=1000,
                        height=1, width=100, color=color_asphalt)

    terrain = extrusion(path=terrain_path, shape=terrain_shape, visible=False)

    if (staticPoints[0].pos.x < staticPoints[1].pos.x) and (staticPoints[0].pos.y < staticPoints[1].pos.y):
        terrain.rotate(angle=pi, axis=vec(0, position_y, 0))
    elif (staticPoints[1].pos.x < staticPoints[0].pos.x) and (staticPoints[1].pos.y < staticPoints[0].pos.y):
        terrain.rotate(angle=pi, axis=vec(0, position_y, 0))

    terrain.pos = vec(position_x, position_y - hight_of_terrain / 2, 0)
    terrain.color = vec(0.5, 0.2, 0.02)

    generatedTerrain.append(terrain)
    generatedTerrain.append(grass1_front)
    generatedTerrain.append(grass2_front)
    generatedTerrain.append(grass1_back)
    generatedTerrain.append(grass2_back)
    generatedTerrain.append(river)
    generatedTerrain.append(road_terrain1)
    generatedTerrain.append(road_terrain2)
    terrain.visible = True


def generate_extra_poles():
    global hight_of_terrain, hight_of_cliff, posX, posY, length_x, length_y
    over_bridge_level = 200
    picked_points = pick_points(ai.BridgeEvolution.bridge)
    for picked_point in picked_points:
        if picked_point.isStationary:
            connected = ai.BridgeEvolution.bridge.getConnectedToJoint(picked_point)
            if len(connected) > 0:
                bridge_level_from_bottom = length_y / length_x * (picked_point.position[0] - posX)
                final_high = (over_bridge_level + bridge_level_from_bottom + hight_of_terrain)
                static_pole1 = box(
                    pos=vec(picked_point.position[0], final_high / 2 - hight_of_terrain + posY, 55),
                    length=30,
                    height=final_high, width=10, color=color_concrete)
                static_pole2 = box(
                    pos=vec(picked_point.position[0], final_high / 2 - hight_of_terrain + posY, -55),
                    length=30,
                    height=final_high, width=10, color=color_concrete)
                static_bar = box(
                    pos=vec(picked_point.position[0], final_high - hight_of_terrain + posY - 5, 0),
                    length=30,
                    height=10, width=100, color=color_concrete)

                generatedExtraPoles.append(static_pole1)
                generatedExtraPoles.append(static_pole2)
                generatedExtraPoles.append(static_bar)


def ui():
    global picking_points, staticPoints, wait_for_click
    first_start = True
    t1 = None
    added_static_points = []

    def change_way_to_present_bridge(b):
        global show_natural
        if b.checked:
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
        if t1 is not None and t1.is_alive():
            t1.raise_exception()
            t1.join()

        time.sleep(1)
        picking_points = True
        start_everything()

    scene = canvas(width=canvasWidth, height=canvasHeight,
                   center=vector(canvasWidth / 2.0, canvasHeight / 2.0, 0), background=color_background,
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

    def show_bridge(bridge, position_z, width_of_bridge):
        picked_lines = pick_lines(bridge)
        # picked_points = pick_points(bridge)

        delete_curves()
        delete_road()

        print("SHOW BRIDGE")
        for ln in picked_lines:
            list_of_points1 = []
            list_of_points2 = []
            list_of_points1.append(vector(ln[0], ln[1], position_z))
            list_of_points1.append(vector(ln[2], ln[3], position_z))
            list_of_points2.append(vector(ln[0], ln[1], position_z+width_of_bridge))
            list_of_points2.append(vector(ln[2], ln[3], position_z+width_of_bridge))
            if show_natural:
                param = vec(0, 1, 0)
                rad = 2
                if ln[5].name == "Asphalt Road":
                    param = color_asphalt
                    rad = 3
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
                    road = box(pos=vec(road_position_x, road_position_y, 0), length=road_box_width, height=2,
                               width=100, axis=vec(road_length_x, road_length_y, 0), color=param)
                    generatedRoad.append(road)


                elif ln[5].name == "Steel Beam":
                    param = color_steel
                    rad = 2
                elif ln[5].name == "Wooden Beam":
                    param = color_wood
                    rad = 2

                c1 = curve(pos=list_of_points1, color=param, radius=rad)
                c2 = curve(pos=list_of_points2, color=param, radius=rad)
                generated_curves.append(c1)
                generated_curves.append(c2)

            else:
                c1 = curve(pos=list_of_points1, color=vec(ln[4], 1.0 - ln[4], ln[4]), radius=1.5)
                c2 = curve(pos=list_of_points2, color=vec(ln[4], 1.0 - ln[4], ln[4]), radius=1.5)
                generated_curves.append(c1)
                generated_curves.append(c2)

        # Picking points is right now too slow
        # p1_shape = shapes.circle(radius=5)
        # for p in picked_points:
        #     p1_path = [vec(p.position[0], p.position[1], 0),
        #                    vec(p.position[0], p.position[1], 2)]
        #
        #     p1 = extrusion(path=p1_path, shape=p1_shape, color=vec(0.2, 0.2, 0.2))
        #     generatedPoints.append(p1)

    scene.bind('mousedown', grab)
    scene.bind('mousemove', move)
    scene.bind('mouseup', drop)

    def start_everything():
        global run_showing_bridge_next_steps, wait_for_click
        nonlocal first_start, t1

        clear_my_scene()
        scene.axis = vector(0, 0, -1)
        scene.center = vector(canvasWidth / 2.0, canvasHeight / 2.0, 0)

        first_start = False
        print("START_EVERYTHING")

        t1 = thread_with_exception('Thread 1')
        bridge_obj = None
        point1 = None
        point2 = None

        while picking_points:
            wait_for_click = False
            rate(10)

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
        elif len(staticPoints) > 2:
            bridge_obj = Builder.buildInitial(materials, point1, point2, number_of_extra_static_points,
                                              added_static_points)
            bridge_obj.roadStrains = static_load

        generate_terrain()

        scene.center = vector(canvasWidth / 2.0, canvasHeight / 2.0, 0)
        scene.camera.axis.z = 900
        show_bridge(bridge_obj, -50, 100)
        scene.autoscale = False

        ai.BridgeEvolution.bridge = bridge_obj
        ai.BridgeEvolution.upgrade_still_running = True

        t1.start()
        wtext_status.text = "\n\nStatus: simulation in progres."
        scene.axis = vector(-0.449187, -0.572867, -0.685605)
        scene.center = vector(position_x, position_y, 0)

        run_showing_bridge_next_steps = True
        while run_showing_bridge_next_steps:
            wtext_progress.text = "\n\nProgress: already done %d simulations" % mechanics.executedSimulation
            show_bridge(bridge_obj, -50, 100)
            delete_extra_poles()
            if number_of_extra_static_points > 0:
                generate_extra_poles()
            if ai.BridgeEvolution.upgrade_still_running:
                wtext_status.text = "\n\nStatus: simulation in progres"
            elif mechanics.road_broke:
                wtext_status.text = "\n\nStatus: simulation ended, bridge broken."
            else:
                wtext_status.text = "\n\nStatus: bridge simulation completed successfully, bridge stable."
            rate(1)

    if first_start:
        start_everything()

    while True:
        print(".", sep=" ")
        rate(1)

    print("END")
