"""
Module defining helper functions for the AI
"""

import math
from tbutils.bridgeparts import *
from tbutils.materiallist import materialList


def moveJoint(bridge: Bridge, indexOfElement: int, valx: float, valy: float):
    """
    Helper function for AI to allow to move single Joint within a square area
    :param bridge: bridge object to alter
    :param indexOfElement: index of the joint to move
    :param valx: ratio of x offset <0, 1>
    :param valy: ratio of y offset <0, 1>
    :return: True if operation was possible False otherwise
    """
    # to do checks if possible and move joint and all connected beams
    # print("mj: ", indexOfElement, len(bridge.points))
    joint = bridge.points[indexOfElement]
    if joint.isStationary:
        return False
    connected = bridge.getConnectedToJoint(joint)
    moveRange = sum(con.material.maxLen for con in connected) / (len(connected) * 2) if len(connected) > 0 else 50.0
    offsetx = (valx - 0.5) * moveRange
    offsety = (valy - 0.5) * moveRange
    newpos = joint.position + m2.Vector2(offsetx, offsety)
    temppos = [con.jointA.position - newpos if con.jointB == joint
               else con.jointB.position - newpos for con in connected]
    templens = [vec.length() for vec in temppos]
    if sum(0 if templens[i] <= con.material.maxLen else 1 for i, con in enumerate(connected)) == 0:
        joint.position = newpos
        bridge.updateOnJoint(joint)
        return True
    else:
        return False


def removeJoint(bridge: Bridge, indexOfElement: int, *extra):
    """
    Helper function for AI to allow to remove single Joint
    :param bridge: bridge object to alter
    :param indexOfElement: index of the joint to remove
    :param extra: extra parameters to normalize interaction
    :return: True if operation was possible False otherwise
    """
    # to do checks and removal of the joint and connection
    # print("rj: ", indexOfElement, len(bridge.points))
    joint = bridge.points[indexOfElement]
    if joint.isStationary:
        return False
    bridge.connections = [con for con in bridge.connections if con.jointA != joint and con.jointB != joint]
    bridge.points.remove(joint)
    return True


def addJoint(bridge: Bridge, indexOfElement: int, valx: float, valy: float):
    """
    Helper function for AI to allow to add single Joint within a square area of the other one
    and connect it them with default beam
    :param bridge: bridge object to alter
    :param indexOfElement: index of the joint to connect with
    :param valx: ratio of x offset of the new joint <0, 1>
    :param valy: ratio of y offset of the new joint <0, 1>
    :param radius: maximum offset in booth axes
    :return: True if operation was possible False otherwise
    """
    # to do checks and adding of the joint
    # print("aj: ", indexOfElement, len(bridge.points))
    joint = bridge.points[indexOfElement]
    connected = bridge.getConnectedToJoint(joint)
    moveRange = sum(con.material.maxLen for con in connected) / (len(connected) * 2) if len(connected) > 0 else 50.0
    offsetx = (valx - 0.5) * moveRange
    offsety = (valy - 0.5) * moveRange
    newpos = joint.position + m2.Vector2(offsetx, offsety)
    newJoint = Joint(newpos)
    bridge.connections.append(Connection.makeCFM(joint, newJoint, bridge.materials[1]))
    bridge.points.append(newJoint)
    return True


def addConnection(bridge: Bridge, indexOfElement: int, valx: float, valy: float):
    """
    Helper function for AI to allow to connect Joint with another with default beam within square area of it
    :param bridge: bridge object to alter
    :param indexOfElement: index of the joint to connect with
    :param valx: ratio of x offset of the second joint <0, 1>
    :param valy: ratio of y offset of the second joint <0, 1>
    :return: True if operation was possible False otherwise
    """
    # to do checks and connection of the joints
    # print("ac: ", indexOfElement, len(bridge.points))
    joint = bridge.points[indexOfElement]
    newpos = joint.position + m2.Vector2((valx - 0.5), (valy - 0.5)) * bridge.materials[1].maxLen
    dists = [(j, (j.position - newpos).length()) for j in bridge.points if j != joint]
    place = min(dists, key=lambda x: x[1])
    if place[1] <= bridge.materials[1].maxLen:
        connected = bridge.getConnectedToJoint(joint)
        for c in connected:
            if c.jointA == place[0] or c.jointB == place[0]:
                return False
        bridge.connections.append(Connection.makeCFM(joint, place[0], bridge.materials[1]))
        return True
    else:
        return False


def changeConnectionMaterial(bridge: Bridge, indexOfElement: int, val: float):
    """
    Helper function for AI to allow to change single Connection's material
    :param bridge: bridge object to alter
    :param indexOfElement: index of the connection
    :param val: ratio of the offset in materials length
    :return: True if operation was possible False otherwise
    """
    # to do checks and alteration of connection
    # print("cc: ", indexOfElement, len(bridge.connections))
    con = bridge.connections[indexOfElement]
    material = bridge.materials[int((len(bridge.materials)-1) * val)]
    if con.length <= material.maxLen:
        bridge.connections[indexOfElement] = Connection.makeCFM(con.jointA, con.jointB, material)
        return True
    else:
        return False


