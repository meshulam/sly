# Slicer: Classes for 3D construction from 2D parts
#
import math
import IPython
import numpy
import bmesh
import shapely.geometry
from shapely.geometry import Point
from sly.utils import each_shape, rotated, pairwise
import shapely.ops
import shapely.affinity
import mathutils.geometry
from mathutils.geometry import distance_point_to_plane, intersect_line_plane
from mathutils import Vector, Matrix

Z_UNIT = Vector((0, 0, 1))

class SliceSpec(object):
    def __init__(self, co, no):
        self.co = co
        self.no = no.normalized()

    def to_slices(self, bm_orig, thickness):
        bm = bm_orig.copy()
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        ret = bmesh.ops.bisect_plane(bm, geom=geom,
                                     dist=0.00001,
                                     plane_co=self.co, plane_no=self.no,
                                     use_snap_center=False,
                                     clear_outer=True, clear_inner=True)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.contextual_create(bm, geom=geom)

        rot = self.no.rotation_difference(Z_UNIT)  # Quaternion to rotate the normal to Z
        joined = mesh_to_polys(bm, rot)
        bm.free()

        xform = to_transform(self.co, self.no)
        return [Slice2D(xform, poly, thickness)
                for poly in each_shape(joined)]


def to_slices(bm, slice_specs, thickness):
    slys = []
    for co, no in slice_specs:
        spec = SliceSpec(co, no)
        slys.extend(spec.to_slices(bm, thickness))

    for sly in slys:
        for other in slys:
            if sly.same_normal(other):
                continue
            mutual_cut(sly, other)
    return slys


def mutual_cut(sly1, sly2):
    s2co, s2no = decompose_transform(sly2.transform)
    cut_dir = sly1.cut_direction(sly2)
    points = []
    for (a, b) in pairwise(sly1.exterior.coords):
        pta = Vector((a[0], a[1], 0)) * sly1.transform
        ptb = Vector((b[0], b[1], 0)) * sly1.transform

        intersect = intersect_line_plane(pta, ptb, s2co, s2no)
        if intersect:
            points.append(intersect)

    if len(points) > 2:
        print("More than one intersection between slices. Not yet supported!")
    elif len(points) == 0:
        print("No intersection found")
    elif len(points) == 1:
        print("Wtf? one intersection?")
    else:
        midpt = points[0].lerp(points[1], 0.5)
        sly1.add_cut(midpt, cut_dir, sly2.thickness)
        sly2.add_cut(midpt, -cut_dir, sly1.thickness)


class Slice(object):

    def __init__(self, co, no, mesh=None, thickness=0.5):
        raise ValueError("Slice class should be dead code now")
        if thickness <= 0:
            raise ValueError("Slice thickness must be positive!")

        self.no = no.normalized()
        self.co = co
        self.mesh = mesh
        self.thickness = thickness
        self.cuts = []

    def copy(self):
        return Slice(self.co.copy(), self.no.copy(),
                     self.mesh.copy(), self.thickness)

    def free(self):
        self.mesh.free()

    @classmethod
    def create(cls, mesh, origin, normal, thickness):
        geom = mesh.verts[:] + mesh.edges[:] + mesh.faces[:]
        ret = bmesh.ops.bisect_plane(mesh, geom=geom,
                                     dist=0.0001,
                                     plane_co=origin, plane_no=normal,
                                     use_snap_center=False,
                                     clear_outer=True, clear_inner=True)
        geom = mesh.verts[:] + mesh.edges[:] + mesh.faces[:]
        bmesh.ops.contextual_create(mesh, geom=geom)

        return cls(origin, normal, mesh, thickness=thickness)

    def bisect(self, co, no, clear=False):
        res = bmesh.ops.bisect_plane(self.mesh, geom=self.all_geometry(),
                                     dist=0.0001,
                                     plane_co=co, plane_no=no,
                                     clear_outer=clear, clear_inner=clear)
        edges = []
        for elem in res['geom_cut']:
            if isinstance(elem, bmesh.types.BMEdge):
                edges.append(elem)
        return edges

    def all_geometry(self):
        return self.mesh.verts[:] + self.mesh.edges[:] + self.mesh.faces[:]

    def mutual_cut(self, other, invert=False):
        cut_dir = self.no.cross(other.no)
        if invert:
            cut_dir = -cut_dir

        temp = self.copy()
        temp.bisect(other.co, other.no, clear=True)
        midpt_verts = [vert for vert in temp.mesh.verts
                       if len(vert.link_edges) > 1]
        bmesh.ops.dissolve_verts(temp.mesh, verts=midpt_verts)

        #for edge in temp.mesh.edges:
        #    midpt = edge.verts[0].co.lerp(edge.verts[1].co, 0.5)
        #    self.cuts.append(Cut(midpt, cut_dir, other.thickness))
        #    other.cuts.append(Cut(midpt, -cut_dir, self.thickness))
        temp.free()


