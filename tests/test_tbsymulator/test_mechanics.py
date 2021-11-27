import tbsymulator.mechanics as mechanics
#import matplotlib.pyplot as plt

def test_sqr():
    assert mechanics.sqr(2) == 4
    assert mechanics.sqr(-2) == 4
    assert mechanics.sqr(3) == 9
    assert mechanics.sqr(-3) == 9
    
def createSampleBridge():
    bridge = mechanics.Bridge()
    
    bridge.points.append(mechanics.Joint([0.0, 0.0], stationary = True))
    bridge.points.append(mechanics.Joint([3.5, 0.0]))
    bridge.points.append(mechanics.Joint([6.5, 0.0]))
    bridge.points.append(mechanics.Joint([10.0, 0.0], stationary = True))
    bridge.points.append(mechanics.Joint([8.0, 2.0]))
    bridge.points.append(mechanics.Joint([5.0, 2.0]))
    bridge.points.append(mechanics.Joint([2.0, 2.0]))
    bridge.points.append(mechanics.Joint([5.0, 5.0]))
    
    defMaxCompression = 0.9
    defMaxStrech = 1.1
    defCompressionForceRate = 1e3
    defStrechForceRate = 1e3
    defMass = 20
    
    # podłoże
    bridge.connections.append(mechanics.Connection(bridge.points[0], bridge.points[1], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    bridge.connections.append(mechanics.Connection(bridge.points[1], bridge.points[2], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    bridge.connections.append(mechanics.Connection(bridge.points[2], bridge.points[3], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    
    # słupki
    bridge.connections.append(mechanics.Connection(bridge.points[0], bridge.points[6], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    bridge.connections.append(mechanics.Connection(bridge.points[1], bridge.points[6], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    bridge.connections.append(mechanics.Connection(bridge.points[1], bridge.points[5], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    bridge.connections.append(mechanics.Connection(bridge.points[2], bridge.points[5], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    bridge.connections.append(mechanics.Connection(bridge.points[2], bridge.points[4], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    bridge.connections.append(mechanics.Connection(bridge.points[3], bridge.points[4], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    
    # liny
    bridge.connections.append(mechanics.Connection(bridge.points[6], bridge.points[5], 1, 0, 0, 1.05*defMaxStrech, 1.2*defStrechForceRate))
    bridge.connections.append(mechanics.Connection(bridge.points[5], bridge.points[4], 1, 0, 0, 1.05*defMaxStrech, 1.2*defStrechForceRate))
    
    # huśtawka
    bridge.connections.append(mechanics.Connection(bridge.points[6], bridge.points[7], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    
    return bridge
    
    
def createSampleBridgePendulum():
    
    bridge = mechanics.Bridge()
    
    bridge.points.append(mechanics.Joint([0.0, 0.0], stationary = True))
    bridge.points.append(mechanics.Joint([3.5, 0.0]))
        
    defMaxCompression = 0.9
    defMaxStrech = 1.1
    defCompressionForceRate = 1e4
    defStrechForceRate = 1e4
    defMass = 20
    
    bridge.connections.append(mechanics.Connection(bridge.points[0], bridge.points[1], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))
    
    return bridge
    
    
def test_createSampleBridge():
    assert isinstance(createSampleBridge(), mechanics.Bridge)
    assert isinstance(createSampleBridgePendulum(), mechanics.Bridge)
    
    
def test_simulation():
    bridge = createSampleBridgePendulum()
    #bridge = createSampleBridge()
    deltaTime = 1e-6
    time = 0.0
    
    it = 0
    
    endTime = 3
    
    print()
    print("time", "dt", "strain", "X", "Y", "Vx", "Vy", "V")
    
    while time < endTime:
        deltaTime = mechanics.simulateTimeStep(bridge, deltaTime, tol = 1e-2)
        time += deltaTime
        it += 1
        #if it % 1000 == 0 or time >= endTime: 
        print(time, deltaTime, bridge.connections[len(bridge.connections)-1].getStrain(), bridge.points[len(bridge.points)-1].position.x, bridge.points[len(bridge.points)-1].position.y, bridge.points[len(bridge.points)-1].velocity.x, bridge.points[len(bridge.points)-1].velocity.y, bridge.points[len(bridge.points)-1].velocity.length())
            
            #print()
            #print(it, time, "\t", deltaTime)

            #print(bridge.points[len(bridge.points)-1])
            #print(bridge.connections[len(bridge.connections)-1].getStrain())

            #for point in bridge.points:
                #print(point.position)
            
            #for connection in bridge.connections:
                #print(connection.getStrain())
    
    #plt.figure()

    #for connection in bridge.connections:
        
        #s = connection.getStrain()
        #if not connection.broken:
            #plt.plot([connection.jointA.position.x, connection.jointB.position.x], [connection.jointA.position.y, connection.jointB.position.y])
    
    #plt.savefig("img.png")
    #plt.close()
        
  
    
    #print()
    #print(len(bridge.points))
    
    #for i in range(len(bridge.points)):
        #print(i, bridge.points[i].position.x, bridge.points[i].position.y)
        
    #print(len(bridge.connections))
    #for connection in bridge.connections:
        #print(bridge.points.index(connection.jointA), bridge.points.index(connection.jointB), connection.getStrain())
  
    
        
    
