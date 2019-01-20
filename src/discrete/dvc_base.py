import numpy as np
from .automota import Automaton4
from . import discrete_cell as dc
from .discrete_cell import DiscreteSite, ShapeSite, \
    WeightedSite, SegmentSite
from . import utils as utils
from .disc_edges import DiscreteEdge
from collections import defaultdict as ddict
from collections import deque
from abc import ABC, abstractmethod
from PIL import Image
"""
Voronoi Diagrams that are
1). Nested
2). Constrained
    - space with holes
    - 
3). Weighted
4). Shaped
5). Combinations
"""


class SiteGenerator(object):
    PLANAR = True

    def __init__(self, *args, cls=DiscreteSite):
        self._sites = []
        self._cls = cls

        if cls == DiscreteSite:
            pass
        elif cls == ShapeSite:
            pass
        elif cls == SegmentSite:
            pass
        elif cls == WeightedSite:
            pass

    def _prep_site(self, tgt):
        pass

    def __iter__(self):
        for site in self._sites:
            yield site


class _DVoronoi(ABC):
    @abstractmethod
    def _setup_cells(self, pts, **kwargs):
        pass

    @abstractmethod
    def claim_cells(self, claimed, boundaries, cell):
        pass

    @abstractmethod
    def create_voronoi(self, **kwargs):
        pass


class DiscreteVoronoi(object):
    def __init__(self,
                 points=None,
                 space=None,
                 stop=None,
                 verbose=False,
                 save=None,
                 bins=1,
                 go=True):
        self._cells = [None]
        self.M = space
        self._save = save
        self._step = 0
        self._stop = stop
        self._verbose = verbose
        if points is not None and space is not None:
            self._setup_cells(points, bins=bins)
            if go:
                self.create_voronoi()

    def __len__(self):
        return len(self._cells)

    def __getitem__(self, item):
        return self._cells[item]

    @property
    def sites(self):
        return self._cells[1:]

    def _setup_cells(self, pts, bins=1):
        """
        points:     [n, 2]
        segments:   [n, 4]
        Shapes:     [n, m, 2]
        +1 if weighted
        """
        if isinstance(pts, list):
            pts = np.asarray(pts)

        if pts.shape[1] % 2 == 1:
            hist, edges = np.histogram(pts[:, -1], bins=bins)
            pts[:, -1] = np.digitize(pts[:, -1], edges)
            if self._verbose:
                print(edges)
                print(pts)

        dimx, dimy = self.M.shape[0], self.M.shape[1]
        for pt in pts:
            # assert that this point is ok
            if len(pt) in [2, 3]:
                cls = DiscreteSite
                x, y = pt[0:2]
                w = pt[-1] if len(pt) == 3 else 1
                # compute how often a step will happen
                site = cls(int(dimx * x), int(dimy * y),
                           parent=self,
                           ix=len(self),
                           source=(x, y),
                           step_every=int(w))

            elif len(pt) in [4, 5]:
                cls = SegmentSite
                x1, y1, x2, y2 = pt[0:4]
                w = pt[-1] if len(pt) == 5 else 1
                dx1, dx2 = int(dimx * x1), int(dimx * x2)
                dy1, dy2 = int(dimy * y1), int(dimy * y2)
                site = cls(dx1, dy1, dx2, dy2,
                           parent=self,
                           ix=len(self),
                           source=pt,
                           step_every=int(w))
            else:
                print('incorrect point size : ', pt)
                continue

            # add the cell
            self._cells.append(site)

        return

    def _step_hooks(self, active_cells, claimed):
        stop = False
        if self._verbose is True:
            print(self._step, len(active_cells), self.M.n_filled, len(claimed))
        if self._save is not None and self._step % self._save == 0:
            self.to_image(size=(500, 500), out='./out/imgs/{}.jpeg'.format(self._step))
        if stop is not None and stop < self._step:
            return False
        return False

    def claim_pixel(self, site, p):
        if isinstance(p, (list, tuple)):
            px = np.asarray(p)
        elif isinstance(p, Automaton4):
            px = p.pos
        else:
            px = p
        if hasattr(site, 'index'):
            cell_ix = site.index
        else:
            cell_ix = site
        self.M[px] = cell_ix

    def distance_test(self, cell1, cell2, pixel):
        """

        return the cell to which pixel is closer
        """
        d1 = self.M.metric(cell1.pos, pixel)
        d2 = self.M.metric(cell2.pos, pixel)
        return cell1 if d1 < d2 else cell2

    def claim_cells(self, claimed, boundaries, cell):
        """
        Check that newly created 'boundary list' items have not been
        claimed by another cell.
        if they are claimed, then check which cell's site is closer
        """
        for b in boundaries:

            pos = tuple(b.pos.tolist())

            if pos in claimed:
                cur_cell_ix, cur_b = claimed[pos]
                cur_claimer_cell = self[cur_cell_ix]

                best_ix = self.distance_test(cell, cur_claimer_cell, pos).index
                if best_ix == cell.index:
                    claimed[pos] = [cell.index, b]
            else:
                claimed[pos] = [cell.index, b]
        return claimed

    def _init_cell_sites(self):
        for site in self.sites:
            self.claim_pixel(site, site.pos.tolist())
            site.add_boundary(site.pos.tolist())

    def create_voronoi(self):
        """
        for all p_i in P do
            L_C_i ⇐ initializeClaimedCellList( p i , M)

        while L_C_i != ∅ ∀ i do
            for all p_i in P do
                L_B_i ⇐ updateBoundaryChain( L_C_i, M, P)
                L_C_i ⇐ claimCells( L_B_i, M, P)
        """
        self._init_cell_sites()
        last_done = 0
        active_cells = list(range(1, len(self)))
        while active_cells or not self.M.done:
            claimed = {}
            for i in active_cells:
                cell = self[i]
                if cell.should_step(self._step):
                    # in theory i should only check conflicts for cells in
                    # start of the deluany graph (neighborhood kernel) of cell
                    boundry_list = cell.update_boundary_chain(self.M)
                    claimed = self.claim_cells(claimed, boundry_list, cell)
                cell._chain = []

            for pos, (cell_ix, boundary_aut) in claimed.items():
                cell = self[cell_ix]
                if cell.should_step(self._step):
                    self[cell_ix].add_boundary(boundary_aut)
                    self.claim_pixel(cell_ix, pos)

            self._step += 1
            if last_done == self.M.n_filled:
                return
            last_done = self.M.n_filled
            self._step_hooks(active_cells, claimed)
            if self._stop is not None and self._stop < self._step:
                return
        return

    # Misc apis ------------------------------------------
    def to_image(self, size=(768, 768), out=None):
        # a, b = self.M.shape
        # ds = np.zeros(self.M.shape)
        ds = np.copy(self.M.np)
        ds *= (255 / (len(self.sites) + 2))
        for cell in self.sites:
            ds[cell.x, cell.y] = 255

        stk = np.uint8(np.stack([ds, ds, ds], -1))
        img = Image.fromarray(stk)
        if isinstance(size, (int, tuple)):
            img = img.resize(size, Image.ANTIALIAS)
        if isinstance(out, str):
            img.save(out)
        return img

    def to_svg(self):
        return

    def linear(self):
        for cell in self._cells:
            pass
        return

    @property
    def inputs(self):
        """ test api -
        todo move to seperate class
        """
        return []


