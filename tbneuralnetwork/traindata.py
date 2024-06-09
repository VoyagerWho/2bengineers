from typing import List, Tuple

import tbutils.materiallist as mat_list
import tbutils.math2d as m2
import tbsymulator.mechanicsFEM as simulator
from tbutils.bridgeparts import Bridge, Joint, Connection
from tbutils.builder import Builder

#: Every bridge is represented as triplet (bridge: Bridge, steps: int, complexity: int)
TOTAL: int = 6
BRIDGES: List[Tuple[Bridge or None, int, int]] = [(None, 0, 0) for _ in range(TOTAL)]

MATERIALS = [mat_list.materialList[3],
             mat_list.materialList[3],
             ]


def build_initial():
    left = -100.0
    right = 100.0
    top = 25.0
    bottom = -25.0
    stat = [m2.Vector2(left, bottom), m2.Vector2(right, bottom), ]
    return Builder.buildInitial(MATERIALS, m2.Vector2(left, top), m2.Vector2(right, top), 1, stat)


def build_spike():
    joints = [Joint(m2.Vector2(-50.0, 0.0), True), Joint(m2.Vector2(50.0, 0.0), True),
              Joint(m2.Vector2(0.0, 10.0))]
    con = [Connection.makeCFM(joints[0], joints[2], MATERIALS[0]),
           Connection.makeCFM(joints[1], joints[2], MATERIALS[0]),
           ]
    bridge = Bridge()
    bridge.points = joints
    bridge.connections = con
    bridge.materials = MATERIALS
    return bridge


def build_pendulum():
    joints = [Joint(m2.Vector2(-50.0, 0.0), True), Joint(m2.Vector2(50.0, 0.0), True),
              Joint(m2.Vector2(0.0, 0.0)), Joint(m2.Vector2(-5.0, 35.0))]
    con = [Connection.makeCFM(joints[0], joints[2], MATERIALS[0]),
           Connection.makeCFM(joints[1], joints[2], MATERIALS[0]),
           Connection.makeCFM(joints[3], joints[2], MATERIALS[0]),
           ]
    bridge = Bridge()
    bridge.points = joints
    bridge.connections = con
    bridge.materials = MATERIALS
    return bridge


def build_mesh():
    xoffset = 950//2
    yoffset = 25
    joints = [
        Joint(m2.Vector2(-100.0 - xoffset, 0.0 - yoffset), True),
        Joint(m2.Vector2(-75.0 - xoffset, 0.0 - yoffset), True),
        Joint(m2.Vector2(-75.0 - xoffset, 75.0 - yoffset)),
    ]
    con = [Connection.makeCFM(joints[-1], joints[-2], MATERIALS[0])]
    for i in range(0, 751, 75):
        joints.append(Joint(m2.Vector2(i - xoffset, 0.0 - yoffset)))
        joints.append(Joint(m2.Vector2(i - xoffset, 75.0 - yoffset)))
        con.append(Connection.makeCFM(joints[-1], joints[-2], MATERIALS[0]))
        con.append(Connection.makeCFM(joints[-1], joints[-3], MATERIALS[0]))
        con.append(Connection.makeCFM(joints[-2], joints[-4], MATERIALS[0]))
    joints.append(Joint(m2.Vector2(825.0 - xoffset, 0.0 - yoffset), True))
    joints.append(Joint(m2.Vector2(825.0 - xoffset, 75.0 - yoffset)))
    joints.append(Joint(m2.Vector2(850.0 - xoffset, 0.0 - yoffset), True))
    con.append(Connection.makeCFM(joints[0], joints[2], MATERIALS[0]))
    con.append(Connection.makeCFM(joints[-1], joints[-2], MATERIALS[0]))
    con.append(Connection.makeCFM(joints[-2], joints[-3], MATERIALS[0]))
    con.append(Connection.makeCFM(joints[-3], joints[-5], MATERIALS[0]))
    con.append(Connection.makeCFM(joints[-2], joints[-4], MATERIALS[0]))
    bridge = Bridge()
    bridge.points = joints
    bridge.connections = con
    bridge.materials = MATERIALS
    return bridge


def build_gap():
    joints = [Joint(m2.Vector2(-75.0, 0.0), True), Joint(m2.Vector2(75.0, 0.0), True),
              Joint(m2.Vector2(-25.0, 10.0)), Joint(m2.Vector2(25.0, 10.0))]
    con = [Connection.makeCFM(joints[0], joints[2], MATERIALS[0]),
           Connection.makeCFM(joints[1], joints[3], MATERIALS[0]),
           ]
    bridge = Bridge()
    bridge.points = joints
    bridge.connections = con
    bridge.materials = MATERIALS
    return bridge


def build_wave():
    xoffset = 150
    joints = [Joint(m2.Vector2(150.0 - xoffset, -50.0), True), Joint(m2.Vector2(300.0 - xoffset, 0.0), True),
              Joint(m2.Vector2(0.0 - xoffset, 0.0), True), ]
    con = []
    for i in range(0, 101, 100):
        joints.append(Joint(m2.Vector2(i + 50.0 - xoffset, 50.0)))
        joints.append(Joint(m2.Vector2(i + 100.0 - xoffset, 0.0)))
        con.append(Connection.makeCFM(joints[-3], joints[-2], MATERIALS[0]))
        con.append(Connection.makeCFM(joints[-2], joints[-1], MATERIALS[0]))
    joints.append(Joint(m2.Vector2(250.0 - xoffset, 50.0)))
    con.append(Connection.makeCFM(joints[-2], joints[-1], MATERIALS[0]))
    con.append(Connection.makeCFM(joints[-1], joints[1], MATERIALS[0]))
    bridge = Bridge()
    bridge.points = joints
    bridge.connections = con
    bridge.materials = MATERIALS
    return bridge


BRIDGES[0] = (build_initial(), 5, 4)
BRIDGES[1] = (build_spike(), 1, 2)
BRIDGES[2] = (build_pendulum(), 1, 2)
BRIDGES[3] = (build_mesh(), 2, 4)
BRIDGES[4] = (build_gap(), 1, 2)
BRIDGES[5] = (build_wave(), 1, 2)


BRIDGES_RESULTS = [() for _ in BRIDGES]
BUDGETS = [0.0 for _ in BRIDGES]
for i, (bridge, _, _) in enumerate(BRIDGES):
    BRIDGES_RESULTS[i] = simulator.simulate(bridge)

    BUDGETS[i] = max(0.9 * sum(con.cost for con in bridge.connections), 0.1)
# print("\nPrepared training data!\n")

if __name__ == "__main__":
    for i, (bridge, _, _) in enumerate(BRIDGES):
        bridge.render(f"Model{i}.png")
    print(BUDGETS)
    from tbneuralnetwork.nueralnetworkfunctions import score, create_inputs
    scores = [score(bridge, BRIDGES_RESULTS[i][1], BUDGETS[i]) for i, (bridge, _, _) in enumerate(BRIDGES)]
    print(scores)
    print(sum(scores)/len(scores))
    with open("inputs.csv", "w") as f:
        for i, (bridge, steps, complexity) in enumerate(BRIDGES):
            (_, strains, break_moments) = BRIDGES_RESULTS[i]
            bridge_copy = bridge.copy()
            inputs_nn = create_inputs(bridge.copy(), break_moments, strains, complexity)
            for vec in inputs_nn:
                for x in vec:
                    f.write(str(x) + ",")
                f.write("0\n")
