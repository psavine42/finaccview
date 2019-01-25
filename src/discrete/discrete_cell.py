from .automota import Automaton4
import numpy as np
from . import utils as utils


class Site(object):
    def __init__(self,
                 *pos,
                 space=None,
                 ix=None,
                 source=None,
                 step_every=1,
                 aut_klass=Automaton4):
        self._pos = pos
        self.index = ix
        self._space = None
        self._step_every = step_every
        self._matrix = None
        self._chain = []
        self._aut_klass = aut_klass
        self._step = 0
        self._color = np.asarray([
            np.random.randint(40, 255) for _ in range(3)
        ])

    def __len__(self):
        return len(self._chain)

    def reset(self, *pt):
        self._chain = []
        self._pos = pt
        self.init_claimed_list()

    @property
    def color(self):
        return self._color

    @property
    def area(self):
        raise NotImplemented()

    @property
    def centroid(self):
        raise NotImplemented()

    @property
    def polygon(self):
        raise NotImplemented()

    @property
    def pos(self):
        return np.asarray(self._pos)

    @property
    def weight(self):
        return self._step_every

    def should_step(self, step):
        do_step = step % self._step_every == 0
        return do_step

    def distance_to(self, other):
        raise NotImplemented()

    def add_boundary(self, boundary):
        if isinstance(boundary, list):
            boundary = self._aut_klass(boundary)
        self._chain.append(boundary)

    @property
    def boundary_chain(self):
        return self._chain

    def init_claimed_list(self):
        raise NotImplemented()

    def update_boundary_chain(self, M):
        unique_nexts = set()
        for automaton in self._chain:
            for next_state in automaton.next_states():
                if M.is_open(next_state.pos) == True:
                    unique_nexts.add(next_state)
        return unique_nexts


class DiscreteSite(Site):
    def __init__(self, *args, parent=None, source=None, **kwargs):
        Site.__init__(self, *args, **kwargs)
        self.x = args[0]
        self.y = args[1]
        self._parent = parent
        self.source_point = source
        self._edges = []

    def __str__(self):
        return '<{}> at {} {}'.format(self.__class__.__name__, self.x, self.y)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if other.index == self.index:
                return True
        return False

    @property
    def area(self):
        return len(np.where(self._parent.M.np == self.index)[0])

    @property
    def center_of_mass(self):
        xs, ys = np.where(self._parent.M.np == self.index)
        pt = utils.pointset_mass_distribution(np.stack([xs, ys], 1))
        return pt.astype(int)

    def distance_to(self, other):
        return (((self.x - other[0]) ** 2) + ((self.y - other[1]) ** 2)) ** 0.5

    def init_claimed_list(self):
        aut = self._aut_klass(self._pos)
        self._parent.claim_pixel(self, aut)
        self._chain = [aut]


class ShapeSite(DiscreteSite):
    def __init__(self, x, y, **kwargs):
        DiscreteSite.__init__(self, x, y, **kwargs)


class SegmentSite(DiscreteSite):
    def __init__(self, x1, y1, x2, y2, **kwargs):
        DiscreteSite.__init__(self, x1, y1, x2, y2, **kwargs)

    def init_claimed_list(self):
        p1 = self._pos[0:2]
        p2 = self._pos[2:4]
        for pt in utils.discretize_segment(p1, p2):
            aut = self._aut_klass(pt)
            self._parent.claim_pixel(self, aut)
            self._chain.append(aut)


class WeightedSite(DiscreteSite):
    def __init__(self, *args, **kwargs):
        p1, p2, w = args
        DiscreteSite.__init__(self, p1, p2, **kwargs)
        self._target_size = w

    def should_step(self, step):
        # if target size has been reached, do not step
        if self.area <= self._target_size:
            do_step = step % self._step_every == 0
            return do_step
        return False


class CompositeSite(Site):
    def __init__(self, *args, **kwargs):
        Site.__init__(self, *args, **kwargs)
        self._children = []

    def init_claimed_list(self):
        for child in self._children:
            child.init_claimed_list()
            items = child._chain
            self._chain.extend(items)
            child._chain = []

    def update_boundary_chain(self, M):
        """
        Top level nesting to handle subsets
        """
        unique_nexts = set()
        for child in self._children:
            for automaton in child._chain:
                for next_state in automaton.next_states():
                    if M.is_open(next_state.pos) == True:
                        unique_nexts.add(next_state)
        return unique_nexts

