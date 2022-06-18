"""
Utility module defining all functional parts of bridge model
Consists of classes and helper functions

"""

import tbutils.math2d as m2
from math import exp


def sqr(x):
    return x * x


def inRange(x, lo, hi):
    return (x >= lo) and (x <= hi)


def inStrongRange(x, lo, hi):
    return (x > lo) and (x < hi)


class Joint:
    """
    Class representing joint which is an ending point of the connection beam
    """

    def __init__(self, position: m2.Vector2, stationary: bool = False):
        self.position: m2.Vector2 = m2.Vector2(position)
        self.forces: m2.Vector2 = m2.Vector2()
        self.additionalForce: m2.Vector2 = m2.Vector2()
        self.isStationary: bool = stationary
        self.velocity: m2.Vector2 = m2.Vector2()
        self.inertia: float = 0
        self.indexOnBridge: int = 0
        self.assignOriginalPosition()

    def move(self, time: float, expResistance: float):
        """
        Simulates one time step with using resistance.
        :param time: period for simulation
        :param expResistance: value of exp(resistance)
        
        """
        if (not self.isStationary) and (self.inertia != 0):
            dv: m2.Vector2 = self.forces * (time / self.inertia)
            self.position += (self.velocity + dv / 2.0) * time
            self.velocity += dv
            self.velocity *= expResistance  # exp(-time * resistance)
        return self
    
    def prepare(self):
        """
        Zeroes variables before any time step.
        """
        self.forces.x = self.additionalForce.x
        self.forces.y = self.additionalForce.y
        self.inertia = 0.0

    def assign(self, j):
        """
        Copy all values from j - another instance of Joint.
        """
        self.position = j.position.copy()
        self.forces = j.forces.copy()
        self.isStationary = j.isStationary
        self.velocity = j.velocity.copy()
        self.inertia = j.inertia

    def copy(self):
        """
        Makes copy of the joint.
        """        
        c = Joint(self.position)
        c.assign(self)
        return c

    def calcDelta(self, j):
        """
        Calculates error between self and j.
        """        
        if not self.isStationary:
            mf : float = (self.forces.length() + j.forces.length())/2
            return (self.forces - j.forces).length()/(mf+1.0)
        return 0.0
    
    def getDisplacement(self):
        return self.position - self.originalPosition
    
    def assignOriginalPosition(self):
        self.originalPosition = self.position.copy()

    def __str__(self):
        return "Position = " + str(self.position) + "\tVelocity = " + str(self.velocity) + "\tForces = " + str(
            self.forces) + "\tInertia = " + str(self.inertia) + "\tIsStationary = " + str(self.isStationary)


