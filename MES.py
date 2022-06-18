"""
Testing ground and training process for AI models
"""
from tbutils.builder import Builder
import tbutils.math2d as m2
from tbutils.bridgeparts import Joint, Connection, Bridge
import os
from tbsymulator.mechanics import simulate, simulateTimeStep
from tbsymulator.mechanics import checkIfBridgeWillSurvive as check_bridge
import tbutils.materiallist as mat_list
import datetime

if __name__ == '__main__':
  # materials = Builder.createMaterialsList()
  #right = 300.0
  #materials = [mat_list.materialList[0],
               #mat_list.materialList[3],
               #mat_list.materialList[7],
               #mat_list.materialList[19], ]
  #stat = [m2.Vector2(100.0, 250.0), m2.Vector2(right, 250.0), ]
  #bridge = Builder.buildInitial(materials, m2.Vector2(100.0, 300.0), m2.Vector2(right, 300.0), 1, stat)
    
  #for point in bridge.points:
      #point.position.x /= 10
      #point.position.y /= 10
      
  pointList = [m2.Vector2(v) for v in [[10.0, 30.0], [30.0, 30.0],[10.0, 25.0],[30.0, 25.0],[20.0, 32.0],[11.25, 27.5],[8.75, 27.5],[31.25, 27.5],[28.75, 27.5],[25.0, 31.414213562373095],[15.0, 31.414213562373095],[11.085786437626905, 35.70710678118655],[16.914213562373095, 36.70710678118655],[23.085786437626905, 36.70710678118655],[28.914213562373095, 35.70710678118655]]]
  
  asphalt = mat_list.materialDictionary["Basic road"]
  mainMaterial = mat_list.materialDictionary["Steel molding 300x25"]
  
  bridge2 = Bridge()
  bridge2.materials = [asphalt, mainMaterial]
  for i, point in enumerate(pointList):
      bridge2.points.append(Joint(position=point, stationary = i < 4))
      
  jointList = bridge2.points
  bridge2.connections.append(Connection.makeCFM(jointList[0], jointList[10], asphalt))
  bridge2.connections.append(Connection.makeCFM(jointList[4], jointList[10], asphalt))
  bridge2.connections.append(Connection.makeCFM(jointList[4], jointList[9], asphalt))
  bridge2.connections.append(Connection.makeCFM(jointList[1], jointList[9], asphalt))
  
  bridge2.connections.append(Connection.makeCFM(jointList[0], jointList[11], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[12], jointList[11], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[12], jointList[13], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[14], jointList[13], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[14], jointList[1], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[14], jointList[9], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[9], jointList[13], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[4], jointList[13], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[12], jointList[4], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[12], jointList[10], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[10], jointList[11], mainMaterial))
  
  bridge2.connections.append(Connection.makeCFM(jointList[2], jointList[6], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[2], jointList[5], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[0], jointList[6], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[0], jointList[5], mainMaterial))
  
  bridge2.connections.append(Connection.makeCFM(jointList[1], jointList[8], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[1], jointList[7], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[3], jointList[8], mainMaterial))
  bridge2.connections.append(Connection.makeCFM(jointList[3], jointList[7], mainMaterial))
  
  bridge=bridge2
  
  for connection in bridge.connections:
      connection.updateLength()
      
  bridge.points[9].additionalForce = m2.Vector2(0, -147150)    
      
  bridge.render("Default.png", 800, 600)

  print(datetime.datetime.now().time())
  simulate(bridge, accelerationTolerance=1e-6, minTolerance=1e-6)
  
  #t = 0.0
  #i=0
  #timestep = 1e-3
  #while t < 0.001:
      #timestep = simulateTimeStep(bridge, timeStep=timestep)
      #t += timestep
      #i += 1
      #if i % 1000 == 0:
          #print("t =", t, "   max =", max(connection.getForce().length() for connection in bridge.connections))
  
  myPointsToOffcial = [1, 5, 10, 11, 3, 12, 13, 14, 15, 4, 2, 9, 8, 7, 6]
  officialConnections = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (4, 6), (4, 7), (3, 7), (3, 8), (2, 8), (2, 9), (1, 9), (8, 9), (7, 8), (6, 7)]
  
  for index, point in zip(myPointsToOffcial, bridge.points):
      point.index = index
      
  for connection in bridge.connections:
      a = min(connection.jointA.index,connection.jointB.index)
      b = max(connection.jointA.index,connection.jointB.index)
      try:
        connection.index = officialConnections.index((a, b))+1
      except:
        connection.index = -1  
    
  bridge.points.sort(key=lambda j: j.index)
  bridge.connections.sort(key=lambda c: c.index)
      
  print(datetime.datetime.now().time())
  
  for connection in bridge.connections:
      print(connection.getForce().length())
      
  print("max=", max(connection.getForce().length() for connection in bridge.connections), "N")
  print("max=", max(connection.getPressure() for connection in bridge.connections), "Pa")
  
  for i, connection in enumerate(bridge.connections):
    print(connection.index, "[" + str(connection.jointA.position) + " - " + str(connection.jointB.position) + "]: " + str(connection.getForce().length()) + " N   " + str(connection.getPressure()) + " Pa")

  for joint in bridge.points:
      d = joint.getDisplacement()
      print(joint.index, d.length(), "m : ", str(d))

  bridge.render("AfterSim.png", 800, 600, drawForces=True, displacementScale=1000000)

