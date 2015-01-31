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

    def solid_mesh(self):
        solid = self.mesh.copy()
        solid.transform(Matrix.Translation(-self.no * self.thickness / 2))
        geom = solid.verts[:] + solid.edges[:] + solid.faces[:]
        res = bmesh.ops.extrude_face_region(solid, geom=geom)
        extruded_verts = [elem for elem in res['geom']
                          if isinstance(elem, bmesh.types.BMVert)]
        bmesh.ops.translate(solid, verts=extruded_verts,
                            vec=(self.no * self.thickness))
        return solid

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

    def bisect_solid(self, other):
        for co in [other.front_coord(), other.back_coord()]:
            self.bisect(co, other.no)

    def all_geometry(self):
        return self.mesh.verts[:] + self.mesh.edges[:] + self.mesh.faces[:]

    def front_coord(self):
        return self.co + (self.no * self.thickness / 2)

    def back_coord(self):
        return self.co - (self.no * self.thickness / 2)

    def is_within_thickness(self, pt):
        """Does the point lie in the thickness of this slice?"""
        d1 = distance_point_to_plane(pt, self.front_coord(), self.no)
        d2 = distance_point_to_plane(pt, self.back_coord(), self.no)
        return (d1 * d2) < 0    # Opposite signs

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

    def intersect(self, other, invert_cuts=False):
        """Cut slots into this slice and another one so they fit together."""
        cut_dir = self.no.cross(other.no)
        if invert_cuts:
            cut_dir = -cut_dir

        self.bisect_solid(other)
        other.bisect_solid(self)

        self_faces = self.mesh.faces[:]     # make a copy since we're mutating stuff

        for face in self_faces:
            if not face.is_valid:
                continue

            # The point that defines the halfway point where the two cuts meet
            pt = face.calc_center_bounds()
            if not other.is_within_thickness(pt):
                continue         # this isn't a face formed by the bisect_solid

            for oface in other.mesh.faces:
                if bounding_boxes_intersect(face, oface):
                    # For corresponding faces on other, remove parts behind the cut_dir plane
                    remove_face_behind_plane(other.mesh, oface, pt, -cut_dir)

            # clear the part of this face behind the cut_dir plane
            remove_face_behind_plane(self.mesh, face, pt, cut_dir)

class Cut(object):
    def __init__(self, point, direction, thickness):
        self.point = point
        self.direction = direction
        self.thickness = thickness

class Cut2D(Cut):
    def polygon(self):
        cut_dist = 1000     # Arbitrarily long cut
        offset = self.direction.orthogonal() * self.thickness / 2
        p2 = self.point + self.direction * cut_dist
        pts = [self.point - offset, self.point + offset,
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
        self.page_position = PagePosition(10, 15, 45)
        self.poly = poly
        self.thickness = thickness
        self.cuts = []

    def apply_cuts(self):
        cut_shapes = [self.get_cut_shape(cut) for cut in self.cuts]
        cuts = shapely.ops.cascaded_union(cut_shapes)
        out = self.poly.difference(cuts)
        if hasattr(out, 'geoms'):
            print("WARNING: cut produced disconnected shapes!")
        self.poly = out

    def get_cut_shape(self, cut):
        ref_pt = shapely.geometry.Point(cut.point.x, cut.point.y)
        negative = cut.polygon()
        cutout = self.poly.intersection(negative)
        if hasattr(cutout, 'geoms'):
            for poly in cutout.geoms:
                if not poly.intersects(ref_pt):
                    continue
                return poly
        else:
            return cutout

    def positioned(self):
        return shapely.affinity.affine_transform(self.poly,
                                                 self.page_position.to_matrix())

    @staticmethod
    def from_3d(slice3d):
        rot = slice3d.no.rotation_difference(Z_UNIT)  # Quaternion to rotate the normal to Z

        def _to_poly(face):
            points_2d = []
            for vert in face.verts:
                (x, y, z) = rotated(vert.co, rot)
                points_2d.append((x, y))
            return shapely.geometry.Polygon(points_2d)
            # TODO: error checking when projecting to 2d
        polys = [_to_poly(face) for face in slice3d.mesh.faces]
        joined = shapely.ops.cascaded_union(polys)
        xform = rot.conjugated().to_matrix().to_4x4()
        xform.translation = Z_UNIT * rotated(slice3d.co, rot).z  # TODO: should be negative?

        sli2d = Slice2D(xform, joined, slice3d.thickness)
        for cut in slice3d.cuts:
            p2 = rotated(cut.point, rot)
            p2.resize_2d()
            d2 = rotated(cut.direction, rot)
            d2.resize_2d()
            d2.normalize()
            sli2d.cuts.append(Cut2D(p2, d2, cut.thickness))
        return sli2d

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


def bounding_boxes_intersect(face1, face2):
    min1 = numpy.amin([vert.co for vert in face1.verts], axis=0)
    max1 = numpy.amax([vert.co for vert in face1.verts], axis=0)
    min2 = numpy.amin([vert.co for vert in face2.verts], axis=0)
    max2 = numpy.amax([vert.co for vert in face2.verts], axis=0)
    return numpy.all(numpy.greater(max1, min2)) \
        and numpy.all(numpy.greater(max2, min1))

def is_point_behind_plane(point, plane_co, plane_no):
    return distance_point_to_plane(point, plane_co, plane_no) < 0

def remove_face_behind_plane(bm, face, plane_co, plane_no):
    geom = face.verts[:] + face.edges[:] + [face]
    ret = bmesh.ops.bisect_plane(bm, geom=geom,
                                 plane_co=plane_co, plane_no=plane_no)
    newface = None
    for elem in ret['geom']:
        if not isinstance(elem, bmesh.types.BMFace):
            continue
        if is_point_behind_plane(elem.calc_center_bounds(), plane_co, plane_no):
            bmesh.ops.delete(bm, geom=[elem], context=5)
        else:
            newface = elem
    return newface

def is_positive(vector):
    """For any two nonzero vectors X and -X, guaranteed to return true for
    exactly one of them"""
    for elem in vector:
        if elem > 0:
            return True
        elif elem < 0:
            return False
    return False  # Only gets here for zero vectors

def rotated(vector, rot):
    vec_new = vector.copy()
    vec_new.rotate(rot)
    return vec_new