class Connection:
    """
    Class representing beams/connections of the bridge
    """

    def __init__(self, jointA: Joint, jointB: Joint, mass: float, maxCompression: float, compressionForceRate: float,
                 maxStretch: float, stretchForceRate: float):
        self.jointA: Joint = jointA
        self.jointB: Joint = jointB
        self.mass: float = mass
        self.maxCompression: float = maxCompression
        self.compressionForceRate: float = compressionForceRate
        self.maxStretch: float = maxStretch
        self.stretchForceRate: float = stretchForceRate
        self.length = 0.0  # placeholder
        self.soften: float = 1.0
        self.updateLength()
        self.broken = False
        self.cost = 0.0
        self.material = None
        self.additionalMass = 0.0

    def __str__(self):
        return "Joints: [" + str(self.jointA) + ", " + str(self.jointB) + "]\tMass=" + str(
            self.mass) + "\tMaxCompression=" + str(self.maxCompression) + "\tCompressionForceRate=" + str(
            self.compressionForceRate) + "\tMaxStretch=" + str(self.maxStretch) + "\tStretchForceRate=" + str(
            self.stretchForceRate) + "\tBroken: " + str(self.broken)

    def updateLength(self):
        """
        Calculates length as distance between jointA and jointB
        """
        self.length: float = (self.jointA.position - self.jointB.position).length()
        self.jointA.assignOriginalPosition()
        self.jointB.assignOriginalPosition()

    @staticmethod
    def makeCFM(jointA: Joint, jointB: Joint, material):
        """
        makeConnectionFromMaterial
        Static method to construct connection based on ending points and material
        :param jointA: First point of connection
        :param jointB: Second point of connection
        :param material: Material used for connection
        :return: Connection between A and B
        """
        c = Connection(jointA, jointB, 0, material.maxCom, material.comFR, material.maxStr, material.strFR)
        c.mass = c.length * material.linDen
        c.addCost(c.length * material.cost)
        c.material = material
        return c

    def getForce(self):  # for jointA / Force jointB = - Force jointA
        """
        Returns force which is made by the connection.
        """
        if self.length > 0:
            v: m2.Vector2 = (self.jointA.position - self.jointB.position)
            currentLength: float = v.length()
            if currentLength < self.length:
                return v.normal() * (-self.compressionForceRate * (currentLength - self.length) / self.length / self.soften)
            if currentLength > self.length:
                return v.normal() * (-self.stretchForceRate * (currentLength - self.length) / self.length / self.soften)
        return m2.Vector2()

    def addForces(self, gravity: m2.Vector2 = m2.Vector2()):
        """
        Adds made forces to joints.
        """
        if not self.broken:
            forces: m2.Vector2 = self.getForce()
            gm: m2.Vector2 = gravity * ((self.mass + self.additionalMass) / 2)
            self.jointA.forces += gm + forces
            self.jointB.forces += gm - forces

    def addInertia(self):
        """
        Adds intertia forces to joints.
        """
        if not self.broken:
            self.jointA.inertia += (self.mass + self.additionalMass) / 2
            self.jointB.inertia += (self.mass + self.additionalMass) / 2

    def getStrain(self):  
        """
        Returns strain of the connection. It is between 0 and 1.
        """
        if self.broken:
            return 1
        v: m2.Vector2 = (self.jointA.position - self.jointB.position)
        currentLength: float = v.length()

        if self.length == 0:
            return 0.0

        if currentLength > self.length and inStrongRange(self.maxCompression, 0, 1):
            return min(1.0, abs((currentLength - self.length) / self.length / (self.maxCompression - 1)))

        elif currentLength < self.length and self.maxStretch > 1:
            return min(1.0, abs((currentLength - self.length) / self.length / (self.maxStretch - 1)))

        return 0
    
    def getPressure(self):
        return self.getForce().length() / self.material.gauge 
        #return abs(((((self.jointA.position - self.jointB.position).length() - self.length) / self.length)) * self.material.raw.youngModule)

    def checkBreaking(self):
        """
        Checks if connection is broken (because it is too long or too short).
        """
        if not self.broken:
            v: m2.Vector2 = (self.jointA.position - self.jointB.position)
            currentLength: float = v.length()
            if currentLength < self.length * self.maxCompression:
                self.broken = True
            if currentLength > self.length * self.maxStretch:
                self.broken = True
        return self.broken

    def copy(self):
        """
        Makes copy of the joint. 
        """
        c = Connection(jointA=self.jointA, jointB=self.jointB, mass=self.mass, maxCompression=self.maxCompression,
                       compressionForceRate=self.compressionForceRate,
                       maxStretch=self.maxStretch, stretchForceRate=self.stretchForceRate)
        c.broken = self.broken
        c.material = self.material
        c.soften = self.soften
        c.additionalMass = self.additionalMass
        return c

    def breakToTwo(self, where: float = 0.5):
        j1 = Joint((self.jointA.position * where + self.jointB.position * (1 - where)))
        j1.velocity = self.jointA.velocity * where + self.jointB.velocity * (1 - where)
        j2 = j1.copy()
        c1 = Connection(self.jointA, j1, self.mass * where, self.maxCompression, self.compressionForceRate,
                        self.maxStretch, self.stretchForceRate)
        c2 = Connection(j2, self.jointB, self.mass * (1.0 - where), self.maxCompression, self.compressionForceRate,
                        self.maxStretch, self.stretchForceRate)
        return j1, j2, c1, c2

    def addCost(self, cost: float):
        """
        Method to alter value of cost attribute of the connection
        :param cost: new cost value
        """

        self.cost = cost

    def update(self):
        """
        Utility method to update length dependant attributes
        """
        self.length = (self.jointA.position - self.jointB.position).length()
        self.mass = self.length * self.material.linDen
        self.cost = self.length * self.material.cost


