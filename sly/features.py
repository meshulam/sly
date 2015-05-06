import shapely.ops

from shapely.geometry import Point, Polygon
from shapely.affinity import rotate, translate
from shapely.ops import cascaded_union
from mathutils import Vector
from math import sqrt

class Joint(object):
    def __init__(self, start_point, end_point, start_positive, width, length):
        self.start_pt = start_point
        self.distance = (start_point - end_point).length
        self.angle = (end_point - start_point).angle_signed(Vector((1.0, 0.0)))
        self.start_positive = start_positive
        self.width = width
        self.length = length

    def polygons(self, positive=True):
        polys = []

        start = Vector((0, 0))
        if self.start_positive is not positive:  # offset by one width
            start.x += self.width

        len_adj = self.length / 2

        while start.x + self.width < self.distance:
            pts = [(start.x, start.y - len_adj),
                   (start.x, start.y + len_adj),
                   (start.x + self.width, start.y + len_adj),
                   (start.x + self.width, start.y - len_adj)]
            polys.append(Polygon(pts))
            start.x += self.width * 2

        poly = cascaded_union(polys)
        poly = rotate(poly, self.angle, origin=(0, 0), use_radians=True)
        poly = translate(poly, self.start_pt[0], self.start_pt[1])
        return poly


class Cut(object):
    """A cutout from a slice. Perpendicular slices fit together by sliding
    their cuts into each other"""
    cut_dist = 1000     # Arbitrarily long cut

    def __init__(self, point, direction, thickness):
        self.point = point
        self.direction = direction
        self.thickness = thickness

    def polygon(self, fillet=0):
        offset = self.direction.orthogonal() * self.thickness / 2

        p2 = self.point + self.direction * self.cut_dist
        p1 = self.point

        pts = [p1 - offset, p1 + offset,
               p2 + offset, p2 - offset]
        simple = Polygon(pts)

        if fillet <= 0:
            return simple

        if fillet > self.thickness * 0.4:  # T-bone
            w_inset = 0
            h_inset = fillet
        else:   # Dogbone
            w_inset = fillet / sqrt(2)
            h_inset = fillet / sqrt(2)
        h0 = self.point + self.direction * h_inset
        hole_w_off = self.direction.orthogonal() * (self.thickness / 2 - w_inset)
        shapes = [Point(h0 + hole_w_off).buffer(fillet),
                  Point(h0 - hole_w_off).buffer(fillet),
                  simple]
        return shapely.ops.unary_union(shapes)

    def overlap_poly(self):
        offset = self.direction.orthogonal() * self.thickness / 2

        p2 = self.point + self.direction * self.cut_dist
        p1 = self.point - self.direction * self.cut_dist

        pts = [p1 - offset, p1 + offset,
               p2 + offset, p2 - offset]
        return shapely.geometry.Polygon(pts)