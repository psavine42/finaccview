from .cell import *
import networkx as nx
from .flow import FlowNode


class BSpace(object):
    """ Boundaries only """
    def __init__(self):
        self._boundaries = {}
        self._data = {}

    def add_boundary(self, name, _to=None):
        self._boundaries[name] = Boundary()


class LSpace(object):
    """
    Class for storing visualizations
    - keeps track
    -keeps track of filters
    -does layout (this should be just voronoi cells)
    - trick is scaling ...
    """
    def __init__(self):
        self._count = 0
        self._cells = {}        # nodes
        self._boundaries = {}   # edges
        self._data = []         #
        self.add_cell(World(self))

    def __getitem__(self, *item):
        """
        return a cell or boundary between cells
        """
        if all([isinstance(x, str) for x in item]):
            item = ''.join(item)
        if isinstance(item, str):
            return self._cells[item]
        elif len(item) == 2:
            return self._cells[item[0]][item[1]]

    @property
    def keys(self):
        return list(self._cells.keys())

    @property
    def boundaries(self):
        res = []
        for c in self._cells:
            for b in c.boundaries:
                if b not in res:
                    res.append(b)
        return res

    def add_cell(self, cell, _from=[], to=[], w=False):
        """
        - add cells
        - create boundaries
        """
        if isinstance(cell, str):
            cell = LCell(cell, space=self)
        if w is True:
            self._cells['world'].bound_to(cell)
        self._cells[cell.name] = cell
        cell._space = self
        for src in _from:
            self._cells[src].bound_to(cell)
        for src in to:
            tgt_cell = self._cells[src]
            cell.bound_to(tgt_cell)
        return cell

    def add_boundary(self, cell1, cell2):
        c1 = self._cells.get(cell1, None)
        c2 = self._cells.get(cell2, None)
        if c1 and c2:
            boundary = c1.bound_to(c2)
            return boundary

    def add_flow(self, data, mag=0, cell=None):
        """
        adding flow
        path can be a tree?
        [ cell_1,
            [ cell_b1,
                [ cell_c1 ] ],
            [ cell_b2,
                [ cell_c2 ] ],
        ]
        """
        flow_id = self._count
        data['__index__'] = flow_id
        if cell is None:
            cell = 'world'
        node = FlowNode(flow_id, None, magnitude=mag)
        self[cell].add_flow(node)
        self._data.append(node)
        self._count += 1            # data is tracked
        # self.flow_to_cell(flow_id, cell)
        return node

    def flow_to_cell(self, flow_id, cell=None):
        if cell is None:
            cell = 'world'
        if isinstance(flow_id, int):
            pass
        self[cell].add_flow(flow_id)

    def boundary_graph(self):
        G = nx.DiGraph()
        for name, cell in self._cells.items():
            els = list(cell._inners.values()) + cell.boundaries
            for bnd in els:
                if bnd is None:
                    continue
                G.add_node(str(bnd), ntype='boundary')
                if name == 'world' and isinstance(bnd, Boundary):
                    G.add_edge('world', str(bnd))
                for nxt in bnd.successors:
                    if nxt is not None:
                        G.add_edge(str(bnd), str(nxt))
        return G

    def cell_graph(self):
        G = nx.DiGraph()
        for name, cell in self._cells.items():
            G.add_node(name)
            for bnd in cell.boundaries:
                if bnd.to_.name == name:
                    G.add_edge(bnd.from_.name, name)
                else:
                    G.add_edge(name, bnd.to_.name)
        return G

    def full_graph(self):
        G = nx.DiGraph()
        for name, cell in self._cells.items():
            G.add_node(name, ntype=cell.__class__.__name__)
            for bnd in cell.boundaries:
                G.add_node(bnd.name, ntype=bnd.__class__.__name__)
                G.add_edge(bnd.name, name)
                for nxt in bnd.successors:
                    G.add_edge(name, nxt.name)
        return G

    def plot(self):
        pass


def build_small():
    """

    Scenario 1:
    # cells - specification for cells
    ls = SetupSpace(cells)

    # add data to contract -> triggers budget +100
    ls['contract'].flow_to( {'id':0, amount:100 })

    ls['contract'].flow_to()

    --------------------------
    Scenario 2: budget

    ls = SetupSpace()
    ls.add_cell('budget', sign=0)

    ls.add_cell('budget_right', sign=1)
    ls.add_cell('budget_left',  sign=-1)

    ls['budget_left'].bound_to('budget',  sign=0)
    ls['budget_right'].bound_to('budget', sign=0)

    # ----------------
    ls.add_cell('contract', sign=1)

    ls['contract'].bound_to('budget') # sign becomes

    ls.add_cell('subcontract', sign=-1)

    ls['subcontract'].bound_to('world')
    ls['subcontract'].bound_to('budget')

    # add flow to budget
    ls['budget'].add(100, code=0)

    ls['contract'].add(50, code=0)

    ls['budget_left'].size
    >> 50

    # -------------------------
    adding data in 'tree' form


    """

    cells = {
        'prime': {
            'sign': +1,
            'boundaries': {'budget'}
        },
        'budget': {
            # no connection to world in this scenario
            'sign': 0,
            'boundaries': {'cost'}
        },
        'cost': {
            'sign': -1,
            'boundaries': {'cost'}
        },
        'cost_change': {
            'sign': +1,
            'boundaries': {'cost'}
        },
        'prime_change': {
            'sign': -1,
            'boundaries': {'prime'}
        }
    }






def build_space(data, states):
    """
    states - partially ordered list of which cells this goes to ...
    partial order should be a valid path
    ( features ) U ( Datum x Cells )


    """
    G = nx.DiGraph()

    boundaries = {

    }

    G.add_edges_from([
        ('World', 'Budget'),
        ('World', 'PrimeContract'),
        ('World', 'CostContract'),
        ('World', 'CostCOR'),
        ('World', 'BudgetPCO'),
        ('PrimeContract', 'Budget'),
        ('CostContract', 'Budget'),
        ('CostCOR', 'CostContract'),
        ('BudgetPCCO', 'PrimeContract'),
        ('BudgetCOR', 'BudgetPCCO'),
        ('BudgetPCO', 'BudgetCOR'),
        ('BudgetPCO', 'BudgetPCO_Noop'),
        ('BudgetPCO', 'BudgetPCO_Noop'),
    ])

    space = LSpace()
    for d in data:
        space.flow_to_cell(d)
        for s in states:
            if d.get(s, False) is True:
                space.flow_to_cell(d, s)

    return space