class Bridge:
    """
    Class representing model of the bridge

    Note: A valid material list consist of at least two materials
       where: 0 - road material
              1 - main structure material
            ... - other support materials
    Road materials at different indexes will not be recognised as valid road material
    """

    def __init__(self, roadStrains : float = 0.0): # road strains in kg per meter
        self.points = []
        self.connections = []
        self.materials = []
        self.roadStrains = roadStrains

    def copy(self):
        """
        Makes depth copy of the bridge.
        """
        b = Bridge(roadStrains=self.roadStrains)
        b.materials = self.materials.copy()

        for i, p in enumerate(self.points):
            p.indexOnBridge = i
            b.points.append(p.copy())

        for connection in self.connections:
            c = connection.copy()
            c.jointA = b.points[c.jointA.indexOnBridge]
            c.jointB = b.points[c.jointB.indexOnBridge]
            b.connections.append(c)

        return b

    def getModelForRender(self, size: (int, int) = None,
                          bounds: float = 1.3, displacementScale: float=1.0):
        """
        Returns vector model of the bridge.
        :param size:
        :param bounds:
        :return: tuple of two lists of tuples: with lines: (x1, y1, x2, y2, strain, force), with joints: (x, y, isStationary)
        """
        lines = []
        points = []
        i = 0
        for i, p in enumerate(self.points):
            p.indexOnBridge = i

        if i == 0:
            return lines, points,

        epsilon: float = +1e-38

        rx: float = 0.0
        ry: float = 0.0
        k: float = 1.0
        displacementScale -= 1.0;

        if size is not None:
            maxX: float = max([p.position.x for p in self.points if p.isStationary], default=0.0)
            maxY: float = max([p.position.y for p in self.points if p.isStationary], default=0.0)
            minX: float = min([p.position.x for p in self.points if p.isStationary], default=0.0)
            minY: float = min([p.position.y for p in self.points if p.isStationary], default=0.0)

            k = min(size[0] / float(maxX - minX + epsilon), size[1] / float(maxY - minY + epsilon)) / bounds
            rx = -float(maxX + minX) / 2 + size[0] / k / 2
            ry = -float(maxY + minY) / 2 + size[1] / k / 2

        for connection in self.connections:
            if not connection.broken:
                displacementA = connection.jointA.getDisplacement() * displacementScale
                displacementB = connection.jointB.getDisplacement() * displacementScale
                lines.append(((connection.jointA.position.x + displacementA.x + rx) * k, (connection.jointA.position.y + displacementA.y + ry) * k,
                              (connection.jointB.position.x + displacementB.x + rx) * k, (connection.jointB.position.y + displacementB.y + ry) * k,
                              connection.getStrain(), connection.getForce().length()))

        for point in self.points:
            displacement = point.getDisplacement() * displacementScale
            points.append(((point.position.x + displacement.x + rx) * k, (point.position.y + displacement.y + ry) * k, point.isStationary))

        return lines, points

    def render(self, fileName: str, width: int = 640, height: int = 480, bounds: float = 1.3, model=None, drawForces: bool=False, displacementScale: float=1.0):
        """
        Renders the bridge to a png file.
        """

        from PIL import Image, ImageDraw

        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        if model is None:
            model = self.getModelForRender((width, height), bounds, displacementScale=displacementScale)
            
        if drawForces:
            forceScale = 1.0/max(line[5] for line in model[0])            

        for line in model[0]:
            color = line[5]*forceScale if drawForces else line[4]
            draw.line([(line[0], height - line[1] - 1), (line[2], height - line[3] - 1)], width=5,
                      fill=(int(255 * color) + int(255 - 255 * color) * 256), joint="curve")

        colors = {True: "purple", False: "red"}

        for point in model[1]:
            draw.ellipse((point[0] - 5, height - point[1] - 5 - 1, point[0] + 5, height - point[1] + 5 - 1),
                         outline=colors[point[2]], width=3, fill=None)

        image.save(fileName)

    def updateAll(self):
        """
        Utility method to call update method on every connection of the bridge
        """

        for con in self.connections:
            con.update()

    def updateOnJoint(self, joint):
        """
        Utility method to all update method on every connection of the bridge
        with specified ending point
        :param joint: ending point of the connections
        """

        for con in self.connections:
            if con.jointA == joint or con.jointB == joint:
                con.update()

    def getConnectedToJoint(self, joint):
        """
        Method to acquire every connection of the bridge
        with specified ending point
        :param joint: ending point of the connections
        :return: list of connections
        """

        return [con for con in self.connections if con.jointA == joint or con.jointB == joint]
    
    def getKineticEnergy(self, gravity : m2.Vector2 = m2.Vector2(0, -9.81)):
        """
        Returns kinetic energy of the bridge.
        """
        return sum(sqr(j.velocity.length()) * j.inertia / 2 - j.position * gravity for j in self.points)

    def getPotentialEnergy(self, gravity : m2.Vector2 = m2.Vector2(0, -9.81)):
        """
        Returns potential energy of the bridge.
        """
        return sum( - j.position * gravity for j in self.points)

    def getEnergy(self, gravity : m2.Vector2 = m2.Vector2(0, -9.81)):
        """
        Returns sum of potential and kinetic energy of the bridge. 
        Do not calculate spring energy.
        """
        return self.getPotentialEnergy(gravity) + self.getKineticEnergy(gravity)
    
    def relaxPendulums(self, gravity : m2.Vector2 = m2.Vector2(0, -9.81)):
        """
        Stops all single pendulums (single connections).
        """
        
        for i, j in enumerate(self.points):
            j.indexOnBridge = i
            j.connectionCount = 0
                    
        for c in self.connections:
            c.jointA.connectionCount += 1
            c.jointB.connectionCount += 1
            
        for j in self.points:        
            if j.connectionCount == 0:
                j.isStationary = True
        
        for c1 in self.connections:
            for c2 in self.connections:
                if c1 != c2:
                    if (c1.jointA.indexOnBridge == c2.jointA.indexOnBridge and c1.jointB.indexOnBridge == c2.jointB.indexOnBridge) or (c1.jointA.indexOnBridge == c2.jointB.indexOnBridge and c1.jointB.indexOnBridge == c2.jointA.indexOnBridge):
                            c1.jointA.connectionCount -= 0.5
                            c1.jointB.connectionCount -= 0.5
            
        gravityTensor = gravity.normal()
            
        for c in self.connections:
            if c.jointA.connectionCount <= 1.01 and (not c.jointA.isStationary):
                c.jointA.position = c.jointB.position + gravityTensor * c.length
            if c.jointB.connectionCount <= 1.01 and (not c.jointB.isStationary):
                c.jointB.position = c.jointA.position + gravityTensor * c.length

    def removeFallings(self):
        """
        Removes all bridge parts which are not connected with any stationary point or another point which is not falling.
        By default every connection is falling.
        """
        for j in self.points:
            j.isConnectedWithStationary = j.isStationary
        
        for i in range(len(self.connections)):
            noFalse = True
            for con in self.connections:
                status = con.jointA.isConnectedWithStationary or con.jointB.isConnectedWithStationary
                con.jointA.isConnectedWithStationary = status
                con.jointB.isConnectedWithStationary = status
                if not status:
                    noFalse = False
            if noFalse:
                break
                        
        for con in self.connections:            
            status = con.jointA.isConnectedWithStationary or con.jointB.isConnectedWithStationary
            con.broken = not status                        
        
    def setSoften(self, newSoften: float):
        """
        Set spring forces of all materials.
        """
        for con in self.connections:
            con.soften = newSoften    
            
    def checkFalls(self, gravity, trigger: float = 1e9):
        """
        Checks if some part of bridge fallen down.
        """
        for c in self.connections:
            if max(c.jointA.position * gravity, c.jointB.position * gravity) >= trigger:
                c.broken = True      
                
    def addAdditionalMassToConnections(self):
        """
        Adds additional mass to the road (like tanks etc.).
        """
        for con in self.connections:
            if con.material == self.materials[0]:
                con.additionalMass = con.length * self.roadStrains
            else:
                con.additionalMass = 0.0                

    def isSemiValid(self):
        """
        Function that checks if there is connection between first two stationary points
        And it also checks additiona strains on roads
        :return: bool
        """
        
        self.addAdditionalMassToConnections()
        
        a = None
        b = None
        for j in self.points:
            if j.isStationary:
                if a is None:
                    a = j
                elif b is None:
                    b = j
                    break
        if a is None or b is None:
            return False  # missing stationary points
                      
        for j in self.points:
            j.connections = []
            j.wasHere = False
        
        for c in self.connections:  
            if c.material == self.materials[0]:
                c.jointA.connections.append(c)
                c.jointB.connections.append(c)
            
        def doit(joint, another):
            if joint.wasHere:
                return False
            joint.wasHere = True
            if joint == another:
                return True
            for c in joint.connections:
                if doit(c.jointA, another) or doit(c.jointB, another):
                    return True
            return False
        
        return doit(a, b)        


