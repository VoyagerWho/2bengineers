import tbutils.math2d as m2
import math
from tbutils.bridgeparts import Joint, Connection, Bridge


class Builder:
    @staticmethod
    def buildInitial(width, height, materials, a, b, noStat=0, *stat):
        """
        Function to create initial procedural solution
        :param width: width of the board
        :param height: height of the board
        :param materials: list of the materials[0-road, 1-main, ...]
        :param a: Vector2 beginning of the road
        :param b: Vector2 end of the road
        :param noStat: number of extra stationary points
        :param stat: list of extra stationary points
        :return: Bridge object representing procedural solution
        """
        vecab = m2.Vector2(b - a)
        dist = vecab.len()
        noroad = dist // materials[0].maxlen + 2
        roadlen = dist / noroad
        ratio = dist / roadlen
        roadpararel = vecab * ratio
        roadperpen = m2.Vector2(-roadpararel[1], roadpararel[0]).normal()
        roadjoints = [a + roadpararel * i + roadperpen * (20 * math.sin(i * math.pi / noroad)) for i in
                      range(noroad + 1)]
        roadjoints.append(b)

        len = 0.7 * materials[1].maxlen
        ratio = math.sqrt(len / roadlen - 1)
        joints = [m2.Vector2() for _ in range(noroad)]
        for i in range(noroad):
            roadvec = roadjoints[i + 1] - roadjoints[i]
            ortroadvec = m2.Vector2(-roadvec[1], roadvec[0]) * ratio
            joints[i] = roadjoints[i] + roadvec * 0.5 + ortroadvec
        mainbeams = [0 for _ in range(3 * noroad - 1)]
        for i in range(noroad):
            mainbeams[3 * i - 2] = Connection.makeCFM(Joint(roadjoints[i]), Joint(joints[i]), materials[1])
            mainbeams[3 * i - 1] = Connection.makeCFM(Joint(roadjoints[i + 1]), Joint(joints[i]), materials[1])
            if i < noroad - 1:
                mainbeams[3 * i] = Connection.makeCFM(Joint(joints[i]), Joint(joints[i + 1]), materials[1])
        if noStat > 0:
            hanging = [j for j in stat]
            connectedm = [j for j in roadjoints[2:-1]] + joints
            connecteds = [a, b]
            i = 0
            change = False
            while len(hanging) > 0:
                dist2 = width ** 2
                minj = 0
                for j in connecteds:
                    vec = hanging[i] - j
                    dist2t = vec * vec
                    if dist2t < dist2:
                        dist2 = dist2t
                        minj = j

                if dist2 < (1.5 * materials[1].maxlen) ** 2:
                    vec = hanging[i] - j
                    dist = math.sqrt(dist2)
                    ratio = dist * math.sin(math.pi / 3)
                    ortnorm = m2.Vector2(vec[1], vec[0]).normal() * ratio
                    connectedm.append(minj + vec * 0.5 + ortnorm)
                    connectedm.append(minj + vec * 0.5 - ortnorm)
                    mainbeams.append(Connection.makeCFM(Joint(hanging[i]), Joint(connectedm[-2]), materials[1]))
                    mainbeams.append(Connection.makeCFM(Joint(hanging[i]), Joint(connectedm[-1]), materials[1]))
                    mainbeams.append(Connection.makeCFM(Joint(minj), Joint(connectedm[-2]), materials[1]))
                    mainbeams.append(Connection.makeCFM(Joint(minj), Joint(connectedm[-1]), materials[1]))
                    connecteds.append(hanging[i])
                    hanging.pop(1)
                    change = True
                    continue

                dist2 = width ** 2
                minj = 0
                for j in connectedm:
                    vec = hanging[i] - j
                    dist2t = vec * vec
                    if dist2t < dist2:
                        dist2 = dist2t
                        minj = j

                if dist2 < (0.9 * materials[1].maxlen) ** 2:
                    connecteds.append(hanging[i])
                    mainbeams.append(Connection.makeCFM(Joint(hanging[i]), Joint(minj), materials[1]))
                    hanging.pop(1)
                    change = True
                    continue
                elif (dist2 >= (0.9 * materials[1].maxlen) ** 2) and (dist2 < (1.9 * materials[1].maxlen) ** 2):
                    vec = hanging[i] - j
                    dist = math.sqrt(dist2)
                    ratio = dist * math.sin(math.pi / 3)
                    ortnorm = m2.Vector2(vec[1], vec[0]).normal() * ratio
                    connectedm.append(minj + vec * 0.5 + ortnorm)
                    connectedm.append(minj + vec * 0.5 - ortnorm)
                    mainbeams.append(Connection.makeCFM(Joint(hanging[i]), Joint(connectedm[-2]), materials[1]))
                    mainbeams.append(Connection.makeCFM(Joint(hanging[i]), Joint(connectedm[-1]), materials[1]))
                    mainbeams.append(Connection.makeCFM(Joint(minj), Joint(connectedm[-2]), materials[1]))
                    mainbeams.append(Connection.makeCFM(Joint(minj), Joint(connectedm[-1]), materials[1]))
                    mainbeams.append(Connection.makeCFM(Joint(connectedm[-2]), Joint(connectedm[-1]), materials[1]))
                    connecteds.append(hanging[i])
                    hanging.pop(1)
                    change = True
                    continue
                i = i + 1

                if i > len(hanging) and not change:
                    hanging = []
                else:
                    i = 0
            joints = connecteds + connectedm
        else:
            joints = joints + roadjoints
        joints = [Joint(bj) for bj in joints]
        bridge = Bridge()
        bridge.points = joints
        bridge.connections = mainbeams
        return bridge
