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
            Value for first argument <0.0, 1.0>,
            Value for second argument <0.0, 1.0>,
        Whether to use addJoint() <0.0, 1.0>,
            Value for first argument <0.0, 1.0>,
            Value for second argument <0.0, 1.0>,
        Whether to use addConnection() <0.0, 1.0>,
            Value for first argument <0.0, 1.0>,
            Value for second argument <0.0, 1.0>,
        Whether to use removeJoint() <0.0, 1.0>,
        Whether to use removeConnection() <0.0, 1.0>,
    ]

    * Note: arguments values are mapped to symmetrical space in helper functions

    Example: [0.95, 0.65, 0.5, 0.01, 0.2, -0.7, 0.8, 0.3, -0.3, 0.0, 0.1]
        -> means:
            call: moveJoint(...,...,0.65,0.5,...)
            call: addConnection(...,...,0.3,-0.3,...)

"""

from __future__ import print_function
import multiprocessing
import os
import neat
import tbsymulator.mechanicsFEM as sim
from tbutils.bridgeparts import Bridge
from tbneuralnetwork.nueralnetworkfunctions import score, alter_bridge, create_inputs
import tbneuralnetwork.traindata as td
import pickle


class BridgeEvolution:
    """
    Main class for evolving the bridge structure
    Requires a bridge to unlock train method for objects
    """
    network_type: str = ''

    def __init__(self, path_to_catalog: str, network_type: str = ''):
        """
        Initialization of new set of neural network pair
        :param path_to_catalog: location of catalog with configuration files relative to __main__
        """
        self.network_type = network_type
        config_path = os.path.join(path_to_catalog, 'config-feedforward-v2' + self.network_type)
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                  neat.DefaultStagnation, config_path)

        # Create the population, which is the top-level object for a NEAT run.
        self.p = neat.Population(self.config)
        self.winner = None

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
        pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)
        self.winner = self.p.run(pe.evaluate, no_generations)

        print('\nBest genome:\n{!s}'.format(self.winner))

        # |____________________
        # |  Add RNN !!!!
        # |____________________
        winner_net = neat.nn.FeedForwardNetwork.create(self.winner, self.config)

        for i, (bridge, steps, complexity) in enumerate(td.BRIDGES):
            (_, strains, break_moments) = td.BRIDGES_RESULTS[i]
            bridge_copy = bridge.copy()
            for j in range(steps):
                inputs_nn = create_inputs(bridge_copy, break_moments, strains, complexity)
                # |____________________
                # |  Add RNN !!!!
                # |____________________
                output = [(xi[0], winner_net.activate(xi)) for xi in inputs_nn]
                bridge_copy = alter_bridge(output, bridge_copy)
                (_, strains, break_moments) = sim.simulate(bridge_copy)
                bridge_copy.render(f"Train{i}_step{j}.png")
            with open(f"winnerBridge{i}.pkl", "wb") as f:
                pickle.dump(bridge_copy, f)

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
        pass
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
                output = [(xi[0], net.activate(xi)) for xi in inputs_j]
                alter_bridge(output, BridgeEvolution.bridge)
                inputs_j = [() for _ in BridgeEvolution.bridge.points]
                inputs_c = [() for _ in BridgeEvolution.bridge.connections]
                [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                    = sim.simulate(BridgeEvolution.bridge)
                create_inputs()
            BridgeEvolution.bridge.render("Upgrade_" + mark + ".png")

        BridgeEvolution.upgrade_still_running = False


def eval_genome(genome, config):
    """
    Scoring function for ai
    :param genome: genomes list
    :param config: genome class configuration data
    :return: float genome's fitness
    """
    # |____________________
    # |  Add RNN !!!!
    # |____________________
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    scores = 0.0
    runs = 0
    for i, (bridge, steps, complexity) in enumerate(td.BRIDGES):
        (_, strains, break_moments) = td.BRIDGES_RESULTS[i]
        bridge_copy = bridge.copy()
        for j in range(steps):
            inputs_nn = create_inputs(bridge_copy, break_moments, strains, complexity)
            # |____________________
            # |  Add RNN !!!!
            # |____________________

            output = [(xi[0], net.activate(xi)) for xi in inputs_nn]
            bridge_copy = alter_bridge(output, bridge_copy)
            (_, strains, break_moments) = sim.simulate(bridge_copy)
            scores += score(bridge_copy, strains, td.BUDGETS[i])
            runs += 1
    return scores/runs


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    chamber = BridgeEvolution(local_dir)
    chamber.set_reporter()
    chamber.train(10)
