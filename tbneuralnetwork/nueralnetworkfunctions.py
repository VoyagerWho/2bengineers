import tbutils.math2d as m2
from tbutils.bridgeparts import *


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
    joint = bridge.points[indexOfElement]
    connected = bridge.getConnectedToJoint(joint)
    moveRange = sum(con.material.maxLen for con in connected) / (len(connected) * 2)
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
    joint = bridge.points[indexOfElement]
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
    joint = bridge.points[indexOfElement]
    connected = bridge.getConnectedToJoint(joint)
    moveRange = sum(con.material.maxLen for con in connected) / (len(connected) * 2)
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
    joint = bridge.points[indexOfElement]
    newpos = joint.position + m2.Vector2((valx - 0.5), (valy - 0.5)) * bridge.materials[1].maxLen
    dists = [(j, (j.position - newpos).length()) for j in bridge.points if j != joint]
    place = min(dists, key=lambda x: x[1])
    if place[1] <= bridge.materials[1].maxLen:
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
    con = bridge.connections[indexOfElement]
    material = bridge.materials[int(len(bridge.materials) * val)]
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
    bridge.connections.pop(indexOfElement)
    return True
