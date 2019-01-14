import numpy as np


class DiscreteSpace(object):
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

    def metric(self, p1, p2):
        return

    def is_open(self, key):
        return

    @property
    def is_filled(self):
        return


class BoundedSpace_Z2(DiscreteSpace):
    """
    Stored as numpy array with a metric
    """
    def __init__(self, x=512, y=512):
        DiscreteSpace.__init__(self)
        self._data = np.zeros((x, y))

    @property
    def shape(self):
        return self._data.shape

    def __len__(self):
        return self._data.shape[0] * self._data.shape[1]

    def metric(self, p1, p2):
        """ euclidean - per paper """
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

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

    def is_open(self, key):
        return self.__setitem__(key, 0)

    @property
    def n_filled(self):
        return len(np.where(self._data == 0)[0])

    @property
    def is_filled(self):
        return self.n_filled == 0

    @property
    def np(self):
        return self._data

