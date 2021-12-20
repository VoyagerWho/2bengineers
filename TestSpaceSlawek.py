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

bridge.render("Default.png", 600, 600)

print(bridge.getModelForRender())

simulation = SimulationThread(bridge, makeAnimation=True)

simulation.start()
while simulation.running and simulation.time < 1.0:
    print(f'{simulation.timeStep:0.6f}\t{simulation.maxSpeed():0.6f}\t{simulation.maxSpeedv2():0.6f}')
    if simulation.isBroken():
        simulation.stopSimulation()
simulation.stopSimulation()
for frame in simulation.animation:
    print(frame)

if __name__ == '__main__' and False:
    ai.bridge = bridge
    chamber = ai.BridgeEvolution(os.path.join(os.path.dirname(__file__), 'tbneuralnetwork'))
    chamber.set_reporter()
    chamber.train(400)

