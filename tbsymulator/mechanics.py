from math import sqrt
from math import exp
import tbutils.math2d as m2
from threading import Thread
from time import sleep


def simulateTimeStep(bridge, timeStep: float = 1e-6, gravity: m2.Vector2 = m2.Vector2(0, -9.81),
                     resistance: float = 1e-3, tol: float = 1e-3, realBrakes: bool = False,
                     toleranceCountDependent: bool = False, safeBreaking: bool = False, relaxationMode: float = 0.0):
    copyJoints = []
    orginalJoints = [joint.copy() for joint in bridge.points]

    it = 0
    goldProportion = (sqrt(5) - 1) / 2
    pointCount = len(bridge.points)
    delta = 0

    while (delta > tol * {True: pointCount, False: 1.0}[toleranceCountDependent]) or (it == 0):

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
                connection.addIntertia()

            if i == 0:
                expResistance: float = exp(-2 * timeStep * resistance)
                copyJoints = [joint.copy().move(2 * timeStep, expResistance) for joint in bridge.points]
                # for joint in bridge.points:
                # copyJoints.append(joint.copy().move(2 * timeStep, expResistance))

            expResistance: float = exp(-timeStep * resistance)
            for joint in bridge.points:
                joint.move(timeStep, expResistance)

        delta = sum(bridge.points[i].calcDelta(copyJoints[i]) for i in range(len(copyJoints)))

        # delta = 0
        # for i in range(len(copyJoints)):
        # delta += bridge.points[i].calcDelta(copyJoints[i])

        copyJoints.clear()
        
    if timeStep < relaxationMode:
        for joint in bridge.points:
            joint.velocity /= 2

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

    if timeStep < relaxationMode:
        for joint in bridge.points:
            joint.velocity /= 2

    return timeStep * 2

def simulateTimeStepForAI(bridge, timeStep: float = 1e-6, tol : float = 1e-3, toleranceCountDependent : float = True, gravity: m2.Vector2 = m2.Vector2(0, -9.81), relaxationValue : float = 1e-3):
    return simulateTimeStep(bridge = bridge, timeStep = timeStep, tol = tol, toleranceCountDependent = toleranceCountDependent, gravity = gravity, resistance = 0.0, relaxationMode = relaxationValue)

def checkIfBridgeWillSurvive(bridge, velocityTolerance : float = 1e-6, minTime : float = 1, maxTime : float = 1000):
    
    endTime = 15
    time = 0.0
    prevFrame = 0.0
    it = 0
    deltaTime = 1e-6
    velocity : float = 0.0
    
    while time < maxTime:
        deltaTime = simulateTimeStepForAI(bridge, deltaTime)
        time += deltaTime
        for connection in bridge.connections:
            if connection.broken:
                return False
        if (time >= minTime) and (max(j.velocity.length() for j in bridge.points) <= velocityTolerance):
            return True
    
    return True


def simulate(bridge, minTimeStep: float = 1e-6, maxTime: float = 5.0, timeStep: float = 1e-6,
             interval: float = 0.05, gravity: m2.Vector2 = m2.Vector2(0, -9.81)):
    time = 0
    strains = []
    break_moments = [-1.0 for _ in range(len(bridge.connections))]
    next_frame = interval
    road_broke = False
    while not road_broke and time < maxTime:
        timeStep = simulateTimeStepForAI(bridge=bridge, timeStep=timeStep, gravity=gravity)
        time += timeStep
        timeStep = min(max(timeStep, minTimeStep), interval)
        # print(f'{time:0.6f}')
        if time >= next_frame:
            strains.append([con.getStrain() for con in bridge.connections])
            next_frame += interval
            print(f'{time:0.6f}\t{max(strains[-1]):0.4f}')
        for i, con in enumerate(bridge.connections):
            if con.broken and break_moments[i] == -1.0:
                break_moments[i] = time
                if con.material == bridge.materials[0]:
                    road_broke = True
    strains.append([con.getStrain() for con in bridge.connections])
    return time, strains, break_moments


class SimulationThread(Thread):

    def __init__(self, bridge, timeStep: float = 1e-6, gravity: m2.Vector2 = m2.Vector2(0, -9.81),
                 resistance: float = 1e-3, tol: float = 1e-3, realBrakes: bool = False,
                 toleranceCountDependent: bool = False, safeBreaking: bool = False, relaxationMode: float = 0.0,
                 makeAnimation: bool = False, animationSize: (int, int) = (640, 480), animationFPS: float = 60.0):
        self.bridge = bridge
        self.timeStep = timeStep
        self.gravity = gravity
        self.resistance = resistance
        self.tol = tol
        self.realBrakes = realBrakes
        self.toleranceCountDependent = toleranceCountDependent
        self.safeBreaking = safeBreaking
        self.relaxationMode = relaxationMode

        self.time: float = 0
        self.running = True
        self.pause = False
        self.makeAnimation = makeAnimation
        self.animation = []
        self.animationFPS = animationFPS
        self.animationSize = animationSize
        self.exceptions = []
        Thread.__init__(self)

    def run(self):
        lastFrameTime: float = 0.0
        while self.running:
            # print(f'Inside: {self.timeStep:0.6f}\t{self.maxSpeed():0.6f}\t{self.maxSpeedv2():0.6f}')
            try:
                self.timeStep = simulateTimeStep(bridge=self.bridge, timeStep=self.timeStep, gravity=self.gravity,
                                                 resistance=self.resistance, tol=self.tol, realBrakes=self.realBrakes,
                                                 toleranceCountDependent=self.toleranceCountDependent,
                                                 safeBreaking=self.safeBreaking, relaxationMode=self.relaxationMode)
                if self.makeAnimation and (self.time - lastFrameTime >= 1 / self.animationFPS):
                    lastFrameTime = self.time;
                    self.animation.append((self.time, self.bridge.getModelForRender(size=self.animationSize)))
            except Exception as error:
                self.exceptions.append(error)
                self.pause = True

            self.time += self.timeStep
            while self.running and self.pause:
                sleep(min(0.001, abs(1 / self.animationFPS)))

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
        maxV: float = 0
        for joint in self.bridge.points:
            v = joint.velocity.length()
            if v > maxV:
                maxV = v
        return maxV

    def maxSpeedv2(self):
        return max(joint.velocity.length() for joint in self.bridge.points)
