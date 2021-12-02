from math import sqrt, exp
import tbsymulator.math2d as m2
from enum import Enum

def sqr(x):
    return x * x

def inRange(x, lo, hi):
    return (x >= lo) and (x <= hi)

def inStrongRange(x, lo, hi):
    return (x > lo) and (x < hi)

class Joint:
    
    def __init__(self, position : m2.Vector2, stationary : bool = False):
        self.position : m2.Vector2 = m2.Vector2(position)
        self.forces : m2.Vector2 = m2.Vector2()
        self.isStationary : bool = stationary
        self.velocity : m2.Vector2 = m2.Vector2()
        self.interia : float = 0
        
    def move(self, time : float, resistance : float):
        if (not self.isStationary) and (self.interia != 0):
            dv : m2.Vector2 = self.forces*(time/self.interia)
            self.position += self.velocity * time + dv * (time/2) 
            self.velocity += dv
            self.velocity *= exp(-time*resistance)
        return self
    
    def prepare(self):
        self.forces = m2.Vector2()
        self.interia = 0.0
    
    def assign(self, j):
        self.position = j.position.copy()
        self.forces = j.forces.copy()
        self.isStationary = j.isStationary
        self.velocity = j.velocity.copy()
        self.interia = j.interia
        
    def copy(self):
        c = Joint(self.position)
        c.assign(self)
        return c
        
    def calcDelta(self, j):      
        m : float = (self.position.length() + self.velocity.length() + self.forces.length() + j.position.length() + j.velocity.length() + j.forces.length())/2
        if m > 0:
            return (self.position - j.position).length() + (self.velocity - j.velocity).length() + (self.forces - j.forces).length() / m
        return 0
    
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
            return v.normal() * (-self.compressionForceRate * (currentLength - self.length))
        if currentLength > self.length:
            return v.normal() * (-self.strechForceRate * (currentLength - self.length))
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
                self.jointA.interia += self.mass/2 # + sqr(self.jointA.forces.x / forcesA * v.y - self.jointA.forces.y / forcesA * v.x)*self.mass/12
            if self.jointB != None:
                self.jointB.interia += self.mass/2 # + sqr(self.jointB.forces.x / forcesB * v.y - self.jointB.forces.y * v.x / forcesB)*self.mass/12
                
    def getStrain(self): # do animacji
        if self.broken:
            return 1
        v : m2.Vector2 = (self.jointA.position - self.jointB.position)
        currentLength : float = v.length()
        
        if self.length == 0:
            return 0.0
        
        if currentLength > self.length and inStrongRange(self.maxCompression, 0, 1):
            return min(1.0, abs((currentLength-self.length) / self.length / (self.maxCompression-1)))
              
        elif currentLength < self.length and self.maxStrech > 1:
            return min(1.0, abs((currentLength-self.length) / self.length / (self.maxStrech-1)))
            
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
        
    def copy(self):
        c = Connection(self.jointA, self.jointB, self.mass, self.maxCompression, self.compressionForceRate, self.maxStrech, self.strechForceRate)
        c.broken = self.broken
        return c
        
    def breakToTwo(self, where : float = 0.5):
        j1 = Joint((self.jointA.position*where + self.jointB.position*(1-where)))
        j1.velocity = self.jointA.velocity*where + self.jointB.velocity*(1-where)
        j2 = j1.copy()
        c1 = Connection(self.jointA, j1, self.mass*where, self.maxCompression, self.compressionForceRate, self.maxStrech, self.strechForceRate)
        c2 = Connection(j2, self.jointB, self.mass*(1.0-where), self.maxCompression, self.compressionForceRate, self.maxStrech, self.strechForceRate)
        return (j1, j2, c1, c2)
        
        
class Bridge:
    
    def __init__(self):
        self.points = []
        self.connections = []
    
    def copy(self):
        b = Bridge()
        i : int = 0
        for p in self.points:
            p.indexOnBridge = i
            b.points.append(p.copy())
            i += 1
            
        for connection in self.connections:
            c = connection.copy()
            c.jointA = b.points[c.jointA.indexOnBridge]
            c.jointB = b.points[c.jointB.indexOnBridge]
            b.connections.append(c)
            
        return b   
    
    def getModelForRender(self, size : (int, int) = None, bounds : float = 1.3): # returns a touple of two lists of touples: with lines: (x1, y1, x2, y2, strain), with joints: (x, y, isStationary)
        lines = []
        points = []
        i : int = 0
        for p in self.points:
            p.indexOnBridge = i
            i += 1
            
        if i == 0:
            return result
        
        epsilon : float = +1e-38;
                    
        rx : float = 0.0
        ry : float = 0.0
        k : float = 1.0
        
        if size != None:
            maxX : int = 0
            maxY : int = 0
            minX : int = 0
            minY : int = 0
            for p in self.points:
                if p.isStationary:
                    v = p.position
                    if v.x > maxX:
                        maxX = v.x
                    elif v.x < minX:
                        minX = v.x
                    if v.y > maxY:
                        maxY = v.y
                    elif v.y < minY:
                        minY = v.y
                    
            k = min(size[0]/float(maxX-minX+epsilon), size[1]/float(maxY-minY+epsilon)) / bounds
            rx = float(-minX) - float(maxX-minX)/2 + size[0]/k/2
            ry = float(-minY) - float(maxY-minY)/2 + size[1]/k/2
            
        for connection in self.connections:
            if not connection.broken:
                lines.append(((connection.jointA.position.x+rx)*k, (connection.jointA.position.y+ry)*k, (connection.jointB.position.x+rx)*k, (connection.jointB.position.y+ry)*k, connection.getStrain()))
            
        for point in self.points:
            points.append(((point.position.x+rx)*k, (point.position.y+ry)*k, point.isStationary))
        
        return (lines, points)
        
    
    def render(self, fileName : str, width : int = 640, height : int = 480, bounds : float = 1.3):
        
        from PIL import Image, ImageDraw
        
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
            
        model = self.getModelForRender((width, height), bounds)
        for line in model[0]:
            draw.line([(line[0], height-line[1]-1), (line[2], height-line[3]-1)], width=5, fill=(int(255*line[4]) + int(255-255*line[4])*256), joint="curve")
            
        colors = {True: "purple", False: "red"}
        
        for point in model[1]:
            draw.ellipse((point[0]-5, height-point[1]-5-1, point[0]+5, height-point[1]+5-1), outline=colors[point[2]], width=3, fill=None)
                    
        image.save(fileName)
    
    
def simulateTimeStep(bridge, timeStep : float = 1e-6, gravity : m2.Vector2 = m2.Vector2(0, -9.81), resistance : float = 1e-3, tol : float = 1e-12, realBrakes : bool = False, toleranceCountDependent : bool = False, safeBreaking : bool = False):
   
    copyJoints = []
    orginalJoints = [joint.copy() for joint in bridge.points]
        
    delta = tol+1
    it = 0
    goldProportion = (sqrt(5)-1)/2
    
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
                    copyJoints.append(joint.copy().move(2*timeStep, resistance))
                    
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
