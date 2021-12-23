import tbsymulator.mechanics as mechanics
import tbutils.bridgeparts as bridgeparts
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from time import sleep


def test_sqr():
    assert bridgeparts.sqr(2) == 4
    assert bridgeparts.sqr(-2) == 4
    assert bridgeparts.sqr(3) == 9
    assert bridgeparts.sqr(-3) == 9


def createSampleBridge():
    bridge = bridgeparts.Bridge()

    bridge.points.append(bridgeparts.Joint([0.0, 0.0], stationary=True))
    bridge.points.append(bridgeparts.Joint([3.5, 0.0]))
    bridge.points.append(bridgeparts.Joint([6.5, 0.0]))
    bridge.points.append(bridgeparts.Joint([10.0, 0.0], stationary=True))
    bridge.points.append(bridgeparts.Joint([8.0, 2.0]))
    bridge.points.append(bridgeparts.Joint([5.0, 2.0]))
    bridge.points.append(bridgeparts.Joint([2.0, 2.0]))
    # bridge.points.append(bridgeparts.Joint([5.0, 5.0]))

    defMaxCompression = 0.9
    defMaxStrech = 1.1
    defCompressionForceRate = 1e4
    defStrechForceRate = 1e4
    defMass = 20

    # podłoże
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[0], bridge.points[1], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[1], bridge.points[2], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[2], bridge.points[3], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))

    # słupki
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[0], bridge.points[6], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[1], bridge.points[6], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[1], bridge.points[5], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[2], bridge.points[5], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[2], bridge.points[4], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[3], bridge.points[4], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))

    # górne
    # bridge.connections.append(bridgeparts.Connection(bridge.points[6], bridge.points[5], 1, 0, 0, 1.05*defMaxStrech, 1.2*defStrechForceRate))
    # bridge.connections.append(bridgeparts.Connection(bridge.points[5], bridge.points[4], 1, 0, 0, 1.05*defMaxStrech, 1.2*defStrechForceRate))
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[6], bridge.points[5], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))
    bridge.connections.append(
        bridgeparts.Connection(bridge.points[5], bridge.points[4], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))

    # huśtawka
    # bridge.connections.append(bridgeparts.Connection(bridge.points[6], bridge.points[7], defMass, defMaxCompression, defCompressionForceRate, defMaxStrech, defStrechForceRate))

    return bridge


def createSampleBridgePendulum():
    bridge = bridgeparts.Bridge()

    bridge.points.append(bridgeparts.Joint([0.0, 0.0], stationary=True))
    bridge.points.append(bridgeparts.Joint([3.5, 0.0]))

    defMaxCompression = 0.9
    defMaxStrech = 1.1
    defCompressionForceRate = 1e4
    defStrechForceRate = 1e4
    defMass = 20

    bridge.connections.append(
        bridgeparts.Connection(bridge.points[0], bridge.points[1], defMass, defMaxCompression, defCompressionForceRate,
                             defMaxStrech, defStrechForceRate))

    return bridge


def test_createSampleBridge():
    assert isinstance(createSampleBridge(), bridgeparts.Bridge)
    assert isinstance(createSampleBridgePendulum(), bridgeparts.Bridge)


def test_CopyBridge():
    b1 = createSampleBridgePendulum()
    b2 = b1.copy()

    b1.connections[0].jointA.position.x = 10
    assert b2.connections[0].jointA.position.x != 10


def test_RenderBridge():
    bridge = createSampleBridge()
    model = bridge.getModelForRender((640, 480))[0]

    assert isinstance(model, list)

    mechanics.simulateTimeStep(bridge, 1e-6, tol=1e-3, resistance=1e-3, realBrakes=True)

    image = Image.new("RGB", (640, 480), "white")
    draw = ImageDraw.Draw(image)

    for line in model:
        assert line[0] >= 0
        assert line[1] >= 0
        assert line[2] >= 0
        assert line[3] >= 0
        assert line[0] < 640
        assert line[1] < 480
        assert line[2] < 640
        assert line[3] < 480
        draw.line([(line[0], 480 - line[1]), (line[2], 480 - line[3])], width=5,
                  fill=(int(255 * line[4]) + int(255 - 255 * line[4]) * 256), joint="curve")

    image.save("/dev/shm/out1.png")
    bridge.render("/dev/shm/out2.png")

def test_AISimulate():
    skip = False
    if skip:
        return

    bridge = createSampleBridge()
    endTime = 15
    time = 0.0
    prevFrame = 0.0
    it = 0
    deltaTime = 1e-6
    v = 10
    
    while v > 1e-3:# time < endTime:
        deltaTime = mechanics.simulateTimeStepForAI(bridge, deltaTime)
        time += deltaTime
        it += 1
        if it % 100 == 0:
            v = max(p.velocity.length() for p in bridge.points)
            print(time, v)


