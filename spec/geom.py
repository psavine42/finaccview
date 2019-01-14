import unittest
import src.voronoie as vor
import importlib
import tess
import src.visual
import spec.vro as vor1
import numpy as np
import CGAL.CGAL_Voronoi_diagram_2 as cgalvor
import spec.cgtests as cg
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

seed = np.random.seed(68)
from src.geo import Line

def RL(*args):
    for a in args:
        importlib.reload(a)


def plot_lines(context):
    if context is not None:
        for l, v1, v2 in context.edges:
            if v1 == -1:
                pass
            elif v2 == -1:
                pass
            else:
                p1 = context.vertices[v1]
                p2 = context.vertices[v2]
                plt.plot(p1, p2, 'k-')
    for p in context.inputs:
        plt.plot([p[0]], [p[1]], 'o')
    plt.show()


def vertex_coord(vertex):
    p = vertex.point()
    return p.x(), p.y()


def edge_pts(edge):
    p1 = edge.source().point()
    p2 = edge.target().point()
    return [p1.x(), p1.y()], [p2.x(), p2.y()]


def plotv(context):
    fig, ax = plt.subplots()
    edges, sites = [], []
    if isinstance(context, (cg.WVoronoi, cg.Voronoi)):
        for edge in context.edges:
            print(edge.is_ray(), edge.is_segment(), edge.is_bisector())
            if edge.has_source() and edge.has_target():
                pts = edge_pts(edge)
                print(pts)
                edges.append(pts)
            elif edge.has_target():
                p = edge.target().point()
                plt.plot(p.x(), p.y(), 'x')
                print(p.x(), p.y())
            elif edge.has_source():
                p = edge.source().point()
                plt.plot(p.x(), p.y(), 'x')
                print(p.x(), p.y())

    elif isinstance(context, tess.Container):
        for cell in context:
            verts = cell.vertices()
            for i in range(1, len(verts)):
                edges.append([verts[i-1][:2], verts[i][:2]])

    ax.set_xlim((0, 1.5))
    ax.set_ylim((0, 1.5))
    for p in context.inputs:
        if len(p) == 2:
            plt.plot([p[0]], [p[1]], 'o')
        elif len(p) == 3:
            plt.plot([p[0]], [p[1]], 'o')
            p = plt.Circle((p[0], p[1]), p[2],
                           clip_on=False, color='b', fill=False)
            ax.add_artist(p)
    for e in edges:
        plt.plot([e[0][0], e[1][0]], [e[0][1], e[1][1]], 'k-')
    plt.show()


def resolve_edge(edge):
    pux, puy = vertex_coord(edge.up())
    pdx, pdy = vertex_coord(edge.down())
    plx, ply = vertex_coord(edge.left())
    prx, pry = vertex_coord(edge.right())
    print(pux, puy, pdx, pdy, plx, ply,prx, pry  )
    return


class TestVor(unittest.TestCase):
    def setUp(self):
        self.domain = [[0., 0.], [0., 1.], [1., 1.], [1., 0.]]
        self.inputs = [[0.25, 0.25], [0.5001, 0.5], [0.73, 0.23], [0.76, 0.76], [0.242, 0.7422]]
        self.weight = [0.4, 0.1, 0.2, 0.2, 0.2]
        self.weighted = [[x, y, w/2] for (x, y), w in zip(self.inputs, self.weight)]

    def random_n(self, n):
        inputs = np.random.rand(n, 3)
        inputs[:, -1] *= 0.1
        return inputs

    def tearDown(self):
        pass

    def test_basic(self):
        inputs = np.random.rand(7, 2)
        print(inputs.shape)
        pts = [vor.Site(x, y) for (x, y) in inputs.tolist()]
        context = vor.VoronoiDiagram(pts, ctx=True)
        return context

    def test_basic2(self):
        pts = [vor.Site(x, y) for (x, y) in self.inputs]
        context = vor.VoronoiDiagram(pts, ctx=True, debug=True)
        return context

    def test_basic3(self):
        return vor1.Voronoi(self.inputs)

    def test_basic4(self):
        vr = tess.Container([[x, y, 0.0] for x, y, w in self.weighted],
                            radii=[x[-1] for x in self.weighted],
                            limits=((0., 0., -1.), (1., 1., 1.)))
        plotv(vr)

    def test_basic5(self):
        vr = cg.WVoronoi(self.weighted)
        plotv(vr)

    def test_basic6(self):
        vr = cg.WVoronoi(self.random_n(6))
        plotv(vr)

    def test_basic7(self):
        vr = cg.Voronoi(self.random_n(6))
        plotv(vr)




def setup(opt=5):
    RL(tess, vor, vor1, cg)
    ctx = TestVor()
    ctx.setUp()
    if opt == 4:
        return tess.Container(ctx.weighted, limits=(1., 1., 1.))
    if opt == 5:
        return cg.WVoronoi(ctx.weighted)
