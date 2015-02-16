# Slicer: Classes for 3D construction from 2D parts
#
import itertools
import math
import IPython
import numpy
import bmesh
import shapely.geometry
import sly.utils
import shapely.ops
import shapely.affinity
import mathutils.geometry
from mathutils import Vector, Matrix

Z_UNIT = Vector((0, 0, 1))

def to_slices(bm, slice_specs, thickness):
    slys = []
    for co, no in slice_specs:
        slys.extend(generate_slice(bm, co, no, thickness))

    for s1, s2 in itertools.combinations(slys, r=2):
        sly.ops.mutual_cut(s1, s2)
    return slys

def generate_slice(bm_orig, co, no, thickness):
    bm = bm_orig.copy()
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    ret = bmesh.ops.bisect_plane(bm, geom=geom,
                                 dist=0.00001,
                                 plane_co=co, plane_no=no,
                                 use_snap_center=False,
                                 clear_outer=True, clear_inner=True)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.contextual_create(bm, geom=geom)

    rot = no.rotation_difference(Z_UNIT)  # Quaternion to rotate the normal to Z
    joined = mesh_to_polys(bm, co, rot)
    bm.free()

    return [Slice(co, rot, poly, thickness)
            for poly in sly.utils.each_shape(joined)]


class Slice(object):
    def __init__(self, co, rot, poly, thickness):
        self.co = co
        self.rot = rot
        self.page_position = PagePosition()
        self.poly = poly
        self.thickness = thickness
        self.cuts = []

    def to_2d(self, vec, translate=True):
        co = self.co if translate else None
        return sly.utils.to_2d(vec, co, self.rot)

    def to_3d(self, vec, translate=True):
        co = self.co if translate else None
        return sly.utils.to_3d(vec, co, self.rot)

    def normal(self):
        return sly.utils.rotated(Z_UNIT, self.rot)

    def move(self, dx, dy):
        self.page_position.xoff += dx
        self.page_position.yoff += dy

    def cut_direction(self, other):
        return self.normal().cross(other.normal())

    def add_cut(self, pt3d, dir3d, thickness):
        p2 = self.to_2d(pt3d)
        d2 = self.to_2d(dir3d, translate=False)
        d2.normalize()
        self.cuts.append(Cut2D(p2, d2, thickness))

    def get_cut_shape(self, cut, fillet=0):
        ref_pt = shapely.geometry.Point(cut.point.x, cut.point.y)
        negative = cut.polygon(fillet=fillet)
        cutout = self.poly.intersection(negative)
        for poly in sly.utils.each_shape(cutout):
            if not poly.intersects(ref_pt):
                continue
            return poly

    def positioned(self):
        return shapely.affinity.affine_transform(self.poly,
                                                 self.page_position.to_matrix())

    @staticmethod
    def is_valid(obj):
        return hasattr(obj, 'poly') and hasattr(obj.poly, 'exterior')


class Cut2D(object):
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
        simple = shapely.geometry.Polygon(pts)

        if fillet <= 0:
            return simple

        if fillet > self.thickness / 4:  # T-bone
            w_inset = 0
            h_inset = fillet
        else:   # Dogbone
            w_inset = fillet / math.sqrt(2)
            h_inset = fillet / math.sqrt(2)
        h0 = self.point + self.direction * h_inset
        hole_w_off = self.direction.orthogonal() * (self.thickness / 2 - w_inset)
        shapes = [shapely.geometry.Point(h0 + hole_w_off).buffer(fillet),
                  shapely.geometry.Point(h0 - hole_w_off).buffer(fillet),
                  simple]
        return shapely.ops.unary_union(shapes)

    def overlap_poly(self):
        offset = self.direction.orthogonal() * self.thickness / 2

        p2 = self.point + self.direction * self.cut_dist
        p1 = self.point - self.direction * self.cut_dist

        pts = [p1 - offset, p1 + offset,
               p2 + offset, p2 - offset]
        return shapely.geometry.Polygon(pts)


class PagePosition(object):
    def __init__(self, xoff=0, yoff=0, rot_deg=0):
        self.xoff = xoff
        self.yoff = yoff
        self.rotation = math.radians(rot_deg)

    def to_matrix(self):
        return (math.cos(self.rotation), -math.sin(self.rotation),
                math.sin(self.rotation), math.cos(self.rotation),
                self.xoff, self.yoff)


def mesh_to_polys(bm, co, rot):
    """Convert all faces in a bmesh to a shapely polygon or MultiPolygon.
    Faces are assmued to all be coplanar with the given co and rot."""
    polys = []
    for face in bm.faces:
        poly = face_to_poly(face, co, rot)
        if poly.is_valid:
            polys.append(poly)
        else:
            print("Invalid polygon, ignoring")
    return shapely.ops.unary_union(polys)

def face_to_poly(face, co, rot):
    """Convert a bmesh face to a 2D polygon"""
    points_2d = []
    for vert in face.verts:
        pt = sly.utils.to_2d(vert.co, co, rot)
        points_2d.append(pt)
    return shapely.geometry.Polygon(points_2d)
