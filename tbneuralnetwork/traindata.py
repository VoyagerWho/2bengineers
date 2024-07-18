from typing import List, Tuple
import tbutils.materiallist as mat_list
import tbutils.math2d as m2
import tbsymulator.mechanicsFEM as simulator
from tbutils.bridgeparts import Bridge, Material
from tbutils.builder import Builder
import numpy as np

#: Every dataset is represented as triplet (bridge: Bridge, steps: int, complexity: int)
STRUCTURES: int = 6
RANDOM: int = 5
DEFECTIVE: int = 4
TOTAL: int = STRUCTURES * (RANDOM + DEFECTIVE + 1)
BRIDGES: List[Tuple[Bridge, int, int]] = [(Bridge(), 0, 0) for _ in range(TOTAL)]

MATERIALS: List[Material] = [
    mat_list.materialList[3],
    mat_list.materialList[3],
    ]

BRIDGES[0] = (Builder.build_initial(MATERIALS, m2.Vector2(-100.0, 25.0), m2.Vector2(100.0, 25.0), 1,
                                    [m2.Vector2(-100.0, -25.0), m2.Vector2(100.0, -25.0), ]), 2, 4)
BRIDGES[1] = (Builder.build_spike(MATERIALS), 1, 2)
BRIDGES[2] = (Builder.build_pendulum(MATERIALS), 1, 2)
BRIDGES[3] = (Builder.build_mesh(MATERIALS), 2, 4)
BRIDGES[4] = (Builder.build_gap(MATERIALS), 1, 2)
BRIDGES[5] = (Builder.build_wave(MATERIALS), 2, 2)

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
