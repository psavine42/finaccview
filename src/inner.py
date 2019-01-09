from .base import SpaceNode
from .flow import FlowNode


class Inner(SpaceNode):
    """
    Abstraction for when two sets of flows must balance
    Thing1.size + thing2.size = 0
    """
    def __init__(self, cell, boundary_in, *args, **kwargs):
        SpaceNode.__init__(self, cell.space)
        self._cell = cell
        self._pred = boundary_in
        self._sucs = list(args)
        if self not in cell:
            cell._inners[self.name] = self
        if self not in self._pred:
            self._pred.add_successor(self)

    def __str__(self):
        return '<{}>:{}'.format(self.__class__.__name__, self.name)

    def __getitem__(self, item):
        if item == self._pred.name:
            return self._pred
        else:
            for b in self._sucs:
                if item == b.name:
                    return b
            return None

    @property
    def successors(self):
        return self._sucs

    @property
    def predecessors(self):
        return [self._pred]

    @property
    def name(self):
        ds = ','.join([x.name for x in self._sucs])
        pname = '' if self._pred is None else self._pred.name
        return '{}--->[{}]'.format(pname, ds)

    def add_flow(self, flow_id):
        flow = self.get_datum(flow_id)
        o1 = FlowNode(flow_id, None, magnitude=flow.size, parent=flow)
        self._sucs[0].flow_to(o1)
        return o1


class Balance(SpaceNode):
    def __init__(self, cell, *args, out=None):
        SpaceNode.__init__(self, cell.space)
        self._cell = cell
        self._pred = list(args)
        self._sucs = out
        if self not in cell:
            cell._inners[self.name] = self
        for b in self._pred:
            if self not in b:
                b.add_successor(self)

    def __getitem__(self, item):
        for b in self._pred:
            if item == b.name:
                return b
        if self._sucs is not None and item == self._sucs.name:
            return self._sucs
        return None

    @classmethod
    def from_cells(cls, cell, *args):
        bnds = []
        for arg in args:
            pass
        return

    @property
    def successors(self):
        if self._sucs:
            return [self._sucs]
        return []

    @property
    def predecessors(self):
        return self._pred

    @property
    def name(self):
        ds = ','.join([x.name for x in self._pred])
        pname = '' if self._sucs is None else self._sucs.name
        return '[{}]--B->{}'.format(ds, pname)

    def add_flow(self, flow_id):
        flow = self.get_datum(flow_id)
        o1 = FlowNode(flow_id, None, magnitude=flow.size, parent=flow)
        self._sucs[0].flow_to(o1)
        return o1


class ManyToOne(Balance):
    def __init__(self, cell, *args, **kwargs):
        Balance.__init__(self, cell, *args, **kwargs)



class PosNegSplit(Inner):
    def __init__(self, cell, bnd_in, *args):
        Inner.__init__(self, cell, bnd_in, *args)

    def add_flow(self, flow_id):
        flow = self.get_datum(flow_id)
        child1, child2 = flow.split()
        child2.change_sign()
        self._sucs[0].flow_to(child1)
        self._sucs[1].flow_to(child2)
        return child1, child2