class VoronoiDBC(DiscreteVoronoi):
    """
    Discrete, Bound, Constrained (DBC)
    """
    def __init__(self, adj=None, go=True, **kwargs):
        """
        G is a nx.graph of which sites will be connected

        what are the data structures to track the boundary
            1) each site tracks its own boundaries as a list
            2) central matrix wiht dim for boundaries between 2 indices
            3)
        """
        DiscreteVoronoi.__init__(self, go=False, **kwargs)
        self._target_edges = ddict(int)     # {(site1, site2) : edge}
        self._edges = {}
        for args in adj:
            if len(args) == 2:
                i1, i2 = args
                w = 100
            else:
                i1, i2, w = args
            tgt = tuple(sorted([i1+1, i2+1]))
            self._target_edges[tgt] = w

        if go:
            self.create_voronoi()

    def _init_cell_sites(self):
        """
        claim points on lines between connected sites.
        these will be seeds for boundary edges.
        """
        for (i1, i2), w in self._target_edges.items():
            site1, site2 = self[i1], self[i2]
            # print(i1, i2)
            # nearest point between site basis, and claim line
            p1, p2 = utils.nearest_points(site1.pos, site2.pos)
            seg = utils.discretize_segment(p1, p2)
            disc_weight = len(seg) // 2

            if p1.tolist() == seg[-1]:
                seg = seg[::-1]
            print(i1, i2, disc_weight, seg[0], seg[-1])

            for x, y in seg[:disc_weight]:
                self.claim_pixel(site1, [x, y])
                site1.add_boundary([x, y])

            for x, y in seg[disc_weight:]:
                self.claim_pixel(site2, [x, y])
                site1.add_boundary([x, y])
        #
        # for site in self.sites:
        #    self.claim_pixel(site, site.pos.tolist())
        #    site.add_boundary(site.pos.tolist())

    def claim_cells(self, claimed, boundaries, new_site):
        """
        Check that newly created 'boundary list' items have not been
        claimed by another cell.
        if they are claimed, then check which cell's site is closer
        """
        new_site_ix = new_site.index
        for b in boundaries:
            pos = tuple(b.pos.tolist())

            if pos not in claimed:
                # no other site has a claim to the pixel
                claimed[pos] = [new_site_ix, b]
                continue

            # check for boundary extended case
            # check that these cells should touch
            cur_site_ix, cur_b = claimed[pos]
            border_ix = tuple(sorted([new_site_ix, cur_site_ix]))
            cur_site = self[cur_site_ix]
            target_size = self._target_edges.get(border_ix, None)

            # if edge between sites does not exist
            edge = self._edges.get(border_ix, None)
            if target_size is not None and edge is None:
                edge = DiscreteEdge(cur_site, new_site, target_size)
                self._edges[border_ix] = edge
                edge.append(b)

            elif target_size is not None and edge is not None:
                if not edge.done:
                    edge.append(b)

            elif target_size is None:
                # if there is no connection between cells, then do nothing
                continue

            # which cell gets the boundary ?
            best_ix = self.distance_test(new_site, cur_site, pos).index
            if best_ix == new_site_ix:
                claimed[pos] = [new_site_ix, b]

        return claimed

