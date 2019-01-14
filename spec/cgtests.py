from CGAL import CGAL_Kernel as k
from CGAL.CGAL_Kernel import Point_2, Weighted_point_2
import CGAL.CGAL_Voronoi_diagram_2 as vor2
import numpy as np
from src.geo import Line


# class CEdge(object):
"""

Point
    x, y

Vertex 
 'degree', 'dual',
 'halfedge', 'is_incident_edge',
 'is_incident_face',
 'is_valid',
 'point',
 'site',
--------------------------------
Edge 
 'down',
 'dual',
 'face',
 'has_source',
 'has_target',
 'is_bisector',
 'is_ray',
 'is_segment',
 'is_unbounded',
 'is_valid',
 'left',
 'next',
 'opposite',
 'previous',
 'right',
 'source',
 'target',
 'this',
 'twin',
 'up'
 
------------------
Face 
 'dual',
 'halfedge',
 'is_halfedge_on_ccb',
 'is_unbounded',
 'is_valid',
 'outer_ccb',
 
"""

def area(face):
    pass



class Face(object):
    def __init__(self, cg_face):
        self._ent = cg_face


class _Voronoi(object):
    def __init__(self, cls, points):
        self._V = cls()
        for point in points:
            self.insert(*point)

    def insert(self, *args):
        pass

    def _input_fmt(self, site):
        return site

    @property
    def inputs(self):
        return list(map(lambda site: self._input_fmt(site),
                        self._iter(self._V.sites())))

    def clipped(self):
        """ return new wrapper for bounded vor"""
        return

    @property
    def faces(self):
        return list(self._iter(self._V.bounded_faces()))

    @property
    def vertices(self):
        return list(self._iter(self._V.vertices()))

    @property
    def edges(self):
        return list(self._iter(self._V.edges()))

    @property
    def halfedges(self):
        return list(self._iter(self._V.halfedges()))

    def _iter(self, iterator):
        while iterator.hasNext():
            nxt = iterator.next()
            if not hasattr(nxt, 'is_valid'):
                yield nxt
            elif nxt.is_valid():
                yield nxt

    def _unwrap(self, cgal_ent):
        pass


class Voronoi(_Voronoi):
    def __init__(self, points):
        _Voronoi.__init__(self, vor2.Voronoi_diagram_2, points)

    def insert(self, *args):
        self._V.insert(Point_2(args[0], args[1]))

    def _input_fmt(self, site):
        return [site.x(), site.y()]


class WVoronoi(_Voronoi):
    def __init__(self, points):
        _Voronoi.__init__(self, vor2.Power_diagram_2, points)

    def _input_fmt(self, site):
        return [site.x(), site.y(), site.weight()]

    def insert(self, *args):
        if len(args) == 2:
            x, y = args
            w = 1
        elif len(args) == 3:
            x, y, w = args
        else:
            print(args)
            return
        pt = Point_2(x, y)
        self._V.insert(Weighted_point_2(pt, w))
