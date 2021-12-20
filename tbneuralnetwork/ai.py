"""
This file contains definition of neural networks used in ai
Two main networks:
    one to work on joints
    second to work on connection
"""
from __future__ import print_function
import math
import os
import neat
import tbsymulator.mechanics as sim
from tbutils.bridgeparts import Bridge
import tbneuralnetwork.nueralnetworkfunctions as nnf

class JointAnalyzer:
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


class ConnectionAnalyzer:
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


class BridgeEvolution:
    """
    Main class for evolving the bridge structure
    """

    def __init__(self, path_to_catalog):
        config_path_joint = os.path.join(path_to_catalog, 'config-feedforward-joint')
        config_path_connection = os.path.join(path_to_catalog, 'config-feedforward-connection')
        self.config_j = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    config_path_joint)

        self.config_c = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    config_path_connection)

        # Create the population, which is the top-level object for a NEAT run.
        self.p_j = neat.Population(self.config_j)
        self.p_c = neat.Population(self.config_c)

        self.winner_j = None
        self.winner_c = None

    def set_reporter(self):
        self.p_j.add_reporter(neat.StdOutReporter(True))
        stats_j = neat.StatisticsReporter()
        self.p_j.add_reporter(stats_j)

        self.p_c.add_reporter(neat.StdOutReporter(True))
        stats_c = neat.StatisticsReporter()
        self.p_c.add_reporter(stats_c)

    def train(self, no_generations: int):
        # Run for up to 300 generations.
        pe_j = neat.ParallelEvaluator(4, eval_genome_j)
        pe_c = neat.ParallelEvaluator(4, eval_genome_c)
        self.winner_j = self.p_j.run(pe_j.evaluate, no_generations)
        self.winner_c = self.p_c.run(pe_c.evaluate, no_generations)

        # Display the winning genome.
        print('\nBest genome:\n{!s}'.format(self.winner_j))

        # Show output of the most fit genome against training data.
        print('\nOutput:')
        winner_net = neat.nn.FeedForwardNetwork.create(self.winner_j, self.config_j)
        for xi, xo in zip(inputs_j, outputs_j):
            output = winner_net.activate(xi)
            print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output))

        # Display the winning genome.
        print('\nBest genome:\n{!s}'.format(self.winner_c))

        # Show output of the most fit genome against training data.
        print('\nOutput:')
        winner_net = neat.nn.FeedForwardNetwork.create(self.winner_c, self.config_c)
        for xi, xo in zip(inputs_c, outputs_c):
            output = winner_net.activate(xi)
            print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output))


inputs_j = []
outputs_j = []

inputs_c = []
outputs_c = []

bridge: Bridge = None
simulation_time = 0.0
strain = 0.0
break_moments = 0.0

def create_inputs_j():
    inputs_j.clear()
    [simulation_time, strain, break_moments] = sim.simulate(bridge)
    strain_min = min(min(s for s in strain))
    strain_max = max(max(s for s in strain))
    def f(x): (x - strain_min) / (strain_max - strain_max)
    for i, j in enumerate(bridge.points):
        indexes = [bridge.connections.index(con) for con in bridge.getConnectedToJoint(j)]
        strain_con = [strain[idx] for idx in indexes]
        inputs_j[i] = ((1.0 if j.isStationary else 0.0), f(min(strain_con)),
                       f(max(strain_con)), f(sum(strain_con) / len(strain_con)),
                       len(strain_con))

    return simulation_time, strain, break_moments


def alter_bridge_j(commands):
    my_bridge = bridge.copy()
    mj = []
    rj = []
    aj = []
    ac = []
    for i, args in enumerate(commands):
        val = (i, args[-2], args[-1], )
        if args[0] > 0.75:
            mj.append(val)
        if args[1] > 0.75:
            rj.append(val)
        if args[2] > 0.75:
            aj.append(val)
        if args[3] > 0.75:
            ac.append(val)
    for c in mj:
        nnf.moveJoint(bridge, c[0], c[1], c[2])
    for c in aj:
        nnf.addJoint(bridge, c[0], c[1], c[2])
    for c in ac:
        nnf.addConnection(bridge, c[0], c[1], c[2])
    for c in rj:
        nnf.removeJoint(bridge, c[0], c[1], c[2])

    return sim.simulate(my_bridge), sum(con.cost for con in my_bridge.connections)


def eval_genome_j(genome, config):
    """
    Scoring function for ai joint
    :param genome: single genome
    :param config: genome class configuration data
    :return: float genome's fitness
    """
    [s_t1, strain_1, _] = create_inputs_j()
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    output = []
    for xi in inputs_j:
        output.append(net.activate(xi))
    [[s_t2, strain_2, _], cost_2] = alter_bridge_j(output)

    dt = math.fabs((s_t2 - s_t1)/s_t1 if s_t1 > 0 else 0)
    s1 = sum(sum(s) for s in strain_1)
    s2 = sum(sum(s) for s in strain_2)
    ds = math.fabs((s2 - s1)/s1 if s1 > 0 else 0)
    cost_1 = sum(con.cost for con in bridge.connections)
    dc = math.fabs((cost_2 - cost_1)/cost_1 if cost_1 > 0 else 0)
    return (5 / (dt + 1) + 3 / (ds + 1) + 2 / (dc + 1)) / 10


def create_inputs_c():
    inputs_c.clear()
    [simulation_time, strain, break_moments] = sim.simulate(bridge)
    strain_min = min(min(s for s in strain))
    strain_max = max(max(s for s in strain))
    def f(x): (x - strain_min) / (strain_max - strain_max)
    for i, con in enumerate(bridge.connections):
        idx = bridge.materials.index(con.material) / len(bridge.materials)
        inputs_c[i] = (idx, f(min(strain[i])),
                       f(max(strain[i])), f(sum(strain[i])/len(strain[i])),
                       break_moments[i]/simulation_time)

    return simulation_time, strain, break_moments


def alter_bridge_c(commands):
    my_bridge = bridge.copy()
    cm = []
    rc = []
    for i, args in enumerate(commands):
        val = (i, args[-1], )
        if args[0] > 0.75:
            cm.append(val)
        if args[1] > 0.75:
            rc.append(val)
    for c in cm:
        nnf.changeConnectionMaterial(bridge, c[0])
    for c in rc:
        nnf.removeConnection(bridge, c[0])

    return sim.simulate(my_bridge), sum(con.cost for con in my_bridge.connections)


def eval_genome_c(genome, config):
    """
    Scoring function for ai connection
    :param genome: single genome
    :param config: genome class configuration data
    :return: float genome's fitness
    """
    [s_t1, strain_1, _] = create_inputs_c()
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    output = []
    for xi in inputs_c:
        output.append(net.activate(xi))
    [[s_t2, strain_2, _], cost_2] = alter_bridge_c(output)

    dt = math.fabs((s_t2 - s_t1) / s_t1 if s_t1 > 0 else 0)
    s1 = sum(sum(s) for s in strain_1)
    s2 = sum(sum(s) for s in strain_2)
    ds = math.fabs((s2 - s1) / s1 if s1 > 0 else 0)
    cost_1 = sum(con.cost for con in bridge.connections)
    dc = math.fabs((cost_2 - cost_1) / cost_1 if cost_1 > 0 else 0)
    return (5 / (dt + 1) + 3 / (ds + 1) + 2 / (dc + 1)) / 10


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    chamber = BridgeEvolution(local_dir)
    chamber.set_reporter()
    chamber.train(400)
