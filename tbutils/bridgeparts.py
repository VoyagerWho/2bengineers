"""
Utility module defining all functional parts of bridge model
Consists of classes and helper functions

"""
from __future__ import annotations
import tbutils.math2d as m2
from typing import List, Tuple


class Joint:
    """
    Class representing joint which is an ending point of the connection beam
    """

    def __init__(self, position: m2.Vector2, stationary: bool = False):
        self.position: m2.Vector2 = m2.Vector2(position)
        self.isStationary: bool = stationary
        self.indexOnBridge: int = 0

    def copy(self):
        """
        Makes copy of the joint
        """        
        j = Joint(self.position.copy(), self.isStationary)
        return j

    def __str__(self):
        return "Position = " + str(self.position) + "\tIsStationary = " + str(self.isStationary)


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
        self.length: float = 0.0  # placeholder
        self.cost: float = 0.0
        self.soften: float = 1.0
        self.broken: bool = False
        self.material: Material or None = None
        self.additionalMass: float = 0.0
        self.update()

    def __str__(self):
        return "Joints: [" + str(self.jointA) + ", " + str(self.jointB) + "]\tMass=" + str(
            self.mass) + "\tMaxCompression=" + str(self.maxCompression) + "\tCompressionForceRate=" + str(
            self.compressionForceRate) + "\tMaxStretch=" + str(self.maxStretch) + "\tStretchForceRate=" + str(
            self.stretchForceRate) + "\tBroken: " + str(self.broken)

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
        c.material = material
        c.update()
        return c

    def copy(self) -> Connection:
        """
        Makes copy of the connection
        """
        c = Connection(jointA=self.jointA, jointB=self.jointB, mass=self.mass, maxCompression=self.maxCompression,
                       compressionForceRate=self.compressionForceRate,
                       maxStretch=self.maxStretch, stretchForceRate=self.stretchForceRate)
        c.broken = self.broken
        c.material = self.material
        c.soften = self.soften
        c.additionalMass = self.additionalMass
        c.update()
        return c

    def update(self):
        """
        Utility method to update length dependant attributes
        """
        if self.material:
            self.length = (self.jointA.position - self.jointB.position).length()
            self.mass = self.length * self.material.linDen
            self.cost = self.length * self.material.cost


