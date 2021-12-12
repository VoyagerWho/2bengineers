import math
"""
This file contains entire definition of neural networks used in ai
Two main networks:
    one to work on joints
    second to work on connection
packed in one bridge evolver
"""


class NeuralNetwork:
    """
    Base class for neural networks
    """

    def __init__(self, input_no: int, output_no: int, hidden_structure: list):
        self.input_no = input_no
        self.output_no = output_no

    class Neuron:
        def __init__(self, input_weight, in_bias, value, out_weight):
            self.input_weight = input_weight
            self.in_bias = in_bias
            self.value = value
            self.out_weight = out_weight

    class NeuronIO:
        def __init__(self):
            self.value = 0.0

    @staticmethod
    def activation(x: float):
        return 1/(1+math.exp(-x))

    @staticmethod
    def activation_der(x: float):
        a = NeuralNetwork.activation(x)
        return a*(1-a)


class JointAnalyzer(NeuralNetwork):
    """
    NN performing modifications on bridge joints
    Structure:
        Input:  [Joint type {stationary: 0.0, movable: 1.0},
                Min stress of the all connected beams (scaled in range of values),
                Max stress of the all connected beams (scaled in range of values),
                Avg stress of the all connected beams (scaled in range of values),
                Number of the connected beams,]
            Example: [1.0, 0.1, 0.9, 0.8, 2]
        Output: [Whether to use moveJoint() <0.0, 1.0>,
                Whether to use removeJoint() <0.0, 1.0>,
                Whether to use addJoint() <0.0, 1.0>,
                Whether to use addConnection() <0.0, 1.0>,
                Value for first argument <0.0, 1.0>,
                Value for second argument <0.0, 1.0>,]
            Example: [0.95, 0.01, 0.2, 0.8, 0.65, 0.5]
                -> means:
                    call: moveJoint(...,...,0.65,0.5,...)
                    call: addConnection(...,...,0.65,0.5,...)
    """


class ConnectionAnalyzer(NeuralNetwork):
    """
    NN performing modifications on bridge connection
    Structure:
        Input:  [Connection material (scaled in range of values),
                Min stress of the connection (scaled in range of values),
                Max stress of the connection (scaled in range of values),
                Avg stress of the connection (scaled in range of values),
                Time before breaking (scaled by time of whole simulation),]
            Example: [0.0, 0.1, 1.0, 0.8, 1.0]
                -> means:
                    part of the road that collapsed ending simulation
        Output: [Whether to use changeConnectionMaterial() <0.0, 1.0>,
                Whether to use removeConnection() <0.0, 1.0>,
                Value for argument <0.0, 1.0>,]
            Example: [0.95, 0.01, 0.65]
                -> means:
                    call: changeConnectionMaterial(...,...,0.65)
    """


class BridgeEvolver:
    """
    Main class handling evolution of the bridge
    """
