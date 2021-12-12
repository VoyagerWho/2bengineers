from tbutils.builder import Builder
import tbutils.math2d as m2
from tbutils.bridgeparts import Joint, Connection
import tbneuralnetwork.nueralnetworkfunctions as nnf

materials = Builder.createMaterialsList()
stat = [m2.Vector2(30.0, 300.0), m2.Vector2(100.0, 230.0),
        m2.Vector2(100.0, 210.0), m2.Vector2(200.0, 800.0)]
bridge = Builder.buildInitial(materials, m2.Vector2(100.0, 300.0), m2.Vector2(700.0, 400.0), 3, stat)

print(nnf.changeConnectionMaterial(bridge, 10, 0.1))

print(nnf.removeConnection(bridge, 7, 0.3))

print(nnf.removeJoint(bridge, 8, 0.3, 0.6))

print(nnf.addJoint(bridge, 10, 0.5, 0.1))

print(nnf.moveJoint(bridge, 15, 0.3, 0.6))

print(nnf.addConnection(bridge, 3, 0.9, 0.3))

bridge.render("Default.png", 800, 600)
