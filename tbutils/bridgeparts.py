import tbutils.math2d as m2
from math import exp


def sqr(x):
    return x * x


def inRange(x, lo, hi):
    return (x >= lo) and (x <= hi)


def inStrongRange(x, lo, hi):
    return (x > lo) and (x < hi)


class Joint:

    def __init__(self, position: m2.Vector2, stationary: bool = False):
        self.position: m2.Vector2 = m2.Vector2(position)
        self.forces: m2.Vector2 = m2.Vector2()
        self.isStationary: bool = stationary
        self.velocity: m2.Vector2 = m2.Vector2()
        self.inertia: float = 0
        self.indexOnBridge: int = 0

    def move(self, time: float, resistance: float):
        if (not self.isStationary) and (self.inertia != 0):
            dv: m2.Vector2 = self.forces * (time / self.inertia)
            self.position += self.velocity * time + dv * (time / 2)
            self.velocity += dv
            self.velocity *= exp(-time * resistance)
        return self

    def prepare(self):
        self.forces = m2.Vector2()
        self.inertia = 0.0

    def assign(self, j):
        self.position = j.position.copy()
        self.forces = j.forces.copy()
        self.isStationary = j.isStationary
        self.velocity = j.velocity.copy()
        self.inertia = j.inertia

    def copy(self):
        c = Joint(self.position)
        c.assign(self)
        return c

    def calcDelta(self, j):
        m: float = (self.position.length()
                    + self.velocity.length()
                    + self.forces.length()
                    + j.position.length()
                    + j.velocity.length()
                    + j.forces.length()) / 2
        if m > 0:
            return (self.position - j.position).length() + (self.velocity - j.velocity).length() + (
                    self.forces - j.forces).length() / m
        return 0

    def __str__(self):
        return "Position = " + str(self.position) + "\tVelocity = " + str(self.velocity) + "\tForces = " + str(
            self.forces) + "\tInertia = " + str(self.inertia) + "\tIsStationary = " + str(self.isStationary)


class Connection:

    def __init__(self, jointA: Joint, jointB: Joint, mass: float, maxCompression: float, compressionForceRate: float,
                 maxStretch: float, stretchForceRate: float):
        self.jointA: Joint = jointA
        self.jointB: Joint = jointB
        self.mass: float = mass
        self.maxCompression: float = maxCompression
        self.compressionForceRate: float = compressionForceRate
        self.maxStretch: float = maxStretch
        self.stretchForceRate: float = stretchForceRate
        self.updateLength()
        self.broken = False
        self.cost = 0.0
        self.material = None
        
    def __str__(self):
        return "Joints: [" + str(self.jointA) + ", " + str(self.jointB) + "]\tMass=" + str(self.mass) + "\tMaxCompression=" + str(self.maxCompression) + "\tCompressionForceRate=" + str(self.compressionForceRate) + "\tMaxStretch=" + str(self.maxStretch) + "\tStretchForceRate=" + str(self.stretchForceRate) + "\tBroken: " + str(self.broken)
        
    def updateLength(self):        
        self.length: float = (self.jointA.position - self.jointB.position).length()

    @staticmethod
    def makeCFM(jointA: Joint, jointB: Joint, material):
        """
        makeConnectionFromMaterial
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
        v: m2.Vector2 = (self.jointA.position - self.jointB.position)
        currentLength: float = v.length()
        if currentLength < self.length:
            return v.normal() * (-self.compressionForceRate * (currentLength - self.length))
        if currentLength > self.length:
            return v.normal() * (-self.stretchForceRate * (currentLength - self.length))
        return m2.Vector2()

    def addForces(self, gravity: m2.Vector2 = m2.Vector2()):
        if not self.broken:
            forces: m2.Vector2 = self.getForce()
            gm: m2.Vector2 = gravity * (self.mass / 2)
            if self.jointA != None:
                self.jointA.forces += gm + forces
            if self.jointB != None:
                self.jointB.forces += gm - forces

    def addIntertia(self):
        if not self.broken:
            v: m2.Vector2 = (self.jointA.position - self.jointB.position)
            forcesA: float = self.jointA.forces.length()
            forcesB: float = self.jointB.forces.length()
            if self.jointA != None:
                self.jointA.inertia += self.mass / 2
            if self.jointB != None:
                self.jointB.inertia += self.mass / 2

    def getStrain(self):  # do animacji
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

    def checkBreaking(self):
        if not self.broken:
            v: m2.Vector2 = (self.jointA.position - self.jointB.position)
            currentLength: float = v.length()
            if currentLength < self.length * self.maxCompression:
                self.broken = True
            if currentLength > self.length * self.maxStretch:
                self.broken = True
        return self.broken

    def copy(self):
        c = Connection(jointA = self.jointA, jointB = self.jointB, mass = self.mass, maxCompression = self.maxCompression, compressionForceRate = self.compressionForceRate,
                       maxStretch = self.maxStretch, stretchForceRate = self.stretchForceRate)
        c.broken = self.broken
        c.material = self.material
        return c

    def breakToTwo(self, where: float = 0.5):
        j1 = Joint((self.jointA.position * where + self.jointB.position * (1 - where)))
        j1.velocity = self.jointA.velocity * where + self.jointB.velocity * (1 - where)
        j2 = j1.copy()
        c1 = Connection(self.jointA, j1, self.mass * where, self.maxCompression, self.compressionForceRate,
                        self.maxStretch, self.stretchForceRate)
        c2 = Connection(j2, self.jointB, self.mass * (1.0 - where), self.maxCompression, self.compressionForceRate,
                        self.maxStretch, self.stretchForceRate)
        return (j1, j2, c1, c2)

    def addCost(self, cost: float):
        self.cost = cost

    def update(self):
        self.length = (self.jointA.position - self.jointB.position).length()
        self.mass = self.length * self.material.linDen
        self.cost = self.length * self.material.cost


class Bridge:

    def __init__(self):
        self.points = []
        self.connections = []
        self.materials = []

    def copy(self):
        b = Bridge()
        b.materials = self.materials

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
                          bounds: float = 1.3):
        """
        :param size:
        :param bounds:
        :return: tuple of two lists of tuples: with lines: (x1, y1, x2, y2, strain), with joints: (x, y, isStationary)
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

        if size is not None:
            maxX: int = 0
            maxY: int = 0
            minX: int = 0
            minY: int = 0
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

            k = min(size[0] / float(maxX - minX + epsilon), size[1] / float(maxY - minY + epsilon)) / bounds
            rx = float(-minX) - float(maxX - minX) / 2 + size[0] / k / 2
            ry = float(-minY) - float(maxY - minY) / 2 + size[1] / k / 2

        for connection in self.connections:
            if not connection.broken:
                lines.append(((connection.jointA.position.x + rx) * k, (connection.jointA.position.y + ry) * k,
                              (connection.jointB.position.x + rx) * k, (connection.jointB.position.y + ry) * k,
                              connection.getStrain()))

        for point in self.points:
            points.append(((point.position.x + rx) * k, (point.position.y + ry) * k, point.isStationary))

        return lines, points

    def render(self, fileName: str, width: int = 640, height: int = 480, bounds: float = 1.3, model = None):

        from PIL import Image, ImageDraw

        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        if model is None:
            model = self.getModelForRender((width, height), bounds)
            
        for line in model[0]:
            draw.line([(line[0], height - line[1] - 1), (line[2], height - line[3] - 1)], width=5,
                      fill=(int(255 * line[4]) + int(255 - 255 * line[4]) * 256), joint="curve")

        colors = {True: "purple", False: "red"}

        for point in model[1]:
            draw.ellipse((point[0] - 5, height - point[1] - 5 - 1, point[0] + 5, height - point[1] + 5 - 1),
                         outline=colors[point[2]], width=3, fill=None)

        image.save(fileName)

    def updateAll(self):
        for con in self.connections:
            con.update()

    def updateOnJoint(self, joint):
        for con in self.connections:
            if con.jointA == joint or con.jointB == joint:
                con.update()

    def getConnectedToJoint(self, joint):
        return [con for con in self.connections if con.jointA == joint or con.jointB == joint]
    