def test_bridgeSurvive():
    bridge = createSampleBridge()
    print(mechanics.checkIfBridgeWillSurvive(bridge))
    print(max(j.velocity.length() for j in bridge.points))
    

def test_RenderBridge2():
    skip = False
    trueRender = True
    if skip:
        return

    bridge = createSampleBridge()
    endTime = 15
    fps = 30
    frameCount = 0
    prevFrame = 0.0
    time = 0.0
    it = 0
    deltaTime = 1e-6

    while time < endTime:
        deltaTime = mechanics.simulateTimeStep(bridge, deltaTime, tol=1e-3, resistance=0.5, realBrakes=True,
                                               toleranceCountDependent=False, relaxationMode = 0.000)
        time += deltaTime
        it += 1
        # deltaTime = min(1.0/fps/2, deltaTime)
        # print(time)

        if time >= prevFrame + 1.0 / fps:
            if trueRender:
                bridge.render("/dev/shm/frame" + str(frameCount) + ".png")
            print("frame: " + str(frameCount))
            frameCount += 1
            prevFrame = time

    print("average dt =", time / it)
    # print(time, deltaTime, bridge.connections[len(bridge.connections)-1].getStrain(), bridge.points[len(bridge.points)-1].position.x, bridge.points[len(bridge.points)-1].position.y, bridge.points[len(bridge.points)-1].velocity.x, bridge.points[len(bridge.points)-1].velocity.y, bridge.points[len(bridge.points)-1].velocity.length())


def test_simulation():
    bridge = createSampleBridgePendulum()
    # bridge = createSampleBridge()
    deltaTime = 1e-6
    time = 0.0

    it = 0

    endTime = 5  # 15 # 20.55s

    timeValues = []
    XValues = []
    YValues = []
    VxValues = []
    VyValues = []
    VValues = []
    strainValues = []

    StdOut = False
    Plots = False

    PlotInterval = 0.01

    PlotTime = -10.0

    if StdOut:
        print()
        print("time", "dt", "strain", "X", "Y", "Vx", "Vy", "V")

    while time < endTime:
        deltaTime = mechanics.simulateTimeStep(bridge, deltaTime, tol=1e-3, resistance=1e-1, realBrakes=True)
        time += deltaTime
        it += 1

        if Plots and (time - PlotTime >= PlotInterval):
            timeValues.append(time)
            XValues.append(bridge.points[len(bridge.points) - 1].position.x)
            YValues.append(bridge.points[len(bridge.points) - 1].position.y)
            VxValues.append(bridge.points[len(bridge.points) - 1].velocity.x)
            VyValues.append(bridge.points[len(bridge.points) - 1].velocity.y)
            VValues.append(bridge.points[len(bridge.points) - 1].velocity.length())
            strainValues.append(bridge.connections[len(bridge.connections) - 1].getStrain())
            PlotTime = time
            if not StdOut:
                print(time)

        if StdOut:
            print(time, deltaTime, bridge.connections[len(bridge.connections) - 1].getStrain(),
                  bridge.points[len(bridge.points) - 1].position.x, bridge.points[len(bridge.points) - 1].position.y,
                  bridge.points[len(bridge.points) - 1].velocity.x, bridge.points[len(bridge.points) - 1].velocity.y,
                  bridge.points[len(bridge.points) - 1].velocity.length())

    if Plots:
        plt.figure()
        plt.plot(timeValues, XValues, ls='-', lw=1, label='X');
        plt.plot(timeValues, YValues, ls='-', lw=1, label='Y');
        plt.plot(timeValues, VxValues, ls='-', lw=1, label='Vx');
        plt.plot(timeValues, VyValues, ls='-', lw=1, label='Vy');
        plt.legend()
        plt.savefig("/dev/shm/Positions.png")
        plt.close()

        fig, ax1 = plt.subplots()
        ax1.plot(timeValues, strainValues, ls='-', lw=1, label='strain');

        ax2 = ax1.twinx()

        ax2.plot(timeValues, VValues, ls='-', color='y', lw=1, label='Velocity');
        fig.legend()
        fig.savefig("/dev/shm/StrainVsVelocity.png")



def test_AsyncRenderBridge2():
    skip = False 
    trueRender = True
    if skip:
        return

    bridge = createSampleBridge()

    simulation = mechanics.SimulationThread(bridge, timeStep = 1e-6, tol=1e-3, resistance=0.5, realBrakes=True, toleranceCountDependent=True)
    simulation.start()
    while simulation.time < 5:
        print("Async t =", simulation.time)
        sleep(0.4)
    
    simulation.stopSimulation()
    
    print("done")
