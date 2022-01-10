from math import sqrt, exp
import tbutils.math2d as m2
from time import sleep, time as getTime

executedSimulation: int = 0
road_broke = False

def simulateTimeStep(bridge, timeStep: float = 1e-6, gravity: m2.Vector2 = m2.Vector2(0, -9.81),
                     resistance: float = 1e-3, tol: float = 1e-3, realBrakes: bool = False,
                     toleranceCountDependent: bool = False, safeBreaking: bool = False, relaxationMode: float = 0.0, enableBreaks: bool = True):
    """
    Function for calculating the next time step for the bridge
    :param bridge: The bridge which is simulated.
    :param timeStep: On the first step: any positive real number, on the each following step: the result of this function.
    :param gravity: Everyone knows what it is.
    :param resistance: Value for breaking the velocity of each part of the bridge.
    :param tol: Toleracne of calculating (positive real number). The bigger value means faster calculation time, but less precision.
    :param realBreakes: For True - broken bridge connection is divided into two connections with points in half of the original connection.
    :param toleranceCountDependent: In case of breaking and realBrakes==True the tolerance will be increased if the count of points will increase.
    :param safeBreaking: When realBrakes==True the created connections has two times more strength to avoid subsequent breaks of them. 
    :param relaxationMode: When timeStep is less than the relaxationMode, velocity is divided by two. It makes slow bridge relaxation. If the value is different than zero, the simulations cannot be used for live-movements (simulating where the parts' velocity and momentum has matter) - for example for simulating the bridge's behavior during an eartch quake or during its destroying.
    :param enableBreaks: If False nothing will break.
    """
    
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
                connection.addInertia()

            if i == 0:
                expResistance: float = exp(-2 * timeStep * resistance)
                copyJoints = [joint.copy().move(2 * timeStep, expResistance) for joint in bridge.points]

            expResistance: float = exp(-timeStep * resistance)
            for joint in bridge.points:
                joint.move(timeStep, expResistance)
                
        delta = sum(bridge.points[i].calcDelta(copyJoints[i]) for i in range(len(copyJoints)))
        copyJoints.clear()

    if timeStep < relaxationMode:      
        v = []
        
        for con in bridge.connections:
            v.append((con.jointA.velocity + con.jointB.velocity)/2)
        
        for i, con in enumerate(bridge.connections):
            if not con.jointA.isStationary:
                con.jointA.velocity = (con.jointA.velocity + v[i])/2
            if not con.jointB.isStationary:
                con.jointB.velocity = (con.jointB.velocity + v[i])/2

    orginalJoints.clear()

    if enableBreaks:    
        
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


def simulateTimeStepForAI(bridge, timeStep: float = 1e-6, tol: float = 1e-3, toleranceCountDependent: float = True, gravity: m2.Vector2 = m2.Vector2(0, -9.81), relaxationValue: float = 1e-3, enableBreaks: bool = True):
    """
    Alias for simulateTimeStep, but with some predifinied default parameters which makes the simulation faster.
    Warning: It uses relaxationValue (alias for: relaxationMode) different than zero.
    """
    return simulateTimeStep(bridge = bridge, timeStep = timeStep, tol = tol, toleranceCountDependent = toleranceCountDependent, gravity = gravity, resistance = 0.0, relaxationMode = relaxationValue, enableBreaks=enableBreaks)


