# Slicer: Classes for 3D construction from 2D parts
#
import IPython
import numpy
import bmesh
from mathutils import Vector, Matrix, Quaternion
from shapely.geometry import Point as Point2D, Polygon, LinearRing
import shapely.geometry.polygon
import shapely.ops

Z_UNIT = Vector((0, 0, 1))

class Slice(object):

    def __init__(self, mat, poly=None):
        self.transformation = mat
        self.polygon = poly

    @staticmethod
    def from_3d_points(points, normal):
        norm = normal.normalized()
        rot = norm.rotation_difference(Z_UNIT)  # Quaternion to rotate the normal to Z
        points_2d = []
        zs = []

        for vector in points:
            (x, y, z) = rotated(vector, rot)
            points_2d.append((x, y))
            zs.append(z)

        min_z = numpy.amin(zs)
        max_z = numpy.amax(zs)
        mean_z = numpy.mean(zs)

        print("Z min: {}, mean: {}, max: {}".format(min_z, mean_z, max_z))
        xform = rot.conjugated().to_matrix().to_4x4()
        xform.translation = Vector((0, 0, mean_z))
        # TODO: check for polygons that don't lie on the given normal
        poly = Polygon(points_2d)
        poly = shapely.geometry.polygon.orient(poly)
        return Slice(xform, poly)

    def to_mesh(self):
        """returns a bmesh object corresponding to this slice in 3-space"""
        tris = shapely.ops.triangulate(self.polygon)
        bm = bmesh.new()
        vertex_cache = {}
        for tri in tris:
            bound = tri.exterior
            face_verts = []
            for coord in bound.coords:
                vertex = vertex_cache.setdefault(coord,
                            bm.verts.new((coord[0], coord[1], 0.0)))
                if vertex not in face_verts:
                    face_verts.append(vertex)
            bm.faces.new(face_verts)
        bm.transform(self.transformation)
        return bm


def outline_polygon(poly, dist):
    border = LinearRing(poly.boundary)
    inner = Polygon(border.parallel_offset(dist, 'left'))
    return poly.difference(inner)

# In shapely:
# face.boundary, make sure oriented ccw,
# parallel_offset left for inner, right for outer


def rotated(vector, rot):
    vec_new = vector.copy()
    vec_new.rotate(rot)
    return vec_new