class Material:
    """
    Class representing different connection materials
    meant to be used like structure no get or set methods
    and all attributes directly accessible
    """

    def __init__(self, name: str, maxLength: float, linearDensity: float,
                 maxCompression: float, compressionForceRate: float,
                 maxStretch: float, stretchForceRate: float, costPerUnit: float, desc: str = ""):
        """
        Basic method of creating material with its main properties
        :param name: name of the material
        :param maxLength: maximum length for connection
        :param linearDensity: density per unit of measurement
        :param maxCompression: maximum sustainable compression
        :param compressionForceRate: transfer rate of the compression force
        :param maxStretch: maximum sustainable stretch
        :param stretchForceRate: transfer rate of the stretch force
        :param costPerUnit: prize of one unit of measurement
        There is description field to be set if needed
        """
        self.name = name
        self.maxLen = maxLength
        self.linDen: float = linearDensity
        self.maxCom: float = maxCompression
        self.comFR: float = compressionForceRate
        self.maxStr: float = maxStretch
        self.strFR: float = stretchForceRate
        self.cost: float = costPerUnit
        self.desc: str = str(desc)

    def __str__(self):
        return "{" + str(self.name) + ", maxLen: " + str(self.maxLen) + ", linearDensity: " + str(
            self.linDen) + ", maxCompression: " + str(self.maxCom) + ", compressionForceRate: " + str(
            self.comFR) + ", maxStretch: " + str(self.maxStr) + ", stretchForceRate: " + str(
            self.strFR) + ", cost: " + str(self.cost) + ", desc: " + str(self.desc) + "}"


