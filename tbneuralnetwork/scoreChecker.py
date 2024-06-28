from typing import Tuple, List
import pickle
from tbsymulator.mechanicsFEM import simulate
import tbneuralnetwork.traindata as td
from tbneuralnetwork.nueralnetworkfunctions import score
from tbutils.bridgeparts import Bridge


def show_all(total: int) -> None:
    scores = [0 for _ in range(total)]
    for i in range(total):
        with open(f"train_results/winnerBridge{i}.pkl", "rb") as f:
            bridge = pickle.load(f)
        (rt, rs, rb) = simulate(bridge)
        scores[i] = score(bridge, rs, td.BUDGETS[i])
    print(scores)
    print(sum(scores) / len(scores))


def compare(old_bridge: Tuple[Bridge, List[float], float], new_bridge: Tuple[Bridge, List[float], float]) -> None:
    old_score = score(old_bridge[0], old_bridge[1], old_bridge[2])
    new_score = score(new_bridge[0], new_bridge[1], new_bridge[2])
    print(f"Score:  {old_score} -> {new_score}")
    print(f"Strain: {max(old_bridge[1])} -> {max(new_bridge[1])}")
    print(f"Points: {len(old_bridge[0].points)} -> {len(new_bridge[0].points)}")
    for p1, p2 in zip(old_bridge[0].points, new_bridge[0].points):
        print(f"Pos:    {p1.position} -> {p2.position}")
    print(f"Beams:  {len(old_bridge[0].connections)} -> {len(new_bridge[0].connections)}")
    for c1, c2 in zip(old_bridge[0].connections, new_bridge[0].connections):
        print(f"Cost:   {c1.cost} -> {c2.cost}")
        print(f"Mass:   {c1.mass} -> {c2.mass}")
        print(f"Length: {c1.length} -> {c2.length}")
        print("----------------------------------")


def get_from_traindata(bridge_id: int) -> Tuple[Bridge, List[float], float]:
    return td.BRIDGES[bridge_id][0], td.BRIDGES_RESULTS[bridge_id][1], td.BUDGETS[bridge_id]


def get_from_results(bridge_id: int) -> Tuple[Bridge, List[float], float]:
    with open(f"train_results/winnerBridge{bridge_id}.pkl", "rb") as f:
        bridge = pickle.load(f)
    (_, rs, _) = simulate(bridge)
    return bridge, rs, td.BUDGETS[bridge_id]


if __name__ == "__main__":
    show_all(60)
    # ob = get_from_traindata(0)
    # nb = get_from_traindata(6)
    # nb = get_from_results(0)
    # compare(ob, nb)
