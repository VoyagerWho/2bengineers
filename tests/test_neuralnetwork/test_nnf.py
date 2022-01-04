from tbutils.bridgeparts import Bridge, Connection, Joint
import tbneuralnetwork.nueralnetworkfunctions as nnf
import tbutils.materiallist as mat_list
import tbutils.math2d as m2


def test_move_joint():
    materials = [mat_list.materialList[0],
                 mat_list.materialList[3],
                 mat_list.materialList[7],
                 mat_list.materialList[19], ]
    p = [Joint(m2.Vector2(0.0, 0.0), True), Joint(m2.Vector2(100.0, 0.0))]
    c = [Connection.makeCFM(p[0], p[1], materials[0])]
    bridge = Bridge()
    bridge.points = p
    bridge.connections = c
    bridge.materials = materials
    assert not nnf.moveJoint(bridge, 0, 0.0, 0.0)
    assert nnf.moveJoint(bridge, 1, 0.0, 0.0)
    assert p[1].position.x == 75.0 and p[1].position.y == -25.0


def test_remove_joint():
    materials = [mat_list.materialList[0],
                 mat_list.materialList[3],
                 mat_list.materialList[7],
                 mat_list.materialList[19], ]
    p = [Joint(m2.Vector2(0.0, 0.0), True), Joint(m2.Vector2(100.0, 0.0))]
    c = [Connection.makeCFM(p[0], p[1], materials[0])]
    bridge = Bridge()
    bridge.points = p
    bridge.connections = c
    bridge.materials = materials
    assert not nnf.removeJoint(bridge, 0, 0.0, 0.0)
    assert nnf.removeJoint(bridge, 1, 0.0, 0.0)
    assert len(bridge.points) == 1 and len(bridge.connections) == 0


def test_add_joint():
    materials = [mat_list.materialList[0],
                 mat_list.materialList[3],
                 mat_list.materialList[7],
                 mat_list.materialList[19], ]
    p = [Joint(m2.Vector2(0.0, 0.0), True), Joint(m2.Vector2(100.0, 0.0))]
    c = [Connection.makeCFM(p[0], p[1], materials[0])]
    bridge = Bridge()
    bridge.points = p
    bridge.connections = c
    bridge.materials = materials
    assert nnf.addJoint(bridge, 1, 0.0, 0.0)
    assert len(bridge.points) == 3
    assert p[2].position.x == 75.0 and p[2].position.y == -25.0


def test_add_connection():
    materials = [mat_list.materialList[0],
                 mat_list.materialList[3],
                 mat_list.materialList[7],
                 mat_list.materialList[19], ]
    p = [Joint(m2.Vector2(0.0, 0.0), True), Joint(m2.Vector2(100.0, 0.0))]
    c = [Connection.makeCFM(p[0], p[1], materials[0])]
    bridge = Bridge()
    bridge.points = p
    bridge.connections = c
    bridge.materials = materials
    nnf.addJoint(bridge, 1, 0.0, 0.0)
    assert not nnf.addConnection(bridge, 0, 0.0, 0.0)
    assert not nnf.addConnection(bridge, 1, 0.0, 0.0)
    assert nnf.addConnection(bridge, 0, 1.0, 0.25)


def test_change_connection():
    materials = [mat_list.materialList[0],
                 mat_list.materialList[3],
                 mat_list.materialList[7],
                 mat_list.materialList[19], ]
    p = [Joint(m2.Vector2(0.0, 0.0), True), Joint(m2.Vector2(100.0, 0.0))]
    c = [Connection.makeCFM(p[0], p[1], materials[0])]
    bridge = Bridge()
    bridge.points = p
    bridge.connections = c
    bridge.materials = materials
    assert nnf.changeConnectionMaterial(bridge, 0, 0.26)
    assert bridge.connections[0].material == bridge.materials[1]

def test_remove_connection():
    materials = [mat_list.materialList[0],
                 mat_list.materialList[3],
                 mat_list.materialList[7],
                 mat_list.materialList[19], ]
    p = [Joint(m2.Vector2(0.0, 0.0), True), Joint(m2.Vector2(100.0, 0.0))]
    c = [Connection.makeCFM(p[0], p[1], materials[0])]
    bridge = Bridge()
    bridge.points = p
    bridge.connections = c
    bridge.materials = materials
    assert nnf.removeConnection(bridge, 0, 0.0)
    assert len(bridge.connections) == 0 and len(bridge.points) == 2


if __name__ == '__main__':
    test_move_joint()
    test_remove_joint()
    test_add_joint()
    test_add_connection()
    test_change_connection()
    test_remove_connection()





