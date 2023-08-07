from typing import List, Tuple

import tbutils.materiallist as mat_list
import tbutils.math2d as m2
import tbsymulator.mechanicsFEM as simulator
from tbutils.bridgeparts import Bridge, Joint, Connection
from tbutils.builder import Builder

#: Every bridge is represented as triplet (bridge: Bridge, steps: int, complexity: int)
TOTAL: int = 3
BRIDGES: List[Tuple[Bridge or None, int, int]] = [(None, 0, 0) for _ in range(TOTAL)]

MATERIALS = [mat_list.materialList[3],
             mat_list.materialList[3],
             ]


def build_initial():
    left = 100.0
    right = 300.0
    top = 300.0
    bottom = 250.0
    stat = [m2.Vector2(left, bottom), m2.Vector2(right, bottom), ]
    return Builder.buildInitial(MATERIALS, m2.Vector2(left, top), m2.Vector2(right, top), 1, stat)


def build_spike():
    joints = [Joint(m2.Vector2(0.0, 0.0), True), Joint(m2.Vector2(100.0, 0.0), True),
              Joint(m2.Vector2(50.0, 10.0))]
    con = [Connection.makeCFM(joints[0], joints[2], MATERIALS[0]),
           Connection.makeCFM(joints[1], joints[2], MATERIALS[0]),
           ]
    bridge = Bridge()
    bridge.points = joints
    bridge.connections = con
    bridge.materials = MATERIALS
    bridge.updateAll()
    return bridge


def build_pendulum():
    joints = [Joint(m2.Vector2(0.0, 0.0), True), Joint(m2.Vector2(100.0, 0.0), True),
              Joint(m2.Vector2(50.0, 0.0)), Joint(m2.Vector2(45.0, 35.0))]
    con = [Connection.makeCFM(joints[0], joints[2], MATERIALS[0]),
           Connection.makeCFM(joints[1], joints[2], MATERIALS[0]),
           Connection.makeCFM(joints[3], joints[2], MATERIALS[0]),
           ]
    bridge = Bridge()
    bridge.points = joints
    bridge.connections = con
    bridge.materials = MATERIALS
    bridge.updateAll()
    return bridge


BRIDGES[0] = (build_initial(), 5, 4)
BRIDGES[1] = (build_spike(), 1, 2)
BRIDGES[2] = (build_pendulum(), 1, 2)


BRIDGES_RESULTS = [() for _ in BRIDGES]
BUDGETS = [0.0 for _ in BRIDGES]
for i, (bridge, _, _) in enumerate(BRIDGES):
    BRIDGES_RESULTS[i] = simulator.simulate(bridge)
    BUDGETS[i] = 0.9 * sum(con.cost for con in bridge.connections)
# print("\nPrepared training data!\n")

if __name__ == "__main__":
    for i, (bridge, _, _) in enumerate(BRIDGES):
        bridge.render(f"Model{i}.png")
