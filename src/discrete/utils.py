import numpy as np
from scipy.spatial import distance


def pt_above(p, a, b):
    """Return True if a is above b relative to fixed point p"""
    return ((a[0] - p[0]) * (b[1] - p[1]) -
            (b[0] - p[0]) * (a[1] - p[1]) > 0.0)


def sort_points(corners):
    n = len(corners)
    cx = float(sum(x for x, y in corners)) / n
    cy = float(sum(y for x, y in corners)) / n

    corners_with_angles = []
    for x, y in corners:
        an = (np.arctan2(y - cy, x - cx) + 2.0 * np.pi) % (2.0 * np.pi)
        corners_with_angles.append((x, y, an))

    corners_with_angles.sort(key=lambda tup: tup[2])
    return map(lambda x: (x[0], x[1]), corners_with_angles)


def polygon_area(corners, sorted=False):
    """https://plot.ly/python/polygon-area/"""
    if sorted is False:
        corners = list(sort_points(corners))
    n = len(corners)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area


def centroid(points):
    """The geometric center point of the polygon. This point only exists
        for simple polygons. For non-simple polygons it is ``None``. Note
        in concave polygons, this point may lie outside of the polygon itself.

        If the centroid is unknown, it is calculated from the vertices and
        cached. If the polygon is known to be simple, this takes O(n) time. If
        not, then the simple polygon check is also performed, which has an
        expected complexity of O(n log n).

        Compute the centroid using by summing the centroids
         of triangles made from each edge with vertex[0] weighted
        (positively or negatively) by each triangle's area
    """
    a = points[0]
    b = points[1]
    total_area = 0.0
    centroid = np.array([0., 0.])
    for i in range(2, len(points)):
        c = points[i]
        area = ((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]))
        centroid += (a + b + c) * area
        total_area += area
        b = c
    return centroid / (3.0 * total_area)


def fill_tri(space, p1, p2, p3):
    # todo
    return space


def _line_low(x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    yi = 1
    if dy < 0:
        yi, dy = -1, -dy
    D = 2 * dy - dx
    y = y0
    marked = [[x0, y]]
    for x in range(x0, x1+1):
        marked.append([x, y])
        if D > 0:
            y += yi
            D -= 2 * dx
        D += 2 * dy
    return marked


def _line_high(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    xi = 1
    if dx < 0:
        xi = -1
        dx = -dx
    D = 2*dx - dy
    x = x0
    marked = []
    for y in range(y0, y1+1):
        marked.append([x, y])
        if D > 0:
            x = x + xi
            D = D - 2*dy
        D = D + 2*dx
    return marked


def discretize_segment(p1, p2):
    (x0, y0), (x1, y1) = p1, p2
    if abs(y1 - y0) < abs(x1 - x0):
        if x0 > x1:
            return _line_low(x1, y1, x0, y0)
        return _line_low(x0, y0, x1, y1)
    else:
        if y0 > y1:
            return _line_high(x1, y1, x0, y0)
        return _line_high(x0, y0, x1, y1)


def nearest_points(pts1, pts2):
    """ nearest [n, 2 ] [m, 2] -> [1,2]"""
    if pts1.ndim == 1:
        pts1 = pts1.reshape(1, 2)
    if pts2.ndim == 1:
        pts2 = pts2.reshape(1, 2)
    dists = distance.cdist(pts1, pts2)
    pts = np.unravel_index(np.argmin(dists, axis=None), dists.shape)
    return pts1[pts[0]], pts2[pts[1]]


def pointset_mass_distribution(points):
    cm = np.sum(points, axis=0) / len(points)
    A = np.asmatrix(np.zeros((2, 2)))
    for p in points:
        r = np.asmatrix(p - cm)
        A += r.transpose()*r
    # np.asarray(cm).reshape(2),
    return A

