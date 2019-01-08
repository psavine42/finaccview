

class SpaceNode(object):
    def __init__(self, space, **kwargs):
        self._space = space
        self._data = []

    @property
    def name(self):
        return ''

    def __contains__(self, item):
        return item in self._data

    def __repr__(self):
        return '<{}>:{}'.format(self.__class__.__name__, self.name)

    def get_datum(self, item):
        if item in self._data:
            return self._space.get_data(item)

    def append(self, item):
        self._data.append(item)

    @property
    def data(self):
        return self._data

    @property
    def space(self):
        return self._space

    @property
    def size(self):
        """ compute the total amount of stuff going through self"""
        _space = self._space
        total = 0
        for d in self._data.__iter__():
            total += _space.get_data(d, {}).get('size', 0)
        return total

    # to implement ----------------------------
    @property
    def predecessors(self):
        return []

    @property
    def successors(self):
        return []

    def flow_to(self, flow_or_id):
        return flow_or_id


class SubSpaceNode(object):
    def __init__(self):
        pass

