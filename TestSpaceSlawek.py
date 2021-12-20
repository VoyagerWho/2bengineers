from tbutils.builder import Builder
import tbutils.math2d as m2
from tbutils.bridgeparts import Joint, Connection, Bridge
import tbneuralnetwork.nueralnetworkfunctions as nnf
import tbneuralnetwork.ai as ai
import os
from tbsymulator.mechanics import SimulationThread

materials = Builder.createMaterialsList()
stat = [m2.Vector2(100.0, 250.0), m2.Vector2(500.0, 250.0), ]
bridge = Builder.buildInitial(materials, m2.Vector2(100.0, 300.0), m2.Vector2(500.0, 300.0), 1, stat)

print([f'{con.length:0.4f}' for con in bridge.connections])
for con in bridge.connections:
    print(con)
    assert not con.checkBreaking()

#from tests.test_tbsymulator.test_mechanics import createSampleBridge
#bridge = createSampleBridge()

bridge.render("Default.png", 600, 600)

print(bridge.getModelForRender())


simulation = SimulationThread(bridge, makeAnimation=True, realBrakes=False, safeBreaking=True, resistance=0.5, toleranceCountDependent=True)

simulation.start()
while simulation.running and simulation.time < 1.0:
    #print(f'{simulation.timeStep:0.6f}\t{simulation.maxSpeed():0.6f}\t{simulation.maxSpeedv2():0.6f}')
    #if simulation.isBroken():
        #print("Broken")
        #simulation.stopSimulation()
    pass
    
simulation.stopSimulation()

print()
print()
print()

for i, frame in enumerate(simulation.animation):
    print(i, "\t", frame, "\n")
    bridge.render("results.tmp/" + str(i) + ".png", 640, 480, model = frame[1])

print()
print()
print()

if __name__ == '__main__' and False:
    ai.bridge = bridge
    chamber = ai.BridgeEvolution(os.path.join(os.path.dirname(__file__), 'tbneuralnetwork'))
    chamber.set_reporter()
    chamber.train(400)

