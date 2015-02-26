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


def to_slices(bm, slice_defs, thickness=None):
    slys = []
    for i, sdef in enumerate(slice_defs):
        if not sdef.name:
            sdef.name = str(i)
        if thickness:
            sdef.thickness = thickness
        slys.extend(sdef.generate_slices(bm))

    for s1, s2 in itertools.combinations(slys, r=2):
        sly.ops.mutual_cut(s1, s2)
    return slys


class SliceDef(object):
    def __init__(self, co, no, thickness=0.5, name="", z_index=0):
        if not hasattr(co, 'length'):   # Support raw tuples or Vector objs
            co = Vector(co)
        if not hasattr(no, 'length'):
            no = Vector(no)
        self.co = co
        self.no = no
        self.thickness = thickness
        self.name = name
        self.z_index = z_index

    def generate_slices(self, bm_orig):
        bm = bm_orig.copy()
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        ret = bmesh.ops.bisect_plane(bm, geom=geom,
                                     dist=0.00001,
                                     plane_co=self.co, plane_no=self.no,
                                     use_snap_center=False,
                                     clear_outer=True, clear_inner=True)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.contextual_create(bm, geom=geom)

        rot = Z_UNIT.rotation_difference(self.no)  # Quaternion to rotate Z to the normal
        joined = mesh_to_polys(bm, self.co, rot)
        bm.free()

        for i, poly in enumerate(sly.utils.each_shape(joined)):
            yield Slice(self.co, rot, poly,
                        self.thickness, z_index=self.z_index,
                        name=self.identify(i))

    def identify(self, sub_id=0):
        return "{}.{}".format(self.name, sub_id)


class Slice(object):
    def __init__(self, co, rot, poly, thickness, z_index=0, name=""):
        self.co = co
        self.rot = rot
        self.poly = poly
        self.thickness = thickness
        self.cuts = []
        self.z_index = z_index
        self.name = name
        self.fillet = 0

    def to_2d(self, vec, translate=True):
        co = self.co if translate else None
        return sly.utils.to_2d(vec, co, self.rot)

    def to_3d(self, vec, translate=True):
        co = self.co if translate else None
        return sly.utils.to_3d(vec, co, self.rot)

    def normal(self):
        return sly.utils.rotated(Z_UNIT, self.rot)

    def cut_direction(self, other):
        direc = self.normal().cross(other.normal())

        if (direc.z > 0 and self.z_index > other.z_index) \
                or (direc.z < 0 and self.z_index < other.z_index):
            direc = -direc

        return direc

    def add_cut(self, pt3d, dir3d, thickness):
        p2 = self.to_2d(pt3d)
        d2 = self.to_2d(dir3d, translate=False)
        d2.normalize()
        self.cuts.append(Cut(p2, d2, thickness))

    def get_cut_shape(self, cut):
        ref = shapely.geometry.Point(cut.point.x, cut.point.y) \
                              .buffer(self.thickness / 2)
        negative = cut.polygon(fillet=self.fillet)
        cutout = self.poly.intersection(negative)
        for poly in sly.utils.each_shape(cutout):
            if not poly.intersects(ref):
                continue
            return poly

    @staticmethod
    def is_valid(obj):
        return hasattr(obj, 'poly') and hasattr(obj.poly, 'exterior')


class Cut(object):
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

        if fillet > self.thickness * 0.4:  # T-bone
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
