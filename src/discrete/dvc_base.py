import numpy as np
from copy import deepcopy


class Site(object):
    def distance_to(self, pixel):
        return


class Automaton4(object):
    _MOVES = [
        [0, 1],   # up
        [0, -1],  # down
        [1, 0],   # right
        [-1, 0],  # left
    ]

    def __init__(self, pos, moves=None):
        self._pos = pos
        self._moves = moves if moves else self._MOVES

    def next_states(self):
        for m in self._moves:
            new_moves = deepcopy(self._MOVES)
            new_moves.remove( (np.array(m)*-1).tolist() )
            new_pos = [self._pos[0] + m[0], self._pos[1] + m[1]]
            yield Automaton4(new_pos, new_moves)

    def constrain(self, constraints):
        for constraint in constraints:
            if constraint in self._moves:
                self._moves.remove(constraint)

    @property
    def pos(self):
        return np.asarray(self._pos)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if other._pos == self._pos:
                return True
        return False

    def __str__(self):
        return '<{}> at {}'.format(self.__class__.__name__, self._pos)

    def __hash__(self):
        return tuple(self._pos).__hash__()


class DiscreteCell(object):
    def __init__(self, x, y,
                 ix=None,
                 source=None,
                 step_every=1):
        self.x = x
        self.y = y
        self.index = ix
        self.source_point = source
        self._step_every = step_every
        self._chain = []
        self._next_chain = []

    def __str__(self):
        return '<{}> at {} {}'.format(self.__class__.__name__, self.x, self.y)

    def init_claimed_list(self, dvor):
        aut = Automaton4([self.x, self.y])
        dvor.claim_pixel(self, aut)
        self._chain = [aut]

    def add_boundary(self, boundary):
        self._chain.append(boundary)

    def should_step(self, step):
        # todo this can be more granular if made stochastic ...
        # return step % self._step_every == 1
        return True

    def distance_to(self, pixel):
        # TODO THIS IS PART OF SITE
        return ((pixel[0] - self.x) ** 2 + (pixel[1] - self.y) ** 2) ** 0.5

    @property
    def boundary_chain(self):
        return self._chain

    def update_boundary_chain(self, M):
        unique_nexts = set()
        for automaton in self._chain:
            for next_state in automaton.next_states():
                if next_state in unique_nexts:
                    continue
                if M[next_state.pos] == 0:
                    unique_nexts.add(next_state)
        self._next_chain = unique_nexts
        return unique_nexts


class DiscreteVoronoi(object):

    def __init__(self, points=None, space=None, x=512, y=512):
        self._cells = []
        self.M = space
        self._step = 0
        if points is not None and space is not None:
            self._setup_cells(points)

    def __len__(self):
        return len(self._cells)

    def _setup_cells(self, points):
        num_cells = 0
        for pt in points:
            # assert that this point is ok
            if len(pt) == 2:
                x, y = pt
                w = 1
            else:
                x, y, w = pt

            # embed in image
            dx = int(self.M.shape[0] * x)   # //
            dy = int(self.M.shape[1] * y)   # // self.M.shape[1]

            # compute how often a step will happen
            dw = w

            # add the cell
            cell = DiscreteCell(dx, dy, ix=num_cells, source=(x, y), step_every=dw)
            self._cells.append(cell)
            num_cells += 1
        return

    def claim_pixel(self, cell, p):
        if isinstance(p, (list, tuple)):
            px = np.asarray(p)
        elif isinstance(p, Automaton4):
            px = p.pos
        else:
            px = p
        if hasattr(cell, 'index'):
            cell_ix = cell.index
        else:
            cell_ix = cell
        # do some stuff
        # print(px, cell_ix)
        self.M[px] = cell_ix

    def distance_test(self, cell1, cell2, pixel):
        """

        return the cell to which pixel is closer
        """
        d1 = cell1.distance_to(pixel)
        d2 = cell2.distance_to(pixel)
        return cell1 if d1 < d2 else cell2

    def claim_cells(self, claimed, boundary_list, cell):
        """
        Check that newly created 'boundary list' items have not been
        claimed by another cell.
        if they are claimed, then check which cell's site is closer
        """
        for b in boundary_list:
            pos = tuple(b.pos.tolist())
            if pos in claimed:
                cell_ix, cur_b = claimed[pos]
                current_claim = self._cells[cell_ix]
                best_ix = self.distance_test(cell, current_claim, pos).index
                if best_ix == cell_ix:
                    claimed[pos] = [best_ix, b]
            else:
                claimed[pos] = [cell.index, b]
        return claimed

    def create_voronoi(self, verbose=False, stop=None):
        """
        for all p_i in P do
            L_C_i ⇐ initializeClaimedCellList( p i , M)

        while L_C_i != ∅ ∀ i do
            for all p_i in P do
                L_B_i ⇐ updateBoundaryChain( L_C_i, M, P)
                L_C_i ⇐ claimCells( L_B_i, M, P)
        """
        last_done = 0
        active_cells = list(range(len(self)))
        for cell in self._cells:
            cell.init_claimed_list(self)

        while active_cells:
            claimed = {}
            for i in active_cells:
                cell = self._cells[i]
                if cell.should_step(self._step):
                    # in theory i should only check conflicts for cells in
                    # start of the deluany graph (neighborhood kernel) of cell
                    boundry_list = cell.update_boundary_chain(self.M)
                    claimed = self.claim_cells(claimed, boundry_list, cell)
                cell._chain = []

            for pos, (cell_ix, boundary) in claimed.items():
                self._cells[cell_ix].add_boundary(boundary)
                self.claim_pixel(cell_ix, pos)

            self._step += 1
            if verbose is True:
                print(self._step, len(active_cells), self.M.n_filled, len(claimed))

            if stop is not None and stop < self._step:
                return

            if last_done == self.M.n_filled:
                return
            else:
                last_done = self.M.n_filled
        return

    # Misc apis ------------------------------------------
    def to_image(self):
        from PIL import Image
        a, b = self.M.shape
        ds = np.copy(self.M.np)
        ds *= 255 / len(self._cells)
        stk = np.uint8(np.stack([ds, ds, ds], -1))
        return Image.fromarray(stk)

    @property
    def inputs(self):
        """ test api -
        todo move to seperate class
        """
        return []

