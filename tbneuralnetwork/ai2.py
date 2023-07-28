"""
New AI module where connection is merged with joint
Structure:
    Input:  [
        Element type {Joint: -1.0, Beam: 1.0}
        Movement {
            Joint {
                stationary: 0.0,
                movable: 1.0
            },
            Beam {
                partly stationary: -1.0,
                stationary: 0.0,
                movable: 1.0
            }
        },
        Min stress {
            Joint: Min stress of the all connected beams (% of maximum stress for beam),
            Beam: -1.0
        },
        Max stress {
            Joint: Max stress of the all connected beams (% of maximum stress for beam),
            Beam: -1.0
        },
        Stress {
            Joint: Avg stress of the all connected beams (% of maximum stress for beam),
            Beam: Beam stress (% of maximum stress for beam)
        },
        Complexity {
            Joint: Number of the connected beams (scaled to structure complexity),
            Beam: Beam length / Maximum length
        },
        Damage {
            Joint: Ratio of broken connected beams to number of connected beams,
            Beam: 1.0 if stress >= 1.0 else 0.0 (whether the beam broke)
        },
    ]

    Examples {
        Joint: [-1.0, 1.0, 0.01, 1.1, 0.5, 0.25, 0.20]
        Beam: [1.0, -1.0, -1.0, -1.0, 0.5, 0.25, 0.0]
        }

    Output: [
        Whether to use moveJoint() <0.0, 1.0>,
            Value for first argument <-1.0, 1.0>,
            Value for second argument <-1.0, 1.0>,
        Whether to use addJoint() <0.0, 1.0>,
            Value for first argument <-1.0, 1.0>,
            Value for second argument <-1.0, 1.0>,
        Whether to use addConnection() <0.0, 1.0>,
            Value for first argument <-1.0, 1.0>,
            Value for second argument <-1.0, 1.0>,
        Whether to use removeJoint() <0.0, 1.0>,
        Whether to use removeConnection() <0.0, 1.0>,
    ]

    Example: [0.95, 0.65, 0.5, 0.01, 0.2, -0.7, 0.8, 0.3, -0.3, 0.0, 0.1]
        -> means:
            call: moveJoint(...,...,0.65,0.5,...)
            call: addConnection(...,...,0.3,-0.3,...)

"""

from __future__ import print_function
import os
import math

import neat
import tbsymulator.mechanicsFEM as sim
from tbutils.bridgeparts import Bridge
import tbneuralnetwork.nueralnetworkfunctions as nnf
import pickle

inputs_nn = []
outputs_nn = []

inputs_j = []
outputs_j = []

inputs_c = []
outputs_c = []

complexity = 4

