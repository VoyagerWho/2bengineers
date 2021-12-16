from math import sqrt
import tbutils.math2d as m2
from threading import Thread
from time import sleep


def simulateTimeStep(bridge, timeStep: float = 1e-6, gravity: m2.Vector2 = m2.Vector2(0, -9.81),
                     resistance: float = 1e-3, tol: float = 1e-3, realBrakes: bool = False,
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


class SimulationThread(Thread):
    
    def __init__(self, bridge, timeStep: float = 1e-6, gravity: m2.Vector2 = m2.Vector2(0, -9.81),
                resistance: float = 1e-3, tol: float = 1e-3, realBrakes: bool = False,
                toleranceCountDependent: bool = False, safeBreaking: bool = False, makeAnimation : bool = False):
        self.bridge = bridge
        self.timeStep = timeStep
        self.gravity = gravity
        self.resistance = resistance
        self.tol = tol
        self.realBrakes = realBrakes
        self.toleranceCountDependent = toleranceCountDependent
        self.safeBreaking = safeBreaking
        
        self.time : float = 0
        self.running = True
        self.pause = False
        self.makeAnimation = makeAnimation
        self.animation = []
        self.exceptions = []
        Thread.__init__(self)
        
    def run(self):
        while self.running:
            try:
                self.timeStep = simulateTimeStep(bridge = self.bridge, timeStep = self.timeStep, gravity = self.gravity, resistance = self.resistance, tol = self.tol, realBrakes = self.realBrakes, toleranceCountDependent = self.toleranceCountDependent, safeBreaking = self.safeBreaking)
                if self.makeAnimation:
                    self.animation.append((time, self.bridge.getModelForRender()))         
            except Exception as error:
                self.exceptions.append(error)
                self.pause = True
            
            self.time += self.timeStep            
            while self.running and self.pause:
                sleep(0.001)
                
                
        
    def isBroken(self):
        for connection in self.bridge.connections:
            if connection.broken:
                return True
        return False
    
    def stopSimulation(self):
        self.pause = False
        self.running = False
        self.join()
        
    def maxSpeed(self):
        maxV : float = 0
        for joint in self.bridge.points:
            v = joint.velocity.length()
            if v > maxV:
                maxV = v
        return maxV
        
