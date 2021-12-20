import tbutils.math2d as m2
import math
from tbutils.bridgeparts import Joint, Connection, Bridge, Material


class Builder:
    """
    Class responsible of creating and initializing objects
    """

    @staticmethod
    def createMaterialsList():
        """
        Method to initialize list of starting materials
        :return: list of materials
        """
        """
        defMaxCompression = 0.9
        defMaxStrech = 1.1
        defCompressionForceRate = 1e4
        defStrechForceRate = 1e4
        """
        materials = [
            Material(
                "Asphalt Road", 100.0, 0.1,
                0.9, 1e4,
                1.1, 1e4, 20.0
            ),
            Material(
                "Steel Beam", 150.0, 0.2,
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
    def buildInitial(materials, a, b, noStat=0, stat=None):
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

        length = 0.7 * materials[1].maxLen
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
