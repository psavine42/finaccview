import unittest
from src.space import *
import networkx as nx
import networkx.algorithms as nxa
import matplotlib.pyplot as plt


def plot(space):
    G = space.boundary_graph()
    print(len(G), nxa.check_planarity(G))

    pos = nx.spring_layout(G, iterations=1000)
    nx.draw(G, pos=pos)
    _edges = [edge for edge in G.edges()]
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edgelist=_edges, arrows=True)
    plt.show()


class TestSpaceSetup(unittest.TestCase):
    def setUp(self):
        self._x = None

    def test_basic_setup(self):
        space = LSpace()
        space.add_cell('budget')
        space.add_cell('income', to=['budget'], _from=['world'])
        space.add_cell('cost', to=['budget'], _from=['world'])
        bnd1 = space[['budget', 'income']]
        print(bnd1)

    def test_procore1_setup(self):
        space = LSpace()
        budget = space.add_cell('budget')
        prime = space.add_cell('prime', w=True)
        cost = space.add_cell('cost', w=True)
        cost_change = space.add_cell('cost_change', w=True)
        prime_change = space.add_cell('prime_change', w=True)

        # cell to cell bounds
        cost_chnge_2_cost = space.add_boundary('cost_change', 'cost')
        prime_chng_2_prime = space.add_boundary('prime_change', 'prime')
        prime_2_budget = space.add_boundary('prime', 'budget')
        cost_2_budget = space.add_boundary('cost', 'budget')

        # inside-cell connections

        cost.bound_to('world', 'budget')
        cost_change.bound_to('world', 'cost')
        prime_change.bound_to('world', 'prime')
        prime.bound_to('world', 'budget')

        bounds = [cost_chnge_2_cost,
                  prime_2_budget,
                  prime_chng_2_prime,
                  cost_2_budget]

        for b in bounds:
            assert b is not None

        # plot(space)
        return space

    def test_procore1_flows(self):
        space = self.test_procore1_setup()
        pc = space['prime']
        wrld = space['world']
        assert wrld is not None
        n1 = space.add_flow({'id': 1}, mag=100)
        assert n1.location is not None
        assert n1.location.name == 'world'

        n2 = space.add_flow({'id': 2}, mag=200)

        print(n1.location.successors)
        assert len(n1.next_states) > 0

        pr = wrld['[world]->[prime]']
        assert pr is not None
        assert isinstance(pr, Boundary), 'boundary is fucked'
        n11 = n1.flow_to(pr)
        assert n11.location.name == '[world]->[prime]'
        assert n1._children == [n11]


    def tearDown(self):
        pass


def setup():
    space = TestSpaceSetup().test_procore1_setup()
    return space

