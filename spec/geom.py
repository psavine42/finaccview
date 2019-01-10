import unittest
import src.voronoie as vor
import importlib
import src.visual
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
seed = np.random.seed(69)


def MakeChart(data, hour, coordinates, lineweights, codes):
    cmap = plt.cm.get_cmap('YlOrRd')
    fig = plt.figure(num=None, figsize=(15, 10), dpi=150, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111)
    ax.set_title('Winter Day: Hour '+str(hour), fontsize=20, fontweight='bold')
    for i in range(0, len(codes)):
        if coordinates[i] != "null":
            path = Path(coordinates[i], codes[i])
            patch = patches.PathPatch(path, facecolor=cmap(data), lw=lineweights[i])
            ax.add_patch(patch)
    ax.autoscale_view()
    plt.axes().set_aspect('equal', 'datalim')
    plt.show()


def plot_lines(context):
    for k, edges in context.polygons.items():
        for l, v1, v2 in edges:
            if -1 in [v1, v2]:
                pass
            else:
                p1 = context.vertices[v1]
                p2 = context.vertices[v2]
                plt.plot(p1, p2, 'k-')
    for p in context.inputs:
        plt.plot([p[0]], [p[1]], 'o')
    plt.show()


class TestVor(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basic(self):
        inputs = np.random.rand(6, 2)
        print(inputs.shape)
        pts = [vor.Site(x, y) for (x, y) in inputs.tolist()]
        context = vor.computeVoronoiDiagram(pts, ctx=True)
        return context

    def test_basic2(self):
        domain = [[0., 0.], [0., 1.], [1., 1.], [1., 0.]]
        inputs = [[0.25, 0.25], [0.5, 0.5], [0.73, 0.23], [0.76, 0.76], [0.24, 0.74]]
        pts = [vor.Site(x, y) for (x, y) in inputs]
        context = vor.computeVoronoiDiagram(pts, ctx=True)
        return context


def setup():
    importlib.reload(vor)
    ctx = TestVor().test_basic2()
    return ctx
