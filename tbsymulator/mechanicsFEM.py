import numpy as np
import numpy.linalg as np_lin
import scipy.linalg as la
from math import sqrt
import tbutils.math2d as m2
from tbutils.builder import Builder
from tbutils.bridgeparts import Bridge, Connection, Joint
import tbutils.materiallist as mat_list


def simulate(bridge_original: Bridge, gravity: m2.Vector2 = m2.Vector2(0, -9.81)):
    bridge = bridge_original.copy()
    # insertion of numerical resistance connection
    numerical_resistance = mat_list.materialList[-1]
    joint_a = Joint(m2.Vector2(-1000.0, -999.0), True)
    joint_b = Joint(m2.Vector2(999.0, 1000.0), True)
    bridge.points.append(joint_a)
    bridge.points.append(joint_b)

    def add_connection(stationary: Joint, tested: Joint):
        if (len(bridge.getConnectedToJoint(tested)) > 0) and (not tested.isStationary):
            bridge.connections.append(Connection.makeCFM(stationary, tested, numerical_resistance))
            bridge.connections[-1].update()
            return 1
        return 0

    added_connections = 0
    for p in bridge.points[:-2]:
        added_connections += add_connection(joint_a, p)
        added_connections += add_connection(joint_b, p)

    bridge_points: np.ndarray = np.array([[p.position.x, p.position.y] for p in bridge.points])
    n: int = len(bridge_points)
    # print(bridge_points)

    elements = np.array([[bridge.points.index(c.jointA), bridge.points.index(c.jointB)] for c in bridge.connections])
    used_elements = np.unique(elements.flatten())
    not_connected_joints = np.setdiff1d(np.array(range(n)), used_elements)
    m: int = len(elements)
    # print(elements)

    e = [c.material.strFR for c in bridge.connections]
    # print(e)

    a = [c.material.surf for c in bridge.connections]
    # print(a)

    den = [c.material.linDen for c in bridge.connections]
    # print(den)
    bc = np.array([[2 * i, 2 * i + 1] for i, p in enumerate(bridge.points) if p.isStationary]).flatten()
    # print(bc)

    lengths = [c.length if c.length > 0.0 else 1e-7 for c in bridge.connections]
    cs_mat: np.ndarray = np.zeros([m, 2])
    forces: np.ndarray = np.zeros(2 * n)

    for i, el in enumerate(elements):
        dp: np.ndarray = (bridge_points[el[1]] - bridge_points[el[0]])
        force = lengths[i] * den[i] * gravity.y
        forces[2 * el[0] + 1] += force / 2
        forces[2 * el[1] + 1] += force / 2
        cs_mat[i] = dp / lengths[i]

    forces[bc] = 0
    # print('l:\n', lengths)
    # print('f:\n', forces)

    k_mat: np.ndarray = np.zeros([m, 4, 4])
    for i, cs in enumerate(cs_mat):
        k_mat[i] = ek_mat(cs)
    # print('k_mat:\n', k_mat)
    kpl_mat: np.ndarray = np.zeros([m, 4, 4])
    for i, k in enumerate(k_mat):
        kpl_mat[i] = k * (a[i] * e[i] / lengths[i])
    # print('kpl_mat:\n', kpl_mat)
    k: np.ndarray = np.zeros([2 * n, 2 * n])
    for i, el in enumerate(elements):
        u = 2 * el[0] + 1
        v = 2 * el[1] + 1
        kpl = kpl_mat[i]
        k[u - 1:u + 1, u - 1:u + 1] += kpl[0:2, 0:2]
        k[u - 1:u + 1, v - 1:v + 1] += kpl[0:2, 2:4]
        k[v - 1:v + 1, u - 1:u + 1] += kpl[2:4, 0:2]
        k[v - 1:v + 1, v - 1:v + 1] += kpl[2:4, 2:4]
    # print('\nk:\n', k)

    for el in bc:
        k[:, el] = np.zeros((2*n,))
        k[el, :] = np.zeros((1, 2 * n))
        k[el, el] = 1
    for el in not_connected_joints:
        k[2 * el, 2 * el] = 1
        k[2 * el + 1, 2 * el + 1] = 1

    # forces[7] -= 147150

    # print('k final:\n', k)

    try:
        # lu, piv = la.lu_factor(k)
        # d = la.lu_solve((lu, piv), forces)
        d = np_lin.solve(k, forces)
    except np.linalg.LinAlgError as e:
        print([k[i, i] for i in range(2*n)])
        np.set_printoptions(precision=0, suppress=True)
        import pickle
        with open("ErrorBridge.pkl", "wb") as f:
            pickle.dump(bridge_original, f)
        bridge_original.render("Error shape.png")
        return 1, [2 for _ in bridge_original.connections], [1 for _ in bridge_original.connections]
    # print('\n\nd:\n', d)

    strains = np.zeros(m)
    for i, el in enumerate(elements):
        dl = cs_mat[i, 0] * (d[2 * el[1]] - d[2 * el[0]]) \
             + cs_mat[i, 1] * (d[2 * el[1] + 1] - d[2 * el[0] + 1])
        strains[i] = e[i] * dl / lengths[i]
    # print('strains:\n', strains)

    moved_points = np.array([[p[0] + d[2 * i], p[1] + d[2 * i + 1]] for i, p in enumerate(bridge_points)])
    moved_lengths = []
    for i, el in enumerate(elements):
        dp: np.ndarray = (moved_points[el[1]] - moved_points[el[0]])
        moved_lengths.append(sqrt(np.dot(dp, dp)))

    strains_percentage = []
    for i, l in enumerate(lengths):
        rate = moved_lengths[i] / l
        c = bridge.connections[i]
        strains_percentage.append((1 - rate) / (1 - c.maxCompression) if rate <= 1.0
                                  else (rate - 1) / (c.maxStretch - 1))

    if added_connections > 0:
        return 0 if max(strains_percentage[:-added_connections], default=0.0) < 1 else 1, \
           strains_percentage[:-added_connections], \
           [0 if p < 1.0 else 1 for p in strains_percentage[:-added_connections]]
    else:
        return 0 if max(strains_percentage, default=0.0) < 1 else 1, \
               strains_percentage, \
               [0 if p < 1.0 else 1 for p in strains_percentage]


def ek_mat(cs: np.ndarray):
    # print(f'cs: {cs}')
    b = np.array([-cs[0], -cs[1], cs[0], cs[1]], ndmin=2)
    return b.transpose() * b


if __name__ == '__main__':
    right = 300.0
    materials = [mat_list.materialList[0],
                 mat_list.materialList[5],
                 mat_list.materialList[7],
                 mat_list.materialList[19],
                 mat_list.materialList[-1],
                 ]
    stat = [m2.Vector2(100.0, 250.0), m2.Vector2(right, 250.0), ]
    test_bridge = Builder.buildInitial(materials, m2.Vector2(100.0, 300.0),
                                       m2.Vector2(right, 300.0), 1, stat)
    # joints = [Joint(m2.Vector2(0.0, 0.0), True), Joint(m2.Vector2(200.0, 200.0), True),
    #           Joint(m2.Vector2(50.0, 100.0), True), Joint(m2.Vector2(50.0, 10.0))]
    # con = [Connection.makeCFM(joints[2], joints[3], materials[0]),
    #        ]
    # test_bridge = Bridge()
    # test_bridge.points = joints
    # test_bridge.connections = con
    # test_bridge.materials = materials
    # test_bridge.render("Test.png")

    (rt, rs, rb) = simulate(test_bridge)
    print(rt, rs, rb, sep='\n')
