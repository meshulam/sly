# Slicer: Classes for 3D construction from 2D parts
#
import math
import IPython
import numpy
import bmesh
import shapely.geometry
import shapely.ops
import shapely.affinity
import mathutils.geometry
from mathutils.geometry import distance_point_to_plane
from mathutils import Vector, Matrix

Z_UNIT = Vector((0, 0, 1))

class Slice(object):

    def __init__(self, co, no, mesh=None, thickness=0.5):
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
        edges = temp.bisect(other.co, other.no)

        # Points that lie on the line we just created
        points = [edge.verts[i].co for edge in edges for i in [0, 1]]
        if len(points) > 1:
            (p1, p2) = point_minmax(points, cut_dir)
            midpt = p1.lerp(p2, 0.5)
            self.cuts.append(Cut(midpt, cut_dir, other.thickness))
            other.cuts.append(Cut(midpt, -cut_dir, self.thickness))
        temp.free()


class Cut(object):
    def __init__(self, point, direction, thickness):
        self.point = point
        self.direction = direction
        self.thickness = thickness

class Cut2D(Cut):
    def polygon(self, whole_face=False):
        cut_dist = 1000     # Arbitrarily long cut
        offset = self.direction.orthogonal() * self.thickness / 2

        p2 = self.point + self.direction * cut_dist
        p1 = self.point

        if whole_face:
            p1 = p1 - self.direction * cut_dist

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


class Slice2D(object):
    def __init__(self, xform, poly, thickness):
        self.transform_3d = xform
        self.page_position = PagePosition()
        self.poly = poly
        self.thickness = thickness
        self.cuts = []

    def move(self, dx, dy):
        self.page_position.xoff += dx
        self.page_position.yoff += dy

    def get_cut_shape(self, cut):
        ref_pt = shapely.geometry.Point(cut.point.x, cut.point.y)
        negative = cut.polygon()
        cutout = self.poly.intersection(negative)
        for poly in each_polygon(cutout):
            if not poly.intersects(ref_pt):
                continue
            return poly

    def positioned(self):
        return shapely.affinity.affine_transform(self.poly,
                                                 self.page_position.to_matrix())

    @staticmethod
    def is_valid(obj):
        return hasattr(obj, 'poly') and \
                hasattr(obj.poly, 'exterior')

    @staticmethod
    def from_3d(slice3d):
        rot = slice3d.no.rotation_difference(Z_UNIT)  # Quaternion to rotate the normal to Z

        def _to_poly(face):
            points_2d = []
            for vert in face.verts:
                (x, y, z) = rotated(vert.co, rot)
                points_2d.append((x, y))
            return shapely.geometry.Polygon(points_2d)
        polys = []
        for face in slice3d.mesh.faces:
            facepoly = _to_poly(face)
            if facepoly.is_valid:
                polys.append(facepoly)
            else:
                print("Invalid polygon, ignoring")
        try:
            joined = shapely.ops.unary_union(polys)
        except ValueError:
            print("Error doing unary union. falling back to linear")
            joined = polys[0]
            for p in polys[1:]:
                joined = joined.union(p)

        xform = rot.conjugated().to_matrix().to_4x4()
        #xform.translation = Z_UNIT * rotated(slice3d.co, rot).z  # TODO: should be negative?
        xform.translation = -slice3d.co

        outs = [Slice2D(xform, poly, slice3d.thickness)
                for poly in each_polygon(joined)]

        for cut in slice3d.cuts:
            p2 = rotated(cut.point, rot)
            p2.resize_2d()
            d2 = rotated(cut.direction, rot)
            d2.resize_2d()
            d2.normalize()
            for sli2d in outs:
                sli2d.cuts.append(Cut2D(p2, d2, cut.thickness))
        return outs

def each_polygon(geom):
    if hasattr(geom, 'geoms'):
        return geom
    else:
        return [geom]

def biggest_polygon(polys):
    if not hasattr(polys, 'geoms'):
        return polys

    biggest = max(polys, key=lambda p: p.area)
    print("Biggest poly: {} total {} ({})"
          .format(biggest.area, polys.area, len(polys)))
    return biggest

def point_minmax(points, direction):
    """Returns the two points out of the given iterable
    that represent the range when projected in the given direction"""
    p1 = points[0]
    p2 = p1
    for point in points:
        if direction.dot(point - p1) < 0:
            p1 = point
        elif direction.dot(point - p2) > 0:
            p2 = point
    return (p1, p2)

def rotated(vector, rot):
    vec_new = vector.copy()
    vec_new.rotate(rot)
    return vec_new

