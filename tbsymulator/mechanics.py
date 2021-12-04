from math import sqrt
import tbutils.math2d as m2


def simulateTimeStep(bridge, timeStep: float = 1e-6, gravity: m2.Vector2 = m2.Vector2(0, -9.81),
                     resistance: float = 1e-3, tol: float = 1e-12, realBrakes: bool = False,
                     toleranceCountDependent: bool = False, safeBreaking: bool = False):
    copyJoints = []
    orginalJoints = [joint.copy() for joint in bridge.points]

    delta = tol + 1
    it = 0
    goldProportion = (sqrt(5) - 1) / 2

    pointCount = len(bridge.points)

    while delta > tol * {True: pointCount, False: 1.0}[toleranceCountDependent]:

        if it > 0:
            for i in range(len(orginalJoints)):
                bridge.points[i].assign(orginalJoints[i])

        timeStep *= goldProportion

        it += 1

        for i in range(2):

            for joint in bridge.points:
                joint.prepare()

            for connection in bridge.connections:
                connection.addForces(gravity)

            for connection in bridge.connections:
                connection.addInteria()

            if i == 0:
                for joint in bridge.points:
                    copyJoints.append(joint.copy().move(2 * timeStep, resistance))

            for joint in bridge.points:
                joint.move(timeStep, resistance)

        delta = 0
        for i in range(len(copyJoints)):
            delta += bridge.points[i].calcDelta(copyJoints[i])

        copyJoints.clear()

    orginalJoints.clear()

    additions = []
    for connection in bridge.connections:
        if (not connection.broken) and connection.checkBreaking() and realBrakes:
            additions.append(connection.breakToTwo())

    for v in additions:
        bridge.points.append(v[0])
        bridge.points.append(v[1])
        if safeBreaking:
            v[2].maxCompression /= 2
            v[2].maxStrech *= 2
            v[3].maxCompression /= 2
            v[3].maxStrech *= 2
        bridge.connections.append(v[2])
        bridge.connections.append(v[3])
        pointCount += 2

    additions.clear()

    return timeStep * 2