class Bridge:
    """
    Class representing model of the bridge
    """

    def __init__(self, roadStrains : float = 0.0):  # road strains in kg per meter
        self.points: List[Joint] = []
        self.connections: List[Connection] = []
        self.materials: List[Material] = []
        self.roadStrains: float = roadStrains

    def copy(self) -> Bridge:
        """
        Makes deep copy of the bridge
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

    def getModelForRender(self, size: (int, int) = None, bounds: float = 1.3) \
            -> Tuple[List[Tuple[float, float, float, float, float] or None], Tuple[float, float, bool] or None]:
        """
        Returns vector model of the bridge
        :param size: Image size
        :param bounds: Extra empty space around model
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
            maxX: float = max([p.position.x for p in self.points], default=0.0)
            maxY: float = max([p.position.y for p in self.points], default=0.0)
            minX: float = min([p.position.x for p in self.points], default=0.0)
            minY: float = min([p.position.y for p in self.points], default=0.0)

            k = min(size[0] / float(maxX - minX + epsilon), size[1] / float(maxY - minY + epsilon)) / bounds
            rx = -float(maxX + minX) / 2 + size[0] / k / 2
            ry = -float(maxY + minY) / 2 + size[1] / k / 2

        for connection in self.connections:
            if not connection.broken:
                lines.append(((connection.jointA.position.x + rx) * k, (connection.jointA.position.y + ry) * k,
                              (connection.jointB.position.x + rx) * k, (connection.jointB.position.y + ry) * k,
                              0))

        for point in self.points:
            points.append(((point.position.x + rx) * k, (point.position.y + ry) * k, point.isStationary))

        return lines, points

    def render(self, fileName: str, width: int = 640, height: int = 480, bounds: float = 1.05, model=None) -> None:
        """
        Renders the bridge to a png file
        :param fileName: File name
        :param width: Image width
        :param height: Image height
        :param bounds: Extra empty space around model
        :param model: Bridge to render
        :return: None
        """

        from PIL import Image, ImageDraw

        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        if model is None:
            model = self.getModelForRender((width, height), bounds)

        for line in model[0]:
            # draw.line([(line[0], height - line[1] - 1), (line[2], height - line[3] - 1)], width=5,
            #           fill=(int(255 * line[4]) + int(255 - 255 * line[4]) * 256), joint="curve")
            draw.line([(line[0], height - line[1] - 1), (line[2], height - line[3] - 1)], width=5,
                      fill=0, joint="curve")

        colors = {True: "purple", False: "red"}

        for point in model[1]:
            if point[2]:
                draw.rectangle((point[0] - 5, height - point[1] - 5 - 1, point[0] + 5, height - point[1] + 5 - 1),
                               outline="magenta", width=3, fill="magenta")
            else:
                draw.ellipse((point[0] - 5, height - point[1] - 5 - 1, point[0] + 5, height - point[1] + 5 - 1),
                             outline=colors[point[2]], width=3, fill="red")

        image.save(fileName)

    def updateAll(self) -> None:
        """
        Utility method to call update method on every connection of the bridge
        """

        for con in self.connections:
            con.update()

    def updateOnJoint(self, joint) -> None:
        """
        Utility method to all update method on every connection of the bridge
        with specified ending point
        :param joint: Ending point of the connections
        """

        for con in self.connections:
            if con.jointA == joint or con.jointB == joint:
                con.update()

    def getConnectedToJoint(self, joint) -> List[Connection]:
        """
        Method to acquire every connection of the bridge
        with specified ending point
        :param joint: Ending point of the connections
        :return: List of connections
        """

        return [con for con in self.connections if con.jointA == joint or con.jointB == joint]
                
    def addAdditionalMassToConnections(self) -> None:
        """
        Adds additional mass to the road (like tanks etc.)
        """
        for con in self.connections:
            if con.material == self.materials[0]:
                con.additionalMass = con.length * self.roadStrains
            else:
                con.additionalMass = 0.0                

    def isSemiValid(self) -> bool:
        """
        Function that checks if there is connection between first two stationary points
        And it also checks additional strains on roads
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
            c.jointA.connections.append(c)
            c.jointB.connections.append(c)
            
        def traverse(joint, another):
            if joint.wasHere:
                return False
            joint.wasHere = True
            if joint == another:
                return True
            for c in joint.connections:
                if traverse(c.jointA, another) or traverse(c.jointB, another):
                    return True
            return False
        
        return traverse(a, b)


class Material:
    """
    Class representing different connection materials
    meant to be used like structure no get or set methods
    and all attributes directly accessible
    """

    def __init__(self, name: str, maxLength: float, linearDensity: float,
                 maxCompression: float, compressionForceRate: float,
                 maxStretch: float, stretchForceRate: float, costPerUnit: float, surface: float, desc: str = ""):
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
        self.name: str = name
        self.maxLen: float = maxLength
        self.linDen: float = linearDensity
        self.maxCom: float = maxCompression
        self.comFR: float = compressionForceRate
        self.maxStr: float = maxStretch
        self.strFR: float = stretchForceRate
        self.cost: float = costPerUnit
        self.surf: float = surface
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

    def createMaterial(self, subname: str, maxLength: float, gauge: float, line: bool = False, customDesc: str = None) \
            -> Material:
        """
        Function to generate material out of raw substance
        :param subname: Name of the sub group
        :param maxLength: Maximal length of the beams
        :param gauge: Surface size
        :param line: Is it a line like material
        :param customDesc: Extra description
        :return: Material usable for beam creation
        """
        if subname is None:
            subname = self.name
        if customDesc is None:
            customDesc = self.desc
        return Material(subname, maxLength, linearDensity=gauge * self.density,
                        maxCompression={False: 1 - self.yieldStrength / self.youngModule, True: 0.0}[line],
                        compressionForceRate={False: self.youngModule, True: 0.0}[line],
                        maxStretch=1 + self.yieldStrength / self.youngModule, stretchForceRate=self.youngModule,
                        costPerUnit=self.cost * gauge, surface=gauge, desc=customDesc)
