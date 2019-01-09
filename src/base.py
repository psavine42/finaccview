

class DataNode(object):
    def __init__(self, space, **kwargs):
        self._space = space
        self._data = []

    def __contains__(self, item):
        return item in self._data

    def get_datum(self, item):
        if item in self._data:
            return self._space.get_data(item)

    def append(self, item):
        self._data.append(item)

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


class SpaceNode(object):
    def __init__(self, space, *args, **kwargs):
        self._data = DataNode(space)

    def __repr__(self):
        return '<{}>:{}'.format(self.__class__.__name__, self.name)

    def get_datum(self, item):
        return self._data.get_datum(item)

    @property
    def space(self):
        return self._data.space

    @property
    def data(self):
        return self._data

    @property
    def name(self):
        return ''

    @property
    def members_dict(self):
        return {}

    @property
    def predecessors(self):
        return []

    @property
    def successors(self):
        return []

    def __contains__(self, item):
        if isinstance(item, str):
            name = item
        elif hasattr(item, 'name'):
            name = getattr(item, 'name', '')
        else:
            name = None
        return name in self.members_dict

    def flow_to(self, flow_or_id):
        return flow_or_id


class SubSpaceNode(object):
    def __init__(self):
        pass

