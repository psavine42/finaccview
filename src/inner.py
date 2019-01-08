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
        return '{}--->[{}]'.format(self._pred.name, ds)

    def add_flow(self, flow_id):
        flow = self.get_datum(flow_id)
        o1 = FlowNode(flow_id, None, magnitude=flow.size, parent=flow)
        self._sucs[0].flow_to(o1)
        return o1


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
