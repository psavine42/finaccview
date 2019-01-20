
class DiscreteEdge(object):
    def __init__(self, site1, site2, size=-1):
        self._s1 = site1
        self._s2 = site2
        self._target_size = size
        # edge can only
        self._cells = []

    def __len__(self):
        return len(self._cells)

    @property
    def head(self):
        if len(self._cells) > 0:
            return self._cells[0]

    @property
    def tail(self):
        if len(self._cells) > 0:
            return self._cells[-1]

    def _is_continuous(self):
        pass

    def append(self, cell):
        self._cells.append(cell)
        return cell

    @property
    def done(self):
        return self.__len__() >= self._target_size

    @property
    def sites(self):
        return self._s1, self._s2

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._s1 == other._s1 \
                   and self._s2 == other._s2
        return False

    def __hash__(self):
        return


class HalfEdge(object):
    """
    not sure yet if needed
    """
    def __init__(self, site1, size=-1):
        self._s1 = site1
        self._target_size = size
        self._cells = []

    def __len__(self):
        return len(self._cells)

    @property
    def sites(self):
        return self._s1

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._s1 == other._s1
        return False

    def __hash__(self):
        return

