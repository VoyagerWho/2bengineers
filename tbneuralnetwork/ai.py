"""
This file contains definition of neural networks used in ai
Two main networks:
    one to work on joints
    second to work on connection
"""
from __future__ import print_function
import os
import math

import neat
import tbsymulator.mechanics as sim
from tbutils.bridgeparts import Bridge
import tbneuralnetwork.nueralnetworkfunctions as nnf
import pickle

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
inputs_j = []
outputs_j = []

inputs_c = []
outputs_c = []
bridge_copy: Bridge = None


class BridgeEvolution:
    """
    Main class for evolving the bridge structure
    Requires a bridge to unlock train method for objects
    """
    # For simulations
    bridge: Bridge = None
    budget: float = 0.0
    strain: list = []
    break_moments: list = []

    def __init__(self, path_to_catalog: str):
        """
        Initialization of new set of neural network pair
        :param path_to_catalog: location of catalog with configuration files relative to __main__
        """
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
        """
        Helper function that turns on evolution progress displays on stdout
        """
        self.p_j.add_reporter(neat.StdOutReporter(True))
        self.p_j.add_reporter(neat.StatisticsReporter())

        self.p_c.add_reporter(neat.StdOutReporter(True))
        self.p_c.add_reporter(neat.StatisticsReporter())

    def train(self, no_generations: int):
        """
        Main function that trains network pair wise for limited amount per pair in iteration
        to allow steady progress
        :param no_generations: max amount of evolution per pair in iteration
        """
        if BridgeEvolution.bridge is not None:
            global inputs_j
            global inputs_c
            inputs_j = [() for _ in range(len(BridgeEvolution.bridge.points))]
            inputs_c = [() for _ in range(len(BridgeEvolution.bridge.connections))]
            [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                = sim.simulate(BridgeEvolution.bridge)
            create_inputs()
            BridgeEvolution.budget = 1.1*sum(con.cost for con in BridgeEvolution.bridge.connections)
            # learning of joint:
            
            # print(inputs_c)
            # print(inputs_j)
            global bridge_copy
            bridge_copy = BridgeEvolution.bridge.copy()
            self.winner_j = self.p_j.run(eval_genome_j, no_generations)
            # with open("winner_j.pkl", "rb") as f:
            #   self.winner_j = pickle.load(f)
            # Display the winning genome.
            print('\nBest genome:\n{!s}'.format(self.winner_j))
            winner_net = neat.nn.FeedForwardNetwork.create(self.winner_j, self.config_j)
            output = [winner_net.activate(xi) for xi in inputs_j]
            alter_bridge_j(output, BridgeEvolution.bridge)
            bridge_copy = BridgeEvolution.bridge.copy()
            BridgeEvolution.bridge.render("Train_joint.png")
            inputs_j = [() for _ in range(len(BridgeEvolution.bridge.points))]
            inputs_c = [() for _ in range(len(BridgeEvolution.bridge.connections))]
            [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                = sim.simulate(BridgeEvolution.bridge)
            create_inputs()
            with open("winner_j.pkl", "wb") as f:
                pickle.dump(self.winner_j, f)

            self.winner_c = self.p_c.run(eval_genome_c, no_generations)
            # Display the winning genome.
            print('\nBest genome:\n{!s}'.format(self.winner_c))
            winner_net = neat.nn.FeedForwardNetwork.create(self.winner_c, self.config_c)
            output = [winner_net.activate(xi) for xi in inputs_c]
            alter_bridge_c(output, BridgeEvolution.bridge)
            BridgeEvolution.bridge.render("Train_connection.png")
            with open("winner_c.pkl", "wb") as f:
                pickle.dump(self.winner_c, f)

    def load(self):
        with open("winner_j.pkl", "rb") as f:
            self.winner_j = pickle.load(f)
        with open("winner_c.pkl", "rb") as f:
            self.winner_c = pickle.load(f)

    def save(self):
        with open("winner_j.pkl", "wb") as f:
            pickle.dump(self.winner_j, f)
        with open("winner_c.pkl", "wb") as f:
            pickle.dump(self.winner_c, f)

    def upgrade(self, mark: str, no_iterations: int):
        """
        Method performing evaluation of the bridge by both networks
        :param mark: signature of the result files
        :param no_iterations: number of updates per network
        """

        if BridgeEvolution.bridge is not None:
            global inputs_j
            global inputs_c
            inputs_j = [() for _ in range(len(BridgeEvolution.bridge.points))]
            inputs_c = [() for _ in range(len(BridgeEvolution.bridge.connections))]
            [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                = sim.simulate(BridgeEvolution.bridge)
            create_inputs()
            BridgeEvolution.budget = 1.1 * sum(con.cost for con in BridgeEvolution.bridge.connections)
            print(inputs_c)
            print(inputs_j)
            global bridge_copy
            bridge_copy = BridgeEvolution.bridge.copy()
            for i in range(no_iterations):
                net = neat.nn.FeedForwardNetwork.create(self.winner_j, self.config_j)
                output = [net.activate(xi) for xi in inputs_j]
                alter_bridge_j(output, BridgeEvolution.bridge)
                inputs_j = [() for _ in range(len(BridgeEvolution.bridge.points))]
                inputs_c = [() for _ in range(len(BridgeEvolution.bridge.connections))]
                [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                    = sim.simulate(BridgeEvolution.bridge)
                create_inputs()
            BridgeEvolution.bridge.render("Upgrade_joint_" + mark + ".png")

            for i in range(no_iterations):
                net = neat.nn.FeedForwardNetwork.create(self.winner_j, self.config_j)
                output = [net.activate(xi) for xi in inputs_j]
                alter_bridge_j(output, BridgeEvolution.bridge)
                inputs_j = [() for _ in range(len(BridgeEvolution.bridge.points))]
                inputs_c = [() for _ in range(len(BridgeEvolution.bridge.connections))]
                [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                    = sim.simulate(BridgeEvolution.bridge)
                create_inputs()
            BridgeEvolution.bridge.render("Upgrade_connection_" + mark + ".png")


def score(max_strain: float, cost: float):
    """

    :param max_strain: maximum value of strain in simulation
    :param cost: cost of the structure
    :return: float: score of the model
    """
    cost_offset = 0.5 * math.atan(0.01 * (BridgeEvolution.budget - cost)) / math.pi
    if bridge.isSemiValid():
        return 1 - max_strain**2 + cost_offset
    return 0.5 + cost_offset


def create_inputs():
    """
    Calculation of current statistics of the bridge and preparing inputs for networks to train on
    """
    for i, j in enumerate(BridgeEvolution.bridge.points):
        indexes = [BridgeEvolution.bridge.connections.index(con)
                   for con in BridgeEvolution.bridge.getConnectedToJoint(j)]
        strain_con = [0 for _ in range(len(indexes) * len(BridgeEvolution.strain))]
        k = 0
        for strain in BridgeEvolution.strain:
            for idx in indexes:
                strain_con[k] = strain[idx]
                k += 1

        inputs_j[i] = ((1.0 if j.isStationary else 0.0), min(strain_con),
                       max(strain_con), sum(strain_con) / len(strain_con),
                       len(indexes))

    for i, con in enumerate(BridgeEvolution.bridge.connections):
        idx = BridgeEvolution.bridge.materials.index(con.material) / len(BridgeEvolution.bridge.materials)
        time = -1.0 if BridgeEvolution.break_moments[i] == -1.0 \
            else BridgeEvolution.break_moments[i] / BridgeEvolution.simulation_time
        inputs_c[i] = (idx, min(strain[i] for strain in BridgeEvolution.strain),
                       max(strain[i] for strain in BridgeEvolution.strain),
                       sum(strain[i] for strain in BridgeEvolution.strain) / len(BridgeEvolution.strain),
                       time)


def alter_bridge_j(commands: list, my_bridge: Bridge):
    """
    Function that performs analysis of network solution for joints
    :param my_bridge: bridge to alter
    :param commands: output of network to incorporate
    :return: statistics of a new bridge
    """
    mj = []
    rj = []
    aj = []
    ac = []
    removed = 0
    for i, args in enumerate(commands):
        val = (i, args[-2], args[-1],)
        if args[0] > 0.75:
            mj.append(val)
        if args[1] > 0.75:
            rj.append((val[0] - removed, val[1], val[2]))
            removed += 1
        if args[2] > 0.75:
            aj.append(val)
        if args[3] > 0.75:
            ac.append(val)
    for c in mj:
        nnf.moveJoint(my_bridge, c[0], c[1], c[2])
    for c in aj:
        nnf.addJoint(my_bridge, c[0], c[1], c[2])
    for c in ac:
        nnf.addConnection(my_bridge, c[0], c[1], c[2])
    for c in rj:
        nnf.removeJoint(my_bridge, c[0], c[1], c[2])

    return sim.simulate(my_bridge), sum(con.cost for con in my_bridge.connections)


def eval_genome_j(genomes, config):
    """
    Scoring function for ai joint
    :param genomes: genomes list
    :param config: genome class configuration data
    :return: float genome's fitness
    """
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        output = [net.activate(xi) for xi in inputs_j]
        global bridge_copy
        [[s_t2, strain_2, _], cost_2] = alter_bridge_j(output, bridge_copy.copy())

        s2 = max(max(s, default=0.0) for s in strain_2)

        # cost will be calculated later first set just survival rate
        # cost_1 = sum(con.cost for con in BridgeEvolution.bridge.connections)

        # genome.fitness = s_t2 / BridgeEvolution.max_time - s2
        genome.fitness = score(s2, cost_2)


def alter_bridge_c(commands: list, my_bridge: Bridge):
    """
    Function that performs analysis of network solution for connections
    :param my_bridge: bridge to alter
    :param commands: output of network to incorporate
    :return: statistics of a new bridge
    """
    cm = []
    rc = []
    removed = 0
    for i, args in enumerate(commands):
        val = (i, args[-1],)
        if args[0] > 0.75:
            cm.append(val)
        if args[1] > 0.75:
            rc.append((val[0] - removed, val[1]))
            removed += 1
    for c in cm:
        nnf.changeConnectionMaterial(my_bridge, c[0], c[1])
    for c in rc:
        nnf.removeConnection(my_bridge, c[0], c[1])

    return sim.simulate(my_bridge), sum(con.cost for con in my_bridge.connections)


def eval_genome_c(genomes, config):
    """
    Scoring function for ai connection
    :param genomes: genomes list
    :param config: genome class configuration data
    :return: float genome's fitness
    """
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        output = [net.activate(xi) for xi in inputs_c]

        [[s_t2, strain_2, _], cost_2] = alter_bridge_c(output, bridge_copy.copy())

        s2 = max(max(s) for s in strain_2)

        # cost will be calculated later first set just survival rate
        # cost_1 = sum(con.cost for con in BridgeEvolution.bridge.connections)
        # genome.fitness = s_t2 / BridgeEvolution.max_time - s2
        genome.fitness = score(s2, cost_2)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    import tbutils.materiallist as mat_list
    import tbutils.math2d as m2
    from tbutils.builder import Builder

    right = 300.0
    materials = [mat_list.materialList[0],
                 mat_list.materialList[3],
                 mat_list.materialList[7],
                 mat_list.materialList[19], ]
    stat = [m2.Vector2(100.0, 250.0), m2.Vector2(right, 250.0), ]
    bridge = Builder.buildInitial(materials, m2.Vector2(100.0, 300.0), m2.Vector2(right, 300.0), 1, stat)
    BridgeEvolution.bridge = bridge
    local_dir = os.path.dirname(__file__)
    chamber = BridgeEvolution(local_dir)
    chamber.set_reporter()
    chamber.train(100)