def removeConnection(bridge: Bridge, indexOfElement: int, *extra):
    """
    Helper function for AI to allow to remove single Connection
    :param bridge: bridge object to alter
    :param indexOfElement: index of the connection
    :param extra: extra value to unify functions call
    :return: True if operation was possible False otherwise
    """
    # to do checks and removal of the connection
    # print("rc: ", indexOfElement, len(bridge.connections))
    bridge.connections.pop(indexOfElement)
    return True


def score(bridge_local: Bridge, strains, budget: float):
    """
    Utility function to calculate resulting score of the simulation for genome fitness value
    :param bridge_local: tested structure
    :param strains: maximum value of strain in simulation
    :param budget: optimal budget of structure
    :return: float: score of the model
    """
    max_strain = max(strains, default=0.0)
    cost = sum(con.cost for con in bridge_local.connections)
    cost_offset = 0.5 * math.atan(0.01 * (budget - cost)) / math.pi
    if bridge_local.isSemiValid():
        return 1 - min(math.sqrt(max_strain), 5.0) + cost_offset
    return 0.5 + cost_offset


def create_inputs(bridge: Bridge, break_moments, strains, complexity):
    """
    Calculation of current statistics of the bridge and preparing inputs for networks to train on
    """
    inputs_nn = [() for _ in range(len(bridge.points) + len(bridge.connections))]
    for i, j in enumerate(bridge.points):
        indexes = [bridge.connections.index(con)
                   for con in bridge.getConnectedToJoint(j)]
        no_connected = len(indexes)
        strain_con = [strains[idx] for idx in indexes]
        broken = list(filter(lambda x: (x >= 1.0), strain_con))
        j_type = -1.0
        j_movement = 1.0 if j.isStationary else 0.0
        j_min = min(strain_con, default=0.0)
        j_max = max(strain_con, default=0.0)
        j_stress = sum(strain_con) / no_connected if no_connected > 0 else 0.0
        j_complexity = (len(indexes)-complexity)/complexity
        j_damage = len(broken)/no_connected if no_connected > 0 else 0.0
        inputs_nn[i] = (j_type, j_movement, j_min, j_max, j_stress, j_complexity, j_damage)
    points = len(bridge.points)

    for i, con in enumerate(bridge.connections):
        movement_joint_a = con.jointA.isStationary
        movement_joint_b = con.jointB.isStationary
        c_type = 1.0
        c_movement = -1.0 if movement_joint_a ^ movement_joint_b else (0.0 if movement_joint_a else 1.0)
        c_min = -1.0
        c_max = -1.0
        c_stress = strains[i]
        c_complexity = con.length / con.material.maxLen
        c_damage = break_moments[i]
        inputs_nn[points+i] = (c_type, c_movement, c_min, c_max, c_stress, c_complexity, c_damage)
    return inputs_nn


def alter_bridge(commands: list, my_bridge: Bridge):
    """
    Function that performs analysis of network solution
    :param verbose: print info whether bridge collapsed or not
    :param my_bridge: bridge to alter
    :param commands: output of network to incorporate
    :return: statistics of a new bridge
    """
    mj = []
    rj = []
    aj = []
    ac = []
    rc = []
    removed_joints = 0
    removed_connections = 0
    for i, (el_type, args) in enumerate(commands):
        if el_type == -1.0:
            if args[0] > 0.75:
                mj.append((i, args[1], args[2]))
            if args[9] > 0.75:
                rj.append((i - removed_joints,))
                removed_joints += 1
            if args[3] > 0.75:
                aj.append((i, args[4], args[5]))
            if args[6] > 0.75:
                ac.append((i, args[7], args[8]))
        elif el_type == 1.0:
            idx = i - len(my_bridge.points)
            if args[10] > 0.75:
                rc.append((idx - removed_connections,))
                removed_connections += 1

    for c in mj:
        moveJoint(my_bridge, c[0], c[1], c[2])
    for c in aj:
        addJoint(my_bridge, c[0], c[1], c[2])
    for c in ac:
        addConnection(my_bridge, c[0], c[1], c[2])
    for c in rc:
        removeConnection(my_bridge, c[0])
    for c in rj:
        removeJoint(my_bridge, c[0])

    return my_bridge


if __name__ == "__main__":
    materials = [materialList[3], materialList[3], ]
    joints = [Joint(m2.Vector2(0.0, 0.0), True), Joint(m2.Vector2(100.0, 0.0), True),
              Joint(m2.Vector2(50.0, 10.0))]
    con = [Connection.makeCFM(joints[0], joints[2], materials[0]),
           Connection.makeCFM(joints[1], joints[2], materials[0]),
           ]
    test_bridge = Bridge()
    test_bridge.points = joints
    test_bridge.connections = con
    test_bridge.materials = materials
    test_bridge.updateAll()
    test_bridge.render("Test.png")
    print(test_bridge.points[2])
    moveJoint(test_bridge, 2, 1, 1)
    addJoint(test_bridge, 2, 0, 0)
    addConnection(test_bridge, 0, 1, 0.4)
    removeJoint(test_bridge, 2)
    removeConnection(test_bridge, 0)
    test_bridge.render("Modified.png")
    print(test_bridge.points[2])