class Material:
    """
    Class representing different connection materials
    meant to be used like structure no get or set methods
    and all attributes directly accessible
    """

    def __init__(self, name: str, maxLength: float, linearDensity: float,
                 maxCompression: float, compressionForceRate: float,
                 maxStretch: float, stretchForceRate: float, costPerUnit: float, desc : str = ""):
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
        self.cost : float = costPerUnit
        self.desc : str = str(desc)

    def __str__(self):
        return "{" + str(self.name) + ", maxLen: " + str(self.maxLen) + ", linearDensity: " + str(self.linearDensity) + ", maxCompression: " + str(self.maxCompression) + ", compressionForceRate: " + str(self.compressionForceRate) + ", maxStretch: " + str(self.maxStretch) + ", stretchForceRate: " + str(self.stretchForceRate) + ", cost: " + str(self.cost) + ", desc: " + str(self.desc) + "}"

class RawMaterial:
    """
    Class representing raw materials like ferritum, oak etc.
    It will be used for creating Material classes.
    """
    def __init__(self, name : str, density : float, youngModule : float, yieldStrenght : float, cost : float, desc : str = ""):
        self.name : str = str(name)
        self.density : float = float(density)
        self.youngModule : float = float(youngModule)
        self.yieldStrenght : float = float(yieldStrenght)
        self.cost : float = float(cost)
        self.desc : str = str(desc)
        
    def __str__(self):
        return "{" + self.name + ", density: " + str(self.density) + " [kg/m^3], youngModule: " + str(self.youngModule) + " [N/m^2], yieldStrenght: " + str(self.yieldStrenght) + " [N/m^2], cost: " + str(self.cost) + " [$/kg]}"
        
    def createMaterial(self, subname : str, maxLength : float, gauge : float, line : bool = False, customDesc : str = None):
        if (subname == None):
            subname = self.name
        if (customDesc == None):
            customDesc = self.desc
        return Material(subname, maxLength, linearDensity = gauge * self.density, 
                        maxCompression = {False: 1-self.yieldStrenght/self.youngModule, True: 0.0}[line], compressionForceRate = {False: self.youngModule, True: 0.0}[line], 
                        maxStretch = 1+self.yieldStrenght/self.youngModule, stretchForceRate = self.youngModule,
                        costPerUnit = self.cost * gauge, desc = customDesc)
    
    
                        
