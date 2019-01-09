from .boundary import bound_name


class FlowNode(object):
    def __init__(self,
                 index,
                 state,
                 magnitude=0.,
                 parent=None,
                 positive=True,
                 **meta):
        # object.__init__(self, **meta)
        self._id = index
        self._size = magnitude
        self._children = []
        self._parent = parent
        self._state = state

    @property
    def path(self):
        yield self
        for c in self._parent:
            yield c

    @property
    def parent(self):
        return self._parent

    @property
    def location(self):
        return self._state

    def info(self):
        if self._state is not None:
            self._state.get_datum(self._id)

    def flow_to(self, cell=None):
        next_state = None
        nxt_states = self._state.successors
        if len(nxt_states) == 1:
            next_state = nxt_states[0]

        elif cell in nxt_states:
            next_state = cell

        if next_state is not None:
            nxt_flow = FlowNode(self._id, nxt_states[0],
                                magnitude=self._size,
                                parent=self)
            self._children.append(nxt_flow)
            nxt_states[0].add_flow(nxt_flow)
            return nxt_flow

    @property
    def next_states(self):
        return self._state.successors

    @property
    def root(self):
        if self._parent is None:
            return self
        else:
            return self._parent.root

    def change_sign(self):
        self._size = -1.0 * self._size

    def add_children(self, *args):
        self._children.extend(*args)

    def split(self, amount=None, rel=None):
        """

        :param target:
        :param amount:
        :param rel:
        Return
        -----------
        children flows which have been
        """
        if amount is None and rel is None:
            raise Exception
        elif isinstance(rel, float):
            new = self._size * rel
            other = self._size - new
            o1 = FlowNode(self._id, None, magnitude=other, parent=self)
            o2 = FlowNode(self._id, None, magnitude=new, parent=self)
            self.add_children(o1, o2)
            return o1, o2