def relaxBridge(bridge, initSoften: float = 1e7, accelerationTolerance: float = 1e-3, gravity: m2.Vector2 = m2.Vector2(0, -9.81)):
    
    soften: float = initSoften
    deltaTime = 1e-6
    it = 0
    
    deltaTime = simulateTimeStepForAI(bridge, deltaTime, gravity=gravity, enableBreaks=False)
    currAcc = max([j.forces.length()/j.inertia for j in bridge.points if (not j.isStationary) and (j.inertia != 0)], default=0.0)
    
    while soften > 1.0 or currAcc > accelerationTolerance:                
        if (currAcc < accelerationTolerance) and soften > 1.0:
            soften = 1.0    
        #bridge.setSoften(soften)
        if soften != 1.0:
            for con in bridge.connections:
                s = con.getStrain()
                if s > 0.3:                
                    con.soften = max(1.0, con.soften*0.9999)
                else:
                    con.soften = min(initSoften, con.soften*1.0001)
        
        if soften == 1.0:
            for j in bridge.points:
                j.velocity = m2.Vector2()
        deltaTime = simulateTimeStep(bridge, deltaTime, gravity=gravity, enableBreaks=False, resistance=min(1.0, soften), relaxationMode=1e-3)
        bridge.checkFalls(gravity)
        currAcc = max([j.forces.length()/j.inertia for j in bridge.points if (not j.isStationary) and (j.inertia != 0)], default=0.0)
        it += 1    
        #if it%100000 == 0:
            #for j in bridge.points:
                #j.velocity = m2.Vector2()
        if it%1000 == 0:
            print(soften, currAcc)
            bridge.render("/dev/shm/relax" + str(it//1000) + ".png")
            
    bridge.setSoften(1.0)
        

def checkIfBridgeWillSurvive(bridge, accelerationTolerance: float = 1e-3, minTime: float = 1, maxTime: float = 1000, gravity: m2.Vector2 = m2.Vector2(0, -9.81)):    
    """
    The function cheks if the bridge can be slow placed without self-destroying (breaking any part). 
    """
    endTime = 15
    time = 0.0
    prevFrame = 0.0
    deltaTime = 1e-6
    
    relaxBridge(bridge, gravity=gravity, accelerationTolerance=accelerationTolerance)

    while time < maxTime:
        deltaTime = simulateTimeStepForAI(bridge, deltaTime, gravity=gravity)
        time += deltaTime
        for connection in bridge.connections:
            if connection.broken:
                return False        
        #print(max(j.forces.length()/j.inertia for j in bridge.points if (not j.isStationary) and (j.inertia != 0)), max(j.velocity.length() for j in bridge.points), step)
        if max([j.forces.length()/j.inertia for j in bridge.points if (not j.isStationary) and (j.inertia != 0)], default=0.0) <= accelerationTolerance:            
            return True

    return True

frameID = 0 #remove after debug

def simulate(bridge, interval: float = 0.05, gravity: m2.Vector2 = m2.Vector2(0, -9.81), accelerationTolerance : float = 1e-2, minTolerance : float = 1e-3):
    """
    Makes all simulation of teh bridge til it is relaxed or road break.
    :param bridge: Bridge for simulation.
    :param interval: Interval of printing information about the simulation.
    :param gravity: What it is everyone knows.
    :param accelerationTolerance: Simulation stops when acceleration of all points is under the value.
    """
    print("Starting new simulation")
    global road_broke
    time = 0
    strains = []
    break_moments = [-1.0 for _ in range(len(bridge.connections))]
    next_frame = interval
    road_broke = False
    maxAcc = 10.0
    prevTimeEfficiency = 0.0
    relaxationValue = 0.001
    relaxationChange = 1.01
    energy = bridge.getPotentialEnergy(gravity)
    prevEnergy = energy
    tolerance = 0.05
    #relaxed = False
    global executedSimulation
    executedSimulation += 1
    it = 0
    
    print("BridgeInfo: ", len(bridge.connections), len(bridge.points))
    bridge.relaxPendulums(gravity)
    bridge.removeFallings()
    #relaxBridge(bridge, gravity=gravity, accelerationTolerance=accelerationTolerance)
    
    global frameID 
    # bridge.render("/dev/shm/test" + str(frameID) + "a.png") #remove after debug
    frameID += 1    #remove after debug
    timeStep: float = 1e-6
    
    while not road_broke and maxAcc > accelerationTolerance:# time < maxTime:
        
        it += 1
        tb = getTime()
        timeStep = simulateTimeStepForAI(bridge=bridge, timeStep=timeStep, gravity=gravity, tol=tolerance, relaxationValue=relaxationValue) 
            
        energy = bridge.getPotentialEnergy(gravity)
        timeEfficiency = abs(prevEnergy-energy)/(getTime() - tb + 1e-9)
        prevEnergy = energy
        
        if timeEfficiency < prevTimeEfficiency:
            relaxationChange = 1/relaxationChange
        relaxationValue = max(1e-6, min(1.0, relaxationValue*relaxationChange))
        prevTimeEfficiency = timeEfficiency
        prevAcc = maxAcc
        maxAcc = max([j.forces.length()/j.inertia for j in bridge.points if (not j.isStationary) and (j.inertia != 0)], default=0.0)
        if (prevAcc - maxAcc) < 0:
            tolerance = max(tolerance * 0.9999, minTolerance)
                    
        #if not relaxed:
            #for con in bridge.connections:
                #con.soften = max(1.0, 0.3 / (con.getStrain() + 1e-7))   
        
        #if maxAcc <= accelerationTolerance and not relaxed:            
            #for con in bridge.connections:
                #con.soften = 1.0
            #relaxed = True
            #maxAcc *= 2
        
        time += timeStep
                        
        #timeStep = min(max(timeStep, minTimeStep), interval)
        #print(f'{time:0.6f}')
        if time >= next_frame:
            strains.append([con.getStrain() for con in bridge.connections])
            next_frame += interval

            print("mechanics.simulate:", it, f'\t{time:0.6f}\t{max(strains[-1], default=0.0):0.4f}', "\tacc=", maxAcc, "\trelax=", relaxationValue, "\ttol=", tolerance,"\tE=", energy, "\tMinY=", min([j.position.y for j in bridge.points], default=0.0))            

        for i, con in enumerate(bridge.connections):
            if con.jointA.position * gravity > gravity.length()**3:
                con.broken = True            
            if con.broken and break_moments[i] == -1.0:
                break_moments[i] = time
                if con.material == bridge.materials[0]:
                    road_broke = True                    
            
    strains.append([con.getStrain() for con in bridge.connections])
    print("Broken: ", road_broke)
    # bridge.render("/dev/shm/test" + str(frameID) + "b.png") #remove after debug
    return time, strains, break_moments