bridge_copy: Bridge or None = None


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
    upgrade_still_running = False

    def __init__(self, path_to_catalog: str):
        """
        Initialization of new set of neural network pair
        :param path_to_catalog: location of catalog with configuration files relative to __main__
        """
        config_path = os.path.join(path_to_catalog, 'config-feedforward-v2')
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                  neat.DefaultStagnation, config_path)

        # Create the population, which is the top-level object for a NEAT run.
        self.p = neat.Population(self.config)
        self.winner = None

        self.simulation_time = 0
        self.strain = []
        self.break_moments = []

    def set_reporter(self):
        """
        Helper function that turns on evolution progress displays on stdout
        """
        self.p.add_reporter(neat.StdOutReporter(True))
        self.p.add_reporter(neat.StatisticsReporter())

    def train(self, no_generations: int):
        """
        Main function that trains network pair wise for limited amount per pair in iteration
        to allow steady progress
        :param no_generations: max amount of evolution per pair in iteration
        """
        if BridgeEvolution.bridge is not None:
            global inputs_j
            global inputs_c
            inputs_j = [() for _ in BridgeEvolution.bridge.points]
            inputs_c = [() for _ in BridgeEvolution.bridge.connections]
            [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                = sim.simulate(BridgeEvolution.bridge)
            create_inputs()
            BridgeEvolution.budget = 0.9 * sum(con.cost for con in BridgeEvolution.bridge.connections)
            # learning of joint:

            # print(inputs_c)
            # print(inputs_j)
            global bridge_copy
            bridge_copy = BridgeEvolution.bridge.copy()
            self.winner = self.p.run(eval_genome, no_generations)
            # with open("winner_j.pkl", "rb") as f:
            #   self.winner_j = pickle.load(f)
            # Display the winning genome.
            print('\nBest genome:\n{!s}'.format(self.winner))
            winner_net = neat.nn.FeedForwardNetwork.create(self.winner, self.config)
            output = [winner_net.activate(xi) for xi in inputs_nn]
            alter_bridge(output, BridgeEvolution.bridge)
            bridge_copy = BridgeEvolution.bridge.copy()
            BridgeEvolution.bridge.render("Train.png")
            inputs_j = [() for _ in BridgeEvolution.bridge.points]
            inputs_c = [() for _ in BridgeEvolution.bridge.connections]
            [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                = sim.simulate(BridgeEvolution.bridge)
            create_inputs()
            with open("winner.pkl", "wb") as f:
                pickle.dump(self.winner, f)

    def load(self):
        with open("winner.pkl", "rb") as f:
            self.winner = pickle.load(f)

    def save(self):
        with open("winner.pkl", "wb") as f:
            pickle.dump(self.winner, f)

    def upgrade(self, mark: str, no_iterations: int):
        """
        Method performing evaluation of the bridge by both networks
        :param mark: signature of the result files
        :param no_iterations: number of updates per network
        """
        BridgeEvolution.upgrade_still_running = True

        if BridgeEvolution.bridge is not None:
            global inputs_j
            global inputs_c
            inputs_j = [() for _ in BridgeEvolution.bridge.points]
            inputs_c = [() for _ in BridgeEvolution.bridge.connections]
            [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                = sim.simulate(BridgeEvolution.bridge)
            create_inputs()
            BridgeEvolution.budget = 0.9 * sum(con.cost for con in BridgeEvolution.bridge.connections)
            print(inputs_c)
            print(inputs_j)
            global bridge_copy
            bridge_copy = BridgeEvolution.bridge.copy()
            for i in range(no_iterations):
                net = neat.nn.FeedForwardNetwork.create(self.winner, self.config)
                output = [net.activate(xi) for xi in inputs_j]
                alter_bridge(output, BridgeEvolution.bridge)
                inputs_j = [() for _ in BridgeEvolution.bridge.points]
                inputs_c = [() for _ in BridgeEvolution.bridge.connections]
                [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                    = sim.simulate(BridgeEvolution.bridge)
                create_inputs()
            BridgeEvolution.bridge.render("Upgrade_" + mark + ".png")

        BridgeEvolution.upgrade_still_running = False


def score(bridge_local: Bridge, max_strain: float, cost: float):
    """
    Utility function to calculate resulting score of the simulation for genome fitness value
    :param bridge_local: tested structure
    :param max_strain: maximum value of strain in simulation
    :param cost: cost of the structure
    :return: float: score of the model
    """
    cost_offset = 0.5 * math.atan(0.01 * (BridgeEvolution.budget - cost)) / math.pi
    if bridge_local.isSemiValid():
        return 1 - min(math.sqrt(max_strain), 5.0) + cost_offset
    return 0.5 + cost_offset


def create_inputs():
    """
    Calculation of current statistics of the bridge and preparing inputs for networks to train on
    """
    for i, j in enumerate(BridgeEvolution.bridge.points):
        indexes = [BridgeEvolution.bridge.connections.index(con)
                   for con in BridgeEvolution.bridge.getConnectedToJoint(j)]
        strain_con = [BridgeEvolution.strain[0][idx] for idx in indexes]
        broken = list(filter(lambda x: (x >= 1.0), strain_con))
        j_type = -1.0
        j_movement = 1.0 if j.isStationary else 0.0
        j_min = min(strain_con)
        j_max = max(strain_con)
        j_stress = sum(strain_con) / len(strain_con)
        j_complexity = (len(indexes)-complexity)/complexity
        j_damage = len(broken)/len(indexes)
        inputs_j[i] = [j_type, j_movement, j_min, j_max, j_stress, j_complexity, j_damage]

    for i, con in enumerate(BridgeEvolution.bridge.connections):
        movement_joint_a = con.jointA.isStationary
        movement_joint_b = con.jointB.isStationary
        c_type = 1.0
        c_movement = -1.0 if movement_joint_a ^ movement_joint_b else (0.0 if movement_joint_a else 1.0)
        c_min = -1.0
        c_max = -1.0
        c_stress = BridgeEvolution.strain[0][i]
        c_complexity = con.length / con.material.maxLen
        c_damage = BridgeEvolution.break_moments[i]
        inputs_c[i] = (c_type, c_movement, c_min, c_max, c_stress, c_complexity, c_damage)
    global inputs_nn
    inputs_nn = []
    inputs_nn.extend(inputs_j)
    inputs_nn.extend(inputs_c)


def alter_bridge(commands: list, my_bridge: Bridge):
    """
    Function that performs analysis of network solution
    :param my_bridge: bridge to alter
    :param commands: output of network to incorporate
    :return: statistics of a new bridge
    """
    mj = []
    rj = []
    aj = []
    ac = []
    rc = []
    removed_joints = 0
    removed_connections = 0
    for i, (el_type, args) in enumerate(commands):
        if el_type == -1.0:
            if args[0] > 0.75:
                mj.append((i, args[1], args[2]))
            if args[9] > 0.75:
                rj.append((i - removed_joints,))
                removed_joints += 1
            if args[3] > 0.75:
                aj.append((i, args[4], args[5]))
            if args[6] > 0.75:
                ac.append((i, args[7], args[8]))
        elif el_type == 1.0:
            idx = i - len(bridge_copy.points)
            if args[10] > 0.75:
                rc.append((idx - removed_connections,))
                removed_connections += 1

    for c in mj:
        nnf.moveJoint(my_bridge, c[0], c[1], c[2])
    for c in aj:
        nnf.addJoint(my_bridge, c[0], c[1], c[2])
    for c in ac:
        nnf.addConnection(my_bridge, c[0], c[1], c[2])
    for c in rc:
        nnf.removeConnection(my_bridge, c[0])
    for c in rj:
        nnf.removeJoint(my_bridge, c[0])

    [_, strain_2, _] = sim.simulate(my_bridge)
    s = max(max(s, default=0.0) for s in strain_2)
    cost = sum(con.cost for con in my_bridge.connections)
    return score(my_bridge, s, cost)


def eval_genome(genomes, config):
    """
    Scoring function for ai
    :param genomes: genomes list
    :param config: genome class configuration data
    :return: float genome's fitness
    """
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        output = [(xi[0], net.activate(xi)) for xi in inputs_nn]
        genome.fitness = alter_bridge(output, bridge_copy.copy())


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
