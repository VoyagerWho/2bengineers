from typing import List, Tuple

import tbutils.materiallist as mat_list
import tbutils.math2d as m2
import tbsymulator.mechanicsFEM as simulator
from tbutils.bridgeparts import Bridge
from tbutils.builder import Builder

#: Every bridge is represented as triplet (bridge: Bridge, steps: int, complexity: int)
TOTAL: int = 1
BRIDGES: List[Tuple[Bridge, int, int]] = [() for _ in range(TOTAL)]

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


BRIDGES[0] = (build_initial(), 5, 4)
BRIDGES_RESULTS = [() for _ in BRIDGES]
BUDGETS = [0.0 for _ in BRIDGES]
for i, (bridge, _, _) in enumerate(BRIDGES):
    BRIDGES_RESULTS[i] = simulator.simulate(bridge)
    BUDGETS[i] = 0.9 * sum(con.cost for con in bridge.connections)
# print("\nPrepared training data!\n")
