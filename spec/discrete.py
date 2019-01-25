import unittest
import numpy as np
from PIL import Image
import src.discrete as disc
from src.discrete import utils as utils

seed = np.random.seed(68)

scen1 = {
    'pts': [[0.25, 0.25],    # 0
            [0.4, 0.4],      # 1
            [0.73, 0.23],    # 2
            [0.25, 0.75],    # 3
            [0.76, 0.76],    # 4
            ],
    'adj': [[0, 1], [1, 2], [1, 4], [1, 3], [0, 3],  [0, 2]],
    'wgt': []
}

scen2 = {
    'pts': [[0.25, 0.25],    # 0
            [0.5, 0.5],      # 1
            [0.73, 0.23],    # 2
            [0.25, 0.75],    # 3
            [0.66, 0.66],    # 4
            [0.76, 0.76],    # 5
            ],
    'adj': [[0, 1], [1, 2], [1, 4], [1, 3], [0, 3],
            [4, 5], [0, 4]],
    'wgt': [1, 2, 3, 4, 5, 4]
}


def prep_segment():
    pass


class TestDisc(unittest.TestCase):
    def setUp(self):
        self.domain = [[0., 0.], [0., 1.], [1., 1.], [1., 0.]]
        self.inputs = [[0.25, 0.25], [0.5, 0.5], [0.73, 0.23], [0.76, 0.76], [0.242, 0.7422]]
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
        assert space.done is False
        space._data = np.ones((100, 100))
        assert space.done is True

    def test_cut1(self):
        space = disc.BoundedSpace_Z2(x=50, y=50)
        cutpts1 = np.array([[1, 1], [10, 3], [8, 8]])
        space.cutout(cutpts1)
        space.to_image(out='./out/init_test/hole1.jpeg')

    def test_crop(self):
        space = disc.BoundedSpace_Z2(x=50, y=50)
        cutpts1 = np.array([[1, 20], [20, 40], [45, 20], [21, 1]])
        space.crop(cutpts1)
        space.to_image(out='./out/init_test/crop1.jpeg')

    def test_discrete1(self):
        space = disc.BoundedSpace_Z2(x=50, y=50)
        vor = disc.DiscreteVoronoi(points=self.inputs, space=space)
        for i, cell in enumerate(vor._cells):
            assert cell.index == i + 1
            print(cell)

        vor.create_voronoi()
        img = vor.to_image()
        img.show()

    def test_discrete2(self):
        pts = np.random.rand(10, 2)
        space = disc.BoundedSpace_Z2(x=100, y=100)
        vor = disc.DiscreteVoronoi(
            points=pts, space=space, verbose=True, stop=100, go=True,
            save=2
        )
        for i, cell in enumerate(vor._cells):
            assert cell.index == i
            print(cell)
        img = vor.to_image()
        img = img.resize((600, 600), Image.ANTIALIAS)
        img.show()
        return vor

    def test_discrete_w1(self):
        pts = np.random.rand(10, 3)
        space = disc.BoundedSpace_Z2(x=200, y=200)
        vor = disc.DiscreteVoronoi(
            points=pts, space=space, verbose=True, stop=100, go=True, bins=3
        )
        for i, cell in enumerate(vor._cells):
            assert cell.index == i
            print(cell)

    def test_discrete_setup(self):
        space = disc.BoundedSpace_Z2(x=100, y=100)
        vor = disc.VoronoiDBC(
            adj=scen1['adj'], points=scen1['pts'], space=space, verbose=True,
            stop=100, go=False, bins=3, save=2
        )
        vor._init_cell_sites()
        for site in vor.sites:
            print(site.index, len(site))
        vor.to_image(out='./out/init_test/t1.jpeg')

    def test_discrete_sg1(self):
        space = disc.BoundedSpace_Z2(x=100, y=100)
        vor = disc.VoronoiDBC(
            adj=scen1['adj'],
            points=scen1['pts'],
            space=space,
            verbose=True,
            stop=100,
            go=True,
            bins=3,
            save=1
        )

        for k, edge in vor._edges.items():
            print(k, len(edge))

    def test_discrete_aut8(self):
        space = disc.BoundedSpace_Z2(x=100, y=100)
        vor = disc.VoronoiDBC(
            adj=scen1['adj'],
            points=scen1['pts'],
            space=space,
            verbose=True,
            stop=100,
            go=True,
            bins=3,
            save=1,
            aut_class=disc.automota.Automaton8
        )

        for k, edge in vor._edges.items():
            print(k, len(edge))

    def test_disc_algo1(self):

        space = disc.BoundedSpace_Z2(x=100, y=100)
        areas = scen1['wgts']
        vor = disc.VoronoiDBC(
            adj=scen1['adj'],
            points=scen1['pts'],
            space=space,
            verbose=True,
            stop=100,
            go=False,
            bins=3,
            save=1,
            aut_class=disc.automota.Automaton8
        )

    def test_disc_nested_algo1(self):

        space = disc.BoundedSpace_Z2(x=100, y=100)

        vor = disc.VoronoiDBC(
            adj=scen1['adj'],
            points=scen1['pts'],
            space=space,
            verbose=True,
            stop=100,
            go=False,
            bins=3,
            save=1,
            aut_class=disc.automota.Automaton8
        )


_inputs = [[0.25, 0.25], [0.25, 0.75], [0.75, 0.75], [0.75, 0.25]]


class TestUtils(unittest.TestCase):
    def test_centroid(self):
        arr = np.asarray(_inputs)
        cr = utils.centroid(arr)
        assert np.allclose(cr, np.array([0.5, 0.5])), cr

    def test_area(self):
        arr = np.asarray(_inputs)
        cr = utils.polygon_area(arr)
        assert cr == 0.5 ** 2, cr

    def test_breseham(self):
        tests = [([25, 25], [25, 75]),
                 ([1, 5], [5, 5]),
                 ([1, 4], [4, 9]),
                 ([0, 1], [4, 9]),
                 ([1, 9], [4, 4])
                 ]
        for p1, p2 in tests:
            m = utils.discretize_segment(p1, p2)
            print(m)
            assert p1 in m
            assert p2 in m



    def test_dists(self):
        pass

