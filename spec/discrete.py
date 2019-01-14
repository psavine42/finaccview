import unittest
import numpy as np
import src.discrete as disc


class TestDisc(unittest.TestCase):
    def setUp(self):
        self.domain = [[0., 0.], [0., 1.], [1., 1.], [1., 0.]]
        self.inputs = [[0.25, 0.25], [0.5001, 0.5], [0.73, 0.23], [0.76, 0.76], [0.242, 0.7422]]
        self.weight = [0.4, 0.1, 0.2, 0.2, 0.2]
        self.weighted = [[x, y, w / 2] for (x, y), w in zip(self.inputs, self.weight)]

    def test_autom(self):
        init_loc = [1, 1]
        root = disc.Automaton4(init_loc)
        step1 = set(root.next_states())
        assert len(step1) == 4, 'expected 4 got {}'.format(len(step1))
        for nxt_state in step1:
            step2 = list(nxt_state.next_states())
            assert len(step2) == 3, 'expected 3 got {}'.format(len(step2))
            print(nxt_state)
            for stp2 in step2:
                assert stp2.pos.tolist() != init_loc
                print('   ', stp2)

    def test_site(self):
        space = disc.BoundedSpace_Z2(x=100, y=100)
        assert len(space) == 100 * 100
        assert space.is_filled is False
        space._data = np.ones((100, 100))
        assert space.is_filled is True

    def test_discrete1(self):
        space = disc.BoundedSpace_Z2(x=100, y=100)
        vor = disc.DiscreteVoronoi(points=self.inputs,
                                   space=space,
                                   x=100, y=100)
        # vor.create_voronoi()
        for i, cell in enumerate(vor._cells):
            assert cell.index == i
            print(cell)

        vor.create_voronoi(verbose=True, stop=100)
        img = vor.to_image()
        img.show()
