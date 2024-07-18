from typing import List, Tuple

import tbutils.materiallist as mat_list
import tbutils.math2d as m2
import tbsymulator.mechanicsFEM as simulator
from tbutils.bridgeparts import Bridge, Joint, Connection, Material
from tbutils.builder import Builder
import numpy as np

#: Every bridge is represented as triplet (bridge: Bridge, steps: int, complexity: int)
STRUCTURES: int = 6
RANDOM: int = 5
DEFECTIVE: int = 4
TOTAL: int = STRUCTURES * (RANDOM + DEFECTIVE + 1)
BRIDGES: List[Tuple[Bridge, int, int]] = [(Bridge(), 0, 0) for _ in range(TOTAL)]

MATERIALS: List[Material] = [
    mat_list.materialList[3],
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
        Joint(m2.Vector2(-75.0 - xoffset, 0.0 - yoffset), True),
        Joint(m2.Vector2(825.0 - xoffset, 0.0 - yoffset), True),
        Joint(m2.Vector2(-100.0 - xoffset, 0.0 - yoffset), True),
        Joint(m2.Vector2(850.0 - xoffset, 0.0 - yoffset), True),
        Joint(m2.Vector2(-75.0 - xoffset, 75.0 - yoffset)),
        Joint(m2.Vector2(825.0 - xoffset, 75.0 - yoffset)),

    ]
    prev_ref = [joints[0], joints[4]]
    con = [Connection.makeCFM(joints[0], joints[4], MATERIALS[0])]
    for i in range(0, 751, 75):
        joints.append(Joint(m2.Vector2(i - xoffset, 0.0 - yoffset)))
        joints.append(Joint(m2.Vector2(i - xoffset, 75.0 - yoffset)))
        con.append(Connection.makeCFM(joints[-1], joints[-2], MATERIALS[0]))
        con.append(Connection.makeCFM(joints[-1], prev_ref[-1], MATERIALS[0]))
        con.append(Connection.makeCFM(joints[-2], prev_ref[-2], MATERIALS[0]))
        prev_ref = [joints[-2], joints[-1]]
    con.append(Connection.makeCFM(joints[2], joints[4], MATERIALS[0]))
    con.append(Connection.makeCFM(joints[3], joints[5], MATERIALS[0]))
    con.append(Connection.makeCFM(joints[1], joints[5], MATERIALS[0]))
    con.append(Connection.makeCFM(joints[-1], joints[5], MATERIALS[0]))
    con.append(Connection.makeCFM(joints[-2], joints[1], MATERIALS[0]))
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
    joints = [Joint(m2.Vector2(300.0 - xoffset, 0.0), True),
              Joint(m2.Vector2(0.0 - xoffset, 0.0), True), ]
    con = []
    for i in range(0, 101, 100):
        joints.append(Joint(m2.Vector2(i + 50.0 - xoffset, 50.0)))
        joints.append(Joint(m2.Vector2(i + 100.0 - xoffset, 0.0)))
        con.append(Connection.makeCFM(joints[-3], joints[-2], MATERIALS[0]))
        con.append(Connection.makeCFM(joints[-2], joints[-1], MATERIALS[0]))
    joints.append(Joint(m2.Vector2(250.0 - xoffset, 50.0)))
    con.append(Connection.makeCFM(joints[-2], joints[-1], MATERIALS[0]))
    con.append(Connection.makeCFM(joints[-1], joints[0], MATERIALS[0]))
    joints.append(Joint(m2.Vector2(150.0 - xoffset, -50.0), True))
    bridge = Bridge()
    bridge.points = joints
    bridge.connections = con
    bridge.materials = MATERIALS
    return bridge


BRIDGES[0] = (build_initial(), 2, 4)
BRIDGES[1] = (build_spike(), 1, 2)
BRIDGES[2] = (build_pendulum(), 1, 2)
BRIDGES[3] = (build_mesh(), 2, 4)
BRIDGES[4] = (build_gap(), 1, 2)
BRIDGES[5] = (build_wave(), 2, 2)

if RANDOM > 0:
    j = STRUCTURES
    rng = np.random.default_rng(seed=3141592653589)
    offsetSize = 20.0
    for i in range(RANDOM):
        for bridge, steps, complexity in BRIDGES[0:STRUCTURES]:
            bridge_copy = bridge.copy()
            pointsCount = len(bridge.points)
            offsets = [m2.Vector2(offsetSize*rng.random()-offsetSize/2, offsetSize*rng.random()-offsetSize/2)
                       for _ in range(pointsCount)]
            for pid in range(pointsCount):
                bridge_copy.points[pid].position += offsets[pid]
            bridge_copy.updateAll()
            BRIDGES[j] = (bridge_copy, steps, complexity)
            j += 1

if DEFECTIVE > 0:
    from tbneuralnetwork.nueralnetworkfunctions import removeJoint, removeConnection
    j = STRUCTURES * (RANDOM + 1)
    rng = np.random.default_rng(seed=3141592653589)
    offsetSize = 20.0
    for i in range(DEFECTIVE):
        for s, (bridge, steps, complexity) in enumerate(BRIDGES[0:STRUCTURES]):
            bridge_copy = bridge.copy()
            if s == 1:
                pointsCount = len(bridge.points)
                offsets = [
                    m2.Vector2(offsetSize * rng.random() - offsetSize / 2, offsetSize * rng.random() - offsetSize / 2)
                    for _ in range(pointsCount)
                ]
                for pid in range(pointsCount):
                    bridge_copy.points[pid].position += offsets[pid]
            else:
                points = [r for r, p in enumerate(bridge.points) if not p.isStationary]
                rand_p = rng.choice(points, size=(DEFECTIVE//2,))
                rand_c = rng.choice(range(len(bridge.connections)), size=(DEFECTIVE - DEFECTIVE // 2), )
                if i < DEFECTIVE//2:
                    removeJoint(bridge_copy, rand_p[i])
                else:
                    removeConnection(bridge_copy, rand_c[i - DEFECTIVE//2])
                pass
            bridge_copy.updateAll()
            BRIDGES[j] = (bridge_copy, steps, complexity)
            j += 1


BRIDGES_RESULTS: List[Tuple[int, List[float], List[int]]] = [(0, [0.0, ], [0, ]) for _ in BRIDGES]
BUDGETS: List[float] = [0.0 for _ in BRIDGES]
for i, (bridge, _, _) in enumerate(BRIDGES):
    BRIDGES_RESULTS[i] = simulator.simulate(bridge)
    # print(BRIDGES_RESULTS[i][1])
    BUDGETS[i] = max(0.9 * sum(con.cost for con in bridge.connections), 0.1)
# print("\nPrepared training data!\n")

if __name__ == "__main__":
    for i, (bridge, _, _) in enumerate(BRIDGES):
        bridge.render(f"models/Model{i}.png")
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
