from tbutils.builder import Builder
import tbutils.math2d as m2
from tbutils.bridgeparts import Joint, Connection, Bridge
import tbneuralnetwork.nueralnetworkfunctions as nnf
import tbneuralnetwork.ai as ai
import os
from tbsymulator.mechanics import simulate
from tbsymulator.mechanics import checkIfBridgeWillSurvive as check_bridge
import tbutils.materiallist as mat_list
import datetime

# materials = Builder.createMaterialsList()
right = 300.0
materials = [mat_list.materialList[0],
             mat_list.materialList[3],
             mat_list.materialList[7],
             mat_list.materialList[19], ]
stat = [m2.Vector2(100.0, 250.0), m2.Vector2(right, 250.0), ]
bridge = Builder.buildInitial(materials, m2.Vector2(100.0, 300.0), m2.Vector2(right, 300.0), 1, stat)

# print([f'{con.length:0.1f}' for con in bridge.connections])

bridge.render("Default.png", 800, 600)

# simulate(bridge, makeAnimation=True, realBrakes=False, safeBreaking=True,
#                              resistance=0.5, toleranceCountDependent=True)
print(datetime.datetime.now().time())
[a, b, c] = simulate(bridge)
print(a, b, c, sep='\n')
# print(check_bridge(bridge))
print(datetime.datetime.now().time())

if _name_ == '_main_':
    ai.BridgeEvolution.bridge = bridge
    chamber = ai.BridgeEvolution(os.path.join(os.path.dirname(_file_), 'tbneuralnetwork'))
    chamber.set_reporter()
    chamber.train(100)