class Cut2D(object):
    cut_dist = 1000     # Arbitrarily long cut

    def __init__(self, point, direction, thickness):
        self.point = point
        self.direction = direction
        self.thickness = thickness

    def polygon(self, fillet_radius=0):
        offset = self.direction.orthogonal() * self.thickness / 2

        p2 = self.point + self.direction * self.cut_dist
        p1 = self.point

        pts = [p1 - offset, p1 + offset,
               p2 + offset, p2 - offset]
        simple = shapely.geometry.Polygon(pts)

        if fillet_radius <= 0:
            return simple

        if fillet_radius > self.thickness / 4:  # T-bone
            w_inset = 0
            h_inset = fillet_radius
        else:   # Dogbone
            w_inset = fillet_radius / math.sqrt(2)
            h_inset = fillet_radius / math.sqrt(2)
        h0 = self.point + self.direction * h_inset
        hole_w_offset = self.direction.orthogonal() * (self.thickness / 2 - w_inset)
        shapes = [Point(h0 + hole_w_offset).buffer(fillet_radius),
                  Point(h0 - hole_w_offset).buffer(fillet_radius),
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

def to_transform(co, no):
    rot = Z_UNIT.rotation_difference(no)  # Rotation from z to normal
    xform = rot.to_matrix().to_4x4()
    xform.translation = co.project(no)
    return xform

def decompose_transform(xform):
    co = xform.translation
    no = rotated(Z_UNIT, xform)
    return (co, no)


class Slice2D(object):
    def __init__(self, transform, poly, thickness):
        self.transform = transform
        self.page_position = PagePosition()
        self.poly = poly
        self.thickness = thickness
        self.cuts = []

    def normal(self):
        _, no = decompose_transform(self.transform)
        return no

    def same_normal(self, other):
        return self.normal() == other.normal()

    def move(self, dx, dy):
        self.page_position.xoff += dx
        self.page_position.yoff += dy

    def cut_direction(self, other):
        return self.normal().cross(other.normal())

    def add_cut(self, pt3d, dir3d, thickness):
        p2 = pt3d * self.transform.inverted()
        p2.resize_2d()
        d2 = dir3d * self.transform.inverted()
        d2.resize_2d()
        d2.normalize()
        self.cuts.append(Cut2D(p2, d2, thickness))

    def get_cut_shape(self, cut, fillet_radius=0):
        ref_pt = shapely.geometry.Point(cut.point.x, cut.point.y)
        negative = cut.polygon(fillet_radius=fillet_radius)
        cutout = self.poly.intersection(negative)
        for poly in each_shape(cutout):
            if not poly.intersects(ref_pt):
                continue
            return poly

    def positioned(self):
        return shapely.affinity.affine_transform(self.poly,
                                                 self.page_position.to_matrix())

    @staticmethod
    def is_valid(obj):
        return hasattr(obj, 'poly') and hasattr(obj.poly, 'exterior')

    @staticmethod
    def from_3d(slice3d):
        raise ValueError("dead code")
        rot = slice3d.no.rotation_difference(Z_UNIT)  # Quaternion to rotate the normal to Z

        joined = mesh_to_polys(slice3d.mesh, rot)

        xform = to_transform(slice3d.co, slice3d.no)

        outs = [Slice2D(xform, poly, slice3d.thickness)
                for poly in each_shape(joined)]

        for cut in slice3d.cuts:
            p2 = rotated(cut.point, rot)
            p2.resize_2d()
            d2 = rotated(cut.direction, rot)
            d2.resize_2d()
            d2.normalize()
            for sli2d in outs:
                sli2d.cuts.append(Cut2D(p2, d2, cut.thickness))
        return outs

def mesh_to_polys(bm, rotation):
    polys = []
    for face in bm.faces:
        poly = face_to_poly(face, rotation)
        if poly.is_valid:
            polys.append(poly)
        else:
            print("Invalid polygon, ignoring")
    return shapely.ops.unary_union(polys)

def face_to_poly(face, rotation):
    """Convert a bmesh face to a flat polygon"""
    points_2d = []
    for vert in face.verts:
        (x, y, z) = rotated(vert.co, rotation)
        points_2d.append((x, y))
    return shapely.geometry.Polygon(points_2d)
