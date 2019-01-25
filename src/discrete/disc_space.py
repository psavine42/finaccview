import numpy as np
from abc import ABC, abstractmethod
from . import utils as utils
from collections import deque
from PIL import Image
from itertools import product


class DiscreteSpace(ABC):
    """
    Abstract class for spaces.
    -spaces should:
        - have a distances metric
        - have size as __len__ attr
        - 'is_open' api to check if site has been claimed
            holes can be represented as -int, as closed subspaces
        - 'is_filled' - check if
    """
    def __init__(self):
        self._data = []

    def __len__(self):
        return len(self._data)

    def __contains__(self, item):
        pass

    def reset(self):
        return

    @abstractmethod
    def metric(self, p1, p2):
        return

    @abstractmethod
    def is_open(self, key):
        return

    @property
    @abstractmethod
    def done(self):
        return


class BoundedSpace_Z2(DiscreteSpace):
    """
    Stored as numpy array with a metric
    """
    def __init__(self, x=512, y=512):
        DiscreteSpace.__init__(self)
        self.x, self.y = x, y
        self._data = None
        self.reset()

    def reset(self):
        self._data = np.zeros((self.x, self.y)).astype(int)

    @property
    def area(self):
        return len(np.where(self._data >= 0)[0])

    @property
    def shape(self):
        return self._data.shape

    def __len__(self):
        return self._data.shape[0] * self._data.shape[1]

    def is_open(self, key):
        x, y = self._norm_key(key)
        if x is not None and y is not None:
            return self._data[x, y] == 0

    def metric(self, p1, p2):
        """ euclidean - per paper
            # todo why not manhattan ????
        """
        return (((p1[0] - p2[0]) ** 2) +
                ((p1[1] - p2[1]) ** 2)) ** 0.5

    def _norm_key(self, item):
        if isinstance(item, (list, tuple)):
            a, b = item[0], item[1]
        elif isinstance(item, np.ndarray):
            a, b = item[0].item(), item[1].item()
        elif isinstance(item, int):
            a, b = divmod(len(self), item)
        else:
            return None, None
        if isinstance(a, int) and isinstance(b, int):
            if 0 <= a < self._data.shape[0] \
                    and 0 <= b < self._data.shape[1]:
                return a, b
        return None, None

    def __getitem__(self, item):
        x, y = self._norm_key(item)
        if x is not None and y is not None:
            return self._data[x, y]

    def __setitem__(self, key, value):
        x, y = self._norm_key(key)
        if x is not None and y is not None:
            self._data[x, y] = value

    def set_if_open(self, key, value):
        x, y = self._norm_key(key)
        if x is not None and y is not None:
            if self._data[x, y] == 0:
                self._data[x, y] = value

    @property
    def n_filled(self):
        return len(np.where(self._data == 0)[0])

    @property
    def done(self):
        return self.n_filled == 0

    @property
    def np(self):
        return self._data

    def _crops(self, points, value=-1, inner=True):
        """
        outline of polygon to cutout -

        draws the segments, and then floodfill4 to mark
        """
        MOVES = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        points = np.array(list(utils.sort_points(points)))
        for i in range(len(points)):
            for x, y in utils.discretize_segment(points[i - 1], points[i]):
                self._data[x, y] = value

        if inner is True:
            center = utils.centroid(points).astype(int)
            q = deque([center])
        else:
            p1, p2 = self._data.shape
            p1 -= 1
            p2 -= 1
            q = deque([[0, 0], [p1-1, 0], [0, p2-1], [p1-1, p2-1]])
        while q:
            el = q.pop()
            self._data[el[0], el[1]] = value
            for m in MOVES:
                check = el + m
                if self[check] == 0:
                    q.append(check)

    def cutout(self, points):
        self._crops(points, value=-1, inner=True)

    def crop(self, points):
        self._crops(points, value=-1, inner=False)

    def to_image(self, size=(768, 768), out=None):
        ds = np.copy(self._data)
        vals = np.unique(ds)
        amin = np.min(vals)
        ds += amin
        stk = np.uint8(np.stack([ds, ds, ds], -1))
        for site in vals:
            c = np.asarray([
                np.random.randint(40, 255) for _ in range(3)
            ])
            stk[np.where(ds == site)] = c

        img = Image.fromarray(stk)
        if isinstance(size, (int, tuple)):
            img = img.resize(size, Image.ANTIALIAS)
        if isinstance(out, str):
            img.save(out)
        return img



class HeirachicalSpace(BoundedSpace_Z2):
    def __init__(self, **kwargs):
        BoundedSpace_Z2.__init__(self, **kwargs)
        self._data = []


