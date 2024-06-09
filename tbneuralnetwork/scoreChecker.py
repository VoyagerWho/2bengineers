import pickle
from tbsymulator.mechanicsFEM import simulate
import tbneuralnetwork.traindata as td
from tbneuralnetwork.nueralnetworkfunctions import score

if __name__ == "__main__":
    scores = [0 for _ in range(6)]
    for i in range(6):
        with open(f"winnerBridge{i}.pkl", "rb") as f:
            bridge = pickle.load(f)
        (rt, rs, rb) = simulate(bridge)
        scores[i] = score(bridge, rs, td.BUDGETS[i])
    print(scores)
    print(sum(scores)/len(scores))