class RawMaterial:
    """
    Class representing raw materials like ferritum, oak etc.
    It will be used for creating Material classes.
    """

    def __init__(self, name: str, density: float, youngModule: float, yieldStrength: float, cost: float,
                 desc: str = ""):
        self.name: str = str(name)
        self.density: float = float(density)
        self.youngModule: float = float(youngModule)
        self.yieldStrength: float = float(yieldStrength)
        self.cost: float = float(cost)
        self.desc: str = str(desc)

    def __str__(self):
        return "{" + self.name + ", density: " + str(self.density) + " [kg/m^3], youngModule: " + str(
            self.youngModule) + " [N/m^2], yieldStrength: " + str(self.yieldStrength) + " [N/m^2], cost: " + str(
            self.cost) + " [$/kg]}"

    def createMaterial(self, subname: str, maxLength: float, gauge: float, line: bool = False, customDesc: str = None):
        if subname is None:
            subname = self.name
        if customDesc is None:
            customDesc = self.desc
        material =  Material(subname, maxLength, linearDensity=gauge * self.density,
                        maxCompression={False: 1 - self.yieldStrength / self.youngModule, True: 0.0}[line],
                        compressionForceRate={False: self.youngModule, True: 0.0}[line] * gauge,
                        maxStretch=1 + self.yieldStrength / self.youngModule, stretchForceRate=self.youngModule * gauge,
                        costPerUnit=self.cost * gauge, desc=customDesc)
        material.gauge = gauge
        material.raw = self
        return material
