"""
This file contains definition of neural networks used in ai
Two main networks:
    one to work on joints
    second to work on connection
"""
from __future__ import print_function
import os
import random

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
    Requires a bridge to unlock train method for objects and max time of the simulation
    """
    # For simulations
    bridge: Bridge = None
    max_time: float = 1.0
    simulation_time: float = 0.4812591086981626
    strain: list = [[0.004533949416271299, 0.0030095314519843104, 0.0030095313315609364, 0.004533949264157258,
                     1.7983723581654047e-05,
                     1.0051729701032907e-05, 1.2754077468888418e-05, 2.663413402523579e-05, 1.2754117866427984e-05,
                     1.0051705423665378e-05, 1.7983745024554325e-05, 2.0921826956373023e-05, 2.0161516776682714e-05,
                     2.0161551474397698e-05, 2.092181077414152e-05, 5.705436569762145e-06, 5.705436569762145e-06,
                     5.705436569762145e-06, 5.705436569762145e-06, 5.705436569762145e-06, 5.705436569762145e-06,
                     5.705436569762145e-06,
                     5.705436569762145e-06],
                    [0.0029921245279054946, 0.001914378818114876, 0.0019143790086581889, 0.0029921246371913102,
                     1.246924519059753e-05,
                     7.481056043111782e-06, 8.957061761975516e-06, 1.928606825775552e-05, 8.95703445479252e-06,
                     7.481061015116652e-06,
                     1.246918507653572e-05, 1.640677426236943e-05, 1.5695120176589882e-05, 1.5695054130505503e-05,
                     1.6406821755337227e-05, 9.482435702999895e-05, 9.482435702999895e-05, 9.482427748135502e-05,
                     9.482427748135502e-05, 9.482447678316891e-05, 9.482447678316891e-05, 9.482444428320671e-05,
                     9.482444428320671e-05],
                    [5.844251557449152e-05, 0.00014164988350460637, 0.00014164974326472815, 5.8442586462587986e-05,
                     1.596511656656051e-06, 2.1364662197076269e-07, 2.16386705507609e-06, 6.8108397197947e-06,
                     2.1638930415702923e-06,
                     2.1355829119674882e-07, 1.5962858407338244e-06, 9.396930571636463e-06, 2.2881446531397014e-06,
                     2.288274223890989e-06, 9.39669513898469e-06, 0.0006413290422238066, 0.0006413290422238066,
                     0.0006412866007148161,
                     0.0006412866007148161, 0.0006413373299879319, 0.0006413373299879319, 0.0006412949625913703,
                     0.0006412949625913703],
                    [0.00492379841863334, 0.003019252237069202, 0.0030192545113941834, 0.004923798564840039,
                     4.244645515853236e-05,
                     1.3566068480302162e-05, 2.147437321353058e-05, 2.3698917073424554e-05, 2.147403608829414e-05,
                     1.3565952182000755e-05, 4.244508769302297e-05, 1.1354795992765884e-05, 3.7723413872815296e-05,
                     3.7723032047418096e-05, 1.1354421769254179e-05, 0.026468019928843737, 0.026468019928843737,
                     0.02649211555650789,
                     0.02649211555650789, 0.026467742757159556, 0.026467742757159556, 0.026491838161430466,
                     0.026491838161430466],
                    [0.000885617282388216, 0.0002141359681386719, 0.00021413654586599634, 0.0008856171066448103,
                     0.00015883864836764073, 3.554005247669802e-05, 6.569780189039814e-05, 0.0001664263816354229,
                     6.569677808467663e-05, 3.553898302952557e-05, 0.0001588333754845216, 7.316451629771628e-07,
                     2.2561482305341823e-05, 2.2561437898287943e-05, 7.345660181297683e-07, 1, 1, 1, 1, 1, 1, 1, 1],
                    [0.0007826163096344068, 0.0001033758811733617, 0.00010335949749715247, 0.0007826159138425349,
                     0.00025393638340009603, 6.971623713317607e-05, 6.779582985120816e-05, 0.0003057155529861735,
                     6.779978142976597e-05, 6.972149312498021e-05, 0.0002539587341853766, 9.908132002719909e-05,
                     3.4495345640979265e-05, 3.4494066943626016e-05, 9.90706598881159e-05, 1, 1, 1, 1, 1, 1, 1, 1],
                    [0.005135008896565864, 0.003222050879619629, 0.003222005255928808, 0.005134999258738415,
                     0.007455741521484531,
                     0.0019440526699596508, 0.002532297289102921, 0.008933529865243215, 0.0025323121899684525,
                     0.0019440751189889194,
                     0.007455834780133065, 0.0016923022756087413, 0.001018365418966027, 0.0010183569275846627,
                     0.001692260304055965, 1,
                     1, 1, 1, 1, 1, 1, 1],
                    [0.0006654477393902604, 0.001194082465795061, 0.0011942716844507671, 0.0006654991096308363,
                     0.009740285300848413,
                     0.0026068231857466363, 0.0031473511734264707, 0.011312428917050013, 0.00314740916195811,
                     0.002606917956704177,
                     0.009740666880955894, 0.0033256708984653826, 0.0001917336831162207, 0.00019172621313472878,
                     0.003325472777372944,
                     1, 1, 1, 1, 1, 1, 1, 1],
                    [0.01173912593500031, 0.010404694411234894, 0.01040555644137685, 0.01173927556648044,
                     0.3105507450284876,
                     0.08169746550006869, 0.10407397524778711, 0.36606580348720325, 0.10407373108047438,
                     0.08169706369588539,
                     0.3105491476094635, 0.08038350542630497, 0.030108747614121984, 0.030108907274265052,
                     0.08038421101186577, 1, 1, 1,
                     1, 1, 1, 1, 1],
                    [0.25752836391808004, 1, 1, 0.25752755681722717, 1, 0.05723257852481457, 0.04559988427093752, 1,
                     0.04560034627098954, 0.057231783299714324, 1, 0.195030100555172, 0.1583861091626705,
                     0.15838514649816424, 0.1950298037523481, 1, 1, 1, 1, 1, 1, 1, 1]]
    break_moments: list = [-1.0, 0.4812591086981626, 0.4812591086981626, -1.0, 0.4796887283105269, -1.0, -1.0,
                           0.47414034419585516, -1.0,
                           -1.0, 0.4796887283105269, -1.0, -1.0, -1.0, -1.0, 0.2382945933263878, 0.2382945933263878,
                           0.23844122081355923,
                           0.23844122081355923, 0.2382945933263878, 0.2382945933263878, 0.23844122081355923,
                           0.23844122081355923]

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
            print(inputs_c)
            print(inputs_j)
            global bridge_copy
            bridge_copy = BridgeEvolution.bridge.copy()
            # pe_j = neat.ParallelEvaluator(4, eval_genome_j)
            # pe_c = neat.ParallelEvaluator(4, eval_genome_c)
            # self.winner_j = self.p_j.run(pe_j.evaluate, no_generations)
            # self.winner_c = self.p_c.run(pe_c.evaluate, no_generations)
            self.winner_j = self.p_j.run(eval_genome_j, no_generations)

            # Display the winning genome.
            print('\nBest genome:\n{!s}'.format(self.winner_j))
            winner_net = neat.nn.FeedForwardNetwork.create(self.winner_j, self.config_j)
            output = [winner_net.activate(xi) for xi in inputs_j]
            alter_bridge_j(output, BridgeEvolution.bridge)
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
            output = [winner_net.activate(xi) for xi in inputs_j]
            alter_bridge_j(output, BridgeEvolution.bridge)
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
        if BridgeEvolution.bridge is not None:
            global inputs_j
            global inputs_c
            inputs_j = [() for _ in range(len(BridgeEvolution.bridge.points))]
            inputs_c = [() for _ in range(len(BridgeEvolution.bridge.connections))]
            [BridgeEvolution.simulation_time, BridgeEvolution.strain, BridgeEvolution.break_moments] \
                = sim.simulate(BridgeEvolution.bridge)
            create_inputs()
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

    if my_bridge.isSemiValid():
        return sim.simulate(my_bridge), sum(con.cost for con in my_bridge.connections)
    return [0, [[-0.5]], []], sum(con.cost for con in my_bridge.connections)


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

        genome.fitness = s_t2 / BridgeEvolution.max_time - s2


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

    if my_bridge.isSemiValid():
        return sim.simulate(my_bridge), sum(con.cost for con in my_bridge.connections)
    return [0, [[-0.5]], []], sum(con.cost for con in my_bridge.connections)


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
        genome.fitness = s_t2 / BridgeEvolution.max_time - s2


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
