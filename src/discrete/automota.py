import numpy as np
from copy import deepcopy


class Automaton(object):
    _MOVES = []

    def __init__(self, pos, moves=None):
        self._pos = pos
        self._matrix = None
        # self._step_every = step_every
        self._moves = moves if moves else self._MOVES

    @property
    def pos(self):
        return np.asarray(self._pos)

    def next_states(self):
        for m in self._moves:
            new_moves = deepcopy(self._MOVES)
            new_moves.remove( (np.array(m)*-1).tolist() )
            new_pos = [self._pos[0] + m[0], self._pos[1] + m[1]]
            yield self.__class__(new_pos, moves=new_moves)

    def constrain(self, constraints):
        for constraint in constraints:
            if constraint in self._moves:
                self._moves.remove(constraint)

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            if other._pos > self._pos:
                return True
        return False

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            if other._pos < self._pos:
                return True
        return False

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if other._pos == self._pos:
                return True
        return False

    def __str__(self):
        return '<{}> at {}'.format(self.__class__.__name__,
                                   self._pos)

    def __hash__(self):
        return tuple(self._pos).__hash__()


class Automaton4(Automaton):
    _MOVES = [
        [0, 1],     # up
        [0, -1],    # down
        [1, 0],     # right
        [-1, 0],    # left
    ]

    def __init__(self, pos, moves=None):
        Automaton.__init__(self, pos, moves=moves)


class Automaton8(Automaton):
    _MOVES = [
        [0, 1], [0, -1], [1, 0], [-1, 0],
        [1, 1], [-1, -1], [1, -1], [-1, 1]
    ]

    def __init__(self, pos, moves=None):
        Automaton.__init__(self, pos, moves=moves)


