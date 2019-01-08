from .base import SpaceNode


def bound_name(from_, to_):
    return '[{}]->[{}]'.format(from_.name, to_.name)


class Boundary(SpaceNode):
    """
    'Edge-Like'
    ----++-------
        ||
     c1 ||   c2
        ||
    ----++-------
    """
    def __init__(self, from_cell, to_cell, sign=None):
        SpaceNode.__init__(self, from_cell.space)
        self._from = from_cell
        self._to = to_cell
        self._sign = sign
        self._successors = {}

    @property
    def from_(self):
        return self._from

    @property
    def to_(self):
        return self._to

    @property
    def name(self):
        """ name is something like (sign is
            [cell1]--(+)-->[cell2]
        """
        return bound_name(self._from, self._to)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if other.name == self.name:
                return True
        return False

    def __str__(self):
        return '<{}>:{}'.format(self.__class__.__name__, self.name)

    def __getitem__(self, item):
        """ lookup connected boundaries """
        return self._successors.get(item, None)

    def __iter__(self):
        pass

    def add_successor(self, bnd_or_balance):
        self._successors[bnd_or_balance.name] = bnd_or_balance

    @property
    def predecessors(self):
        return [self.from_]

    @property
    def successors(self):
        return list(self._successors.values())

    def state_space(self):
        yield self
        for boundary in list(self._successors.values()):
            yield boundary

    # setup ----------------------------------
    def connect(self, other):
        if isinstance(other, Boundary):
            self._successors[other.name] = other
            return
        other_bndry = self._to[other]
        if other_bndry is None:
            other_bndry = self._to.bound_to(other)
        if other_bndry is not None:
            self._successors[other.name] = other_bndry
        return

    # flows ----------------------------------
    def add_flow(self, flow_or_id):
        """
        bnd1.flow_to(bnd2, data)
        adds index of this datum to

        """
        if isinstance(flow_or_id, int):
            flow = self.get_datum(flow_or_id)
        else:
            flow = flow_or_id
        # flow.flow_to(self._to)
        self.data.append(flow)
        return flow


