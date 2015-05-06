import itertools
import math
import bmesh
import shapely.geometry
import shapely.ops
from mathutils import Vector, Matrix

import sly.utils
from sly.features import Cut, Joint

"""The main module in Sly."""


Z_UNIT = Vector((0, 0, 1))


def to_slices(bm, slice_defs, thickness, cut_specs=[], fillet_radius=0):
    slys = []
    for i, sdef in enumerate(slice_defs):
        if not sdef.name:
            sdef.name = str(i)
        sdef.thickness = thickness
        sdef.fillet = fillet_radius
        slys.extend(sdef.generate_slices(bm))

    for s1, s2 in itertools.combinations(slys, r=2):
        spec = {}
        for specline in cut_specs:
            if s1.name in specline['intersect'] and \
                    s2.name in specline['intersect']:
                spec = specline
        sly.ops.mutual_cut(s1, s2, cut_spec=spec)
    return slys


class SliceDef(object):
    def __init__(self, co, no, name="", z_index=0):
        if not hasattr(co, 'length'):   # Support raw tuples or Vector objs
            co = Vector(co)
        if not hasattr(no, 'length'):
            no = Vector(no)
        self.co = co
        self.no = no
        self.thickness = 0.5    # Default should be overridden in to_slices
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
                        name=self.identify(i), fillet=self.fillet)

    def identify(self, sub_id=0):
        return "{}.{}".format(self.name, sub_id)


class Slice(object):
    """A 2D shape oriented in 3D space. The core object in the Sly library."""

    def __init__(self, co, rot, poly, thickness, z_index=0, name="", fillet=0):
        self.co = co
        self.rot = rot
        self.poly = poly
        self.thickness = thickness
        self.cuts = []
        self.joints = []
        self.z_index = z_index
        self.name = name
        self.fillet = fillet

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

    def add_joint(self, start3d, end3d, *args, **kwargs):
        start2d = self.to_2d(start3d)
        end2d = self.to_2d(end3d)
        self.joints.append(Joint(start2d, end2d, *args, **kwargs))

    def get_cut_shape(self, cut):
        ref = shapely.geometry.Point(cut.point.x, cut.point.y) \
                              .buffer(self.thickness / 2)
        negative = cut.polygon(fillet=self.fillet)
        cutout = self.poly.buffer(self.thickness).intersection(negative)
        for poly in sly.utils.each_shape(cutout):
            if not poly.intersects(ref):
                continue
            return poly

    @staticmethod
    def is_valid(obj):
        return hasattr(obj, 'poly') and hasattr(obj.poly, 'exterior')


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
