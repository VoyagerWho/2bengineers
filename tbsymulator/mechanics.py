import math
import tbsymulator.math2d as m2

def sqr(x):
    return x * x

class Joint:
    
    def __init__(self, position : m2.Vector2, stationary : bool = False):
        self.position : m2.Vector2 = m2.Vector2(position)
        self.forces : m2.Vector2 = m2.Vector2()
        self.isStationary : bool = stationary
        self.velocity : m2.Vector2 = m2.Vector2()
        self.interia : float = 0
        
    def move(self, time : float, resistance : float):
        if (not self.isStationary) and (self.interia != 0):
            a : m2.Vector2 = self.forces/self.interia
            self.position += self.velocity * time + a * (sqr(time)/2)
            self.velocity += a * time
            self.velocity *= math.exp(-time*resistance)
        return self
    
    def prepare(self):
        self.forces = m2.Vector2()
        self.interia = 0.0
    
    def copy(self):
        c = Joint(self.position)
        c.forces = self.forces.copy()
        c.isStationary = self.isStationary
        c.velocity = self.velocity.copy()
        c.interia = self.interia
        return c
    
    def assign(self, j):
        self.position = j.position.copy()
        self.forces = j.forces.copy()
        self.isStationary = j.isStationary
        self.velocity = j.velocity.copy()
        self.interia = j.interia
        
    def calcDelta(self, j):      
        return (self.position - j.position).length() + (self.velocity - j.velocity).length() + (self.forces - j.forces).length()
    
    def __str__(self):
        return "Position = " + str(self.position) + "\tVelocity = " + str(self.velocity) + "\tForces = " + str(self.forces) + "\tInteria = " + str(self.interia) + "\tIsStationary = " + str(self.isStationary)
    
        
class Connection:
    
    def __init__(self, jointA : Joint, jointB : Joint, mass : float, maxCompression : float, compressionForceRate : float, maxStrech : float, strechForceRate : float):
        self.jointA : Joint = jointA
        self.jointB : Joint = jointB
        self.mass : float = mass
        self.maxCompression : float = maxCompression
        self.compressionForceRate : float = compressionForceRate
        self.maxStrech : float = maxStrech
        self.strechForceRate : float = strechForceRate
        self.length : float = (self.jointA.position - self.jointB.position).length()
        self.broken = False
        
    def getForce(self): # for jointA / Force jointB = - Force jointA
        v : m2.Vector2 = (self.jointA.position - self.jointB.position)
        currentLength : float = v.length()
        if currentLength < self.length:
            return v.normal() * (-self.compressionForceRate * sqr(currentLength - self.length) / 2)
        if currentLength > self.length:
            return v.normal() * (-self.strechForceRate * sqr(currentLength - self.length) / 2)
        return m2.Vector2()
        
    def addForces(self, gravity : m2.Vector2 = m2.Vector2()):
        if not self.broken:
            forces : m2.Vector2 = self.getForce()
            gm : m2.Vector2 = gravity * (self.mass / 2)
            if self.jointA != None:
                self.jointA.forces += gm + forces
            if self.jointB != None:
                self.jointB.forces += gm - forces
            
    def addInteria(self):
        if not self.broken:
            v : m2.Vector2 = (self.jointA.position - self.jointB.position)
            forcesA : float = self.jointA.forces.length()
            forcesB : float = self.jointB.forces.length()
            if self.jointA != None:
                self.jointA.interia += self.mass/2 + abs(self.jointA.forces.x * v.y - self.jointA.forces.y * v.x)*self.mass/12/forcesA
            if self.jointB != None:
                self.jointB.interia += self.mass/2 + abs(self.jointB.forces.x * v.y - self.jointB.forces.y * v.x)*self.mass/12/forcesB
                
    def getStrain(self): # do animacji
        if self.broken:
            return 1
        v : m2.Vector2 = (self.jointA.position - self.jointB.position)
        currentLength : float = v.length()
        
        if self.length == 0:
            return 0
        
        if currentLength > self.length:
            return abs((currentLength-self.length) / self.length / (self.maxCompression-1))
              
        if currentLength < self.length:
            return abs((currentLength-self.length) / self.length / (self.maxStrech-1))
            
        return 0
                
    def checkBreaking(self):
        if not self.broken:
            v : m2.Vector2 = (self.jointA.position - self.jointB.position)
            currentLength : float = v.length()
            if currentLength < self.length * self.maxCompression:
                self.broken = True
            if currentLength > self.length * self.maxStrech:
                self.broken = True
        return self.broken
        
        
        
class Bridge:
    
    def __init__(self):
        self.points = []
        self.connections = []
    
    
def simulateTimeStep(bridge, timeStep : float = 1e-6, gravity : m2.Vector2 = m2.Vector2(0, -9.81), resistance : float = 1e-3, tol : float = 1e-12):
   
    copyJoints = []
    orginalJoints = []
    for joint in bridge.points:
        orginalJoints.append(joint.copy())
        
    delta = tol + 1
    it = 0
    
    while delta > tol:
        
        if it > 0:
            for i in range(len(orginalJoints)):
                bridge.points[i].assign(orginalJoints[i])
            timeStep *= (math.sqrt(5)-1)/2
                
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
                    copyJoints.append(joint.copy().move(2*timeStep, resistance))
                    
            for joint in bridge.points:
                joint.move(timeStep, resistance)
        
        delta = 0
        for i in range(len(copyJoints)):
            delta += bridge.points[i].calcDelta(copyJoints[i])
        
        copyJoints.clear()
    
    orginalJoints.clear()
    
    for connection in bridge.connections:
        connection.checkBreaking()
    
    return timeStep * 2 
