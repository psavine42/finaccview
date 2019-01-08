from abc import ABC
from .boundary import Boundary, bound_name
from .base import SpaceNode
from .inner import Inner
from .flow import FlowNode


class LCell(SpaceNode):
    """
    Node-like
    """
    def __init__(self, name, space, **data):
        SpaceNode.__init__(self, space, **data)
        self._name = name
        self._flows = []
        self._boundaries = {}
        self._inners = {}

    def __getitem__(self, item):
        """ return a boundary.
            if given boundary name, returns that one
            if given cell name, return boundary between
        """
        if item in self._boundaries:
            return self._boundaries.get(item, None)
        else:
            for b in self.boundaries:
                if item in [b.from_.name, b.to_.name] :
                    return b
            return None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if other.name == self.name:
                return True
        return False

    def __str__(self):
        return '<{}>:{}'.format(self.__class__.__name__, self.name)

    @property
    def boundaries(self):
        return list(self._boundaries.values())

    @property
    def successors(self):
        return [b for b in self.boundaries if b.from_ == self]

    @property
    def predecessors(self):
        return [b for b in self.boundaries if b.to_ == self]

    @property
    def neigh_cells(self):
        res = {}
        for b in self.boundaries:
            cell_from, cell_to = b.from_, b.to_
            if cell_from == self:
                res[cell_to.name] = cell_to
            else:
                res[cell_from.name] = cell_from
        return res

    @property
    def name(self):
        return self._name

    # setup ----------------------------------
    def bound_to(self, *args):
        """
        given (self, other_cell) create boundary between cells
        """
        # print(args)
        if len(args) == 1:
            # create boundary between self and another cell
            other_cell = args[0]
            if isinstance(other_cell, str):
                other_cell = self.space[other_cell]
            bound = Boundary(self, other_cell)
            self._boundaries[bound.name] = bound
            other_cell._boundaries[bound.name] = bound
            return bound

        elif len(args) == 2:
            # connect 2 boundaries from cell
            # cell_from--[b1]--self--[b2]--cell_to
            # -> [b1]--[balance]--[b2]
            cell_from, cell_to = args
            cells = self.space.keys
            neigh_cell = self.neigh_cells

            if cell_from not in cells or cell_to not in cells:
                print('missing cell')
                return None

            if cell_from not in neigh_cell:
                bound_from = cell_from.bound_to(self)
            else:
                bound_from = bound_name(neigh_cell[cell_from], self)
                bound_from = self._boundaries[bound_from]

            if cell_to not in neigh_cell:
                bound_to = self.bound_to(cell_to)
            else:
                bound_to = bound_name(self, neigh_cell[cell_to])
                bound_to = self._boundaries[bound_to]

            if bound_from and bound_to:
                b = Inner(self, bound_from, bound_to)
                bound_from.add_successor(b)
                # self._balances.append(b)
                return b
            print('missing item ')
            return

    # flows -------------------------------------
    def add_flow(self, data):
        if isinstance(data, int):
            self._flows.append(self.get_datum(data))
        elif isinstance(data, FlowNode):
            data._state = self
            self._flows.append(data)


class World(LCell):
    def __init__(self, space):
        LCell.__init__(self, 'world', space=space)
        self._inners['default'] = Inner(self, None)

    @property
    def successors(self):
        return self.boundaries

    @property
    def predecessors(self):
        return self

    def add_flow(self, data):
        if isinstance(data, int):
            self._flows.append(self.get_datum(data))
        elif isinstance(data, FlowNode):
            data._state = self
            self._flows.append(data)


class SinkCell(LCell):
    """
    Sinks have no outputs. when something is not linked to next state, they end up in a sink
    """
    def __init__(self, *args, **kwargs):
        LCell.__init__(*args, **kwargs)

    def outputs(self):
        return []


