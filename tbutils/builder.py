import tbutils.math2d as m2
import math
from tbutils.bridgeparts import Joint, Connection, Bridge, Material
from typing import List


class Builder:
    """
    Class responsible of creating and initializing basic models of bridges
    """

    @staticmethod
    def createMaterialsList() -> List[Material]:
        """
        Method to initialize list of starting materials
        :return: list of materials
        """
        materials = [
            Material(
                "Asphalt Road", 100.0, 0.2,
                0.9, 1e4,
                1.1, 1e4, 20.0
            ),
            Material(
                "Steel Beam", 150.0, 0.4,
                0.9, 1e4,
                1.1, 1e4, 20.0
            ),
            Material(
                "Wooden Beam", 75.0, 0.1,
                0.9, 1e4,
                1.1, 1e4, 20.0
            ),
        ]
        materials[0].desc = "Material for roads (required)"
        materials[1].desc = "Basic support structure material"
        materials[2].desc = "Second support material"
        return materials

    @staticmethod
    def build_initial(materials: List[Material], a: m2.Vector2, b: m2.Vector2, noStat: int = 0,
                      stat: None or List[m2.Vector2] = None) -> Bridge:
        """
        Function to create initial procedural solution
        :param materials: list of the materials[0-road, 1-main, ...]
        :param a: Vector2 beginning of the road
        :param b: Vector2 end of the road
        :param noStat: number of extra stationary points
        :param stat: list of extra stationary points
        :return: Bridge object representing procedural solution
        """

        vecab = m2.Vector2(b - a)
        dist = vecab.length()
        noroad = int(dist // materials[0].maxLen + 2)
        roadlen = dist / noroad
        ratio = roadlen / dist
        roadpararel = vecab * ratio
        roadperpen = m2.Vector2(-roadpararel[1], roadpararel[0]).normal()
        roadjoints = [Joint(a, True)] \
                     + [Joint(a + roadpararel * i + roadperpen * (20 * math.sin(i * math.pi / noroad)))
                        for i in range(1, noroad)]
        roadjoints.append(Joint(b, True))

        length = materials[1].maxLen
        ratio = math.sqrt(length / roadlen - 1)
        joints = [Joint([0, 0]) for _ in range(noroad)]
        roads = [0 for _ in range(noroad)]
        for i in range(noroad):
            roadvec = roadjoints[i + 1].position - roadjoints[i].position
            ortroadvec = m2.Vector2(-roadvec[1], roadvec[0]) * ratio
            joints[i] = Joint(roadjoints[i].position + roadvec * 0.5 + ortroadvec)
            roads[i] = Connection.makeCFM(roadjoints[i], roadjoints[i + 1], materials[0])
        beams = [0 for _ in range(3 * noroad - 1)]
        for i in range(noroad):
            beams[3 * i - 2] = Connection.makeCFM(roadjoints[i], joints[i], materials[1])
            beams[3 * i - 1] = Connection.makeCFM(roadjoints[i + 1], joints[i], materials[1])
            if i < noroad - 1:
                beams[3 * i] = Connection.makeCFM(joints[i], joints[i + 1], materials[1])
        beams = roads + beams

        # handling of additional stationary points
        if noStat > 0:
            hanging = [j for j in stat]
            connectedm = [j for j in roadjoints[1:-1]] + joints
            connecteds = [roadjoints[0], roadjoints[-1]]
            i = 0
            while len(hanging) > 0:
                change = False
                dist2 = 1e20  # arbitrary large initial number
                minj = 0
                for j in connecteds:
                    vec = hanging[i] - j.position
                    dist2t = vec * vec
                    if dist2t < dist2:
                        dist2 = dist2t
                        minj = j

                if dist2 < (1.5 * materials[1].maxLen) ** 2:
                    vec = hanging[i] - minj.position
                    dist = math.sqrt(dist2)
                    ratio = 0.5 * dist * 0.5  # math.sin(math.pi / 6)
                    ortnorm = m2.Vector2(-vec[1], vec[0]).normal() * ratio
                    connectedm.append(Joint(minj.position + vec * 0.5 + ortnorm))
                    connectedm.append(Joint(minj.position + vec * 0.5 - ortnorm))
                    connecteds.append(Joint(hanging[i], True))
                    beams.append(Connection.makeCFM(connecteds[-1], connectedm[-2], materials[1]))
                    beams.append(Connection.makeCFM(connecteds[-1], connectedm[-1], materials[1]))
                    beams.append(Connection.makeCFM(minj, connectedm[-2], materials[1]))
                    beams.append(Connection.makeCFM(minj, connectedm[-1], materials[1]))

                    hanging.pop(i)
                    i = 0
                    change = True
                    continue

                dist2 = 1e20  # arbitrary large initial number
                minj = 0
                for j in connectedm:
                    vec = hanging[i] - j.position
                    dist2t = vec * vec
                    if dist2t < dist2:
                        dist2 = dist2t
                        minj = j

                if dist2 < (0.9 * materials[1].maxLen) ** 2:
                    connecteds.append(Joint(hanging[i], True))
                    beams.append(Connection.makeCFM(connecteds[-1], minj, materials[1]))
                    hanging.pop(i)
                    i = 0
                    change = True
                    continue
                elif (dist2 >= (0.9 * materials[1].maxLen) ** 2) and (dist2 < (1.9 * materials[1].maxLen) ** 2):
                    vec = hanging[i] - minj.position
                    dist = math.sqrt(dist2)
                    ratio = min(0.5 * dist * math.sin(math.pi / 3), 0.3 * materials[1].maxLen)
                    ortnorm = m2.Vector2(-vec[1], vec[0]).normal() * ratio
                    connectedm.append(Joint(minj.position + vec * 0.5 + ortnorm))
                    connectedm.append(Joint(minj.position + vec * 0.5 - ortnorm))
                    connecteds.append(Joint(hanging[i], True))
                    beams.append(Connection.makeCFM(connecteds[-1], connectedm[-2], materials[1]))
                    beams.append(Connection.makeCFM(connecteds[-1], connectedm[-1], materials[1]))
                    beams.append(Connection.makeCFM(minj, connectedm[-2], materials[1]))
                    beams.append(Connection.makeCFM(minj, connectedm[-1], materials[1]))
                    beams.append(Connection.makeCFM(connectedm[-2], connectedm[-1], materials[1]))
                    hanging.pop(i)
                    i = 0
                    change = True
                    continue
                i = i + 1
                print(i, change, hanging)
                if i >= len(hanging):
                    if not change:
                        for v in hanging:
                            connecteds.append(Joint(v, True))
                        hanging = []
                    i = 0
            joints = connecteds + connectedm
        else:
            joints = roadjoints + joints
        bridge = Bridge()
        bridge.points = joints
        bridge.connections = beams
        bridge.materials = materials
        return bridge

    @staticmethod
    def build_spike(materials: List[Material]) -> Bridge:
        """
        Function to create almost optimal model
        :param materials: list of the materials[0-road, 1-main, ...]
        :return: Bridge object representing prepared structure
        """
        joints = [Joint(m2.Vector2(-50.0, 0.0), True), Joint(m2.Vector2(50.0, 0.0), True),
                  Joint(m2.Vector2(0.0, 10.0))]
        con = [Connection.makeCFM(joints[0], joints[2], materials[0]),
               Connection.makeCFM(joints[1], joints[2], materials[0]),
               ]
        bridge = Bridge()
        bridge.points = joints
        bridge.connections = con
        bridge.materials = materials
        return bridge

    @staticmethod
    def build_pendulum(materials: List[Material]) -> Bridge:
        """
        Function to create model with one additional pendulum
        :param materials: list of the materials[0-road, 1-main, ...]
        :return: Bridge object representing prepared structure
        """
        joints = [Joint(m2.Vector2(-50.0, 0.0), True), Joint(m2.Vector2(50.0, 0.0), True),
                  Joint(m2.Vector2(0.0, 0.0)), Joint(m2.Vector2(-5.0, 35.0))]
        con = [Connection.makeCFM(joints[0], joints[2], materials[0]),
               Connection.makeCFM(joints[1], joints[2], materials[0]),
               Connection.makeCFM(joints[3], joints[2], materials[0]),
               ]
        bridge = Bridge()
        bridge.points = joints
        bridge.connections = con
        bridge.materials = materials
        return bridge

    @staticmethod
    def build_mesh(materials: List[Material]) -> Bridge:
        """
        Function to create model of multiple quadrangles
        :param materials: list of the materials[0-road, 1-main, ...]
        :return: Bridge object representing prepared structure
        """
        xoffset = 950 // 2
        yoffset = 25
        joints = [
            Joint(m2.Vector2(-75.0 - xoffset, 0.0 - yoffset), True),
            Joint(m2.Vector2(825.0 - xoffset, 0.0 - yoffset), True),
            Joint(m2.Vector2(-100.0 - xoffset, 0.0 - yoffset), True),
            Joint(m2.Vector2(850.0 - xoffset, 0.0 - yoffset), True),
            Joint(m2.Vector2(-75.0 - xoffset, 75.0 - yoffset)),
            Joint(m2.Vector2(825.0 - xoffset, 75.0 - yoffset)),

        ]
        prev_ref = [joints[0], joints[4]]
        con = [Connection.makeCFM(joints[0], joints[4], materials[0])]
        for i in range(0, 751, 75):
            joints.append(Joint(m2.Vector2(i - xoffset, 0.0 - yoffset)))
            joints.append(Joint(m2.Vector2(i - xoffset, 75.0 - yoffset)))
            con.append(Connection.makeCFM(joints[-1], joints[-2], materials[0]))
            con.append(Connection.makeCFM(joints[-1], prev_ref[-1], materials[0]))
            con.append(Connection.makeCFM(joints[-2], prev_ref[-2], materials[0]))
            prev_ref = [joints[-2], joints[-1]]
        con.append(Connection.makeCFM(joints[2], joints[4], materials[0]))
        con.append(Connection.makeCFM(joints[3], joints[5], materials[0]))
        con.append(Connection.makeCFM(joints[1], joints[5], materials[0]))
        con.append(Connection.makeCFM(joints[-1], joints[5], materials[0]))
        con.append(Connection.makeCFM(joints[-2], joints[1], materials[0]))
        bridge = Bridge()
        bridge.points = joints
        bridge.connections = con
        bridge.materials = materials
        return bridge

    @staticmethod
    def build_gap(materials: List[Material]) -> Bridge:
        """
        Function to create model not semi valid model with gap
        :param materials: list of the materials[0-road, 1-main, ...]
        :return: Bridge object representing prepared structure
        """
        joints = [Joint(m2.Vector2(-75.0, 0.0), True), Joint(m2.Vector2(75.0, 0.0), True),
                  Joint(m2.Vector2(-25.0, 10.0)), Joint(m2.Vector2(25.0, 10.0))]
        con = [Connection.makeCFM(joints[0], joints[2], materials[0]),
               Connection.makeCFM(joints[1], joints[3], materials[0]),
               ]
        bridge = Bridge()
        bridge.points = joints
        bridge.connections = con
        bridge.materials = materials
        return bridge

    @staticmethod
    def build_wave(materials: List[Material]) -> Bridge:
        """
        Function to create unstable model with road in the shape of wave
        :param materials: list of the materials[0-road, 1-main, ...]
        :return: Bridge object representing prepared structure
        """
        xoffset = 150
        joints = [Joint(m2.Vector2(300.0 - xoffset, 0.0), True),
                  Joint(m2.Vector2(0.0 - xoffset, 0.0), True), ]
        con = []
        for i in range(0, 101, 100):
            joints.append(Joint(m2.Vector2(i + 50.0 - xoffset, 50.0)))
            joints.append(Joint(m2.Vector2(i + 100.0 - xoffset, 0.0)))
            con.append(Connection.makeCFM(joints[-3], joints[-2], materials[0]))
            con.append(Connection.makeCFM(joints[-2], joints[-1], materials[0]))
        joints.append(Joint(m2.Vector2(250.0 - xoffset, 50.0)))
        con.append(Connection.makeCFM(joints[-2], joints[-1], materials[0]))
        con.append(Connection.makeCFM(joints[-1], joints[0], materials[0]))
        joints.append(Joint(m2.Vector2(150.0 - xoffset, -50.0), True))
        bridge = Bridge()
        bridge.points = joints
        bridge.connections = con
        bridge.materials = materials
        return bridge
