# Slicer: Classes for 3D construction from 2D parts
#
import IPython
import numpy
import bmesh
from mathutils import Vector, Matrix, Quaternion
import Polygon

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
            print("Transformed {} to {}".format(vector, (x, y, z)))
            points_2d.append((x, y))
            zs.append(z)

        min_z = numpy.amin(zs)
        max_z = numpy.amax(zs)
        mean_z = numpy.mean(zs)

        print("Z min: {}, mean: {}, max: {}".format(min_z, mean_z, max_z))
        xform = rot.conjugated().to_matrix().to_4x4()
        xform.translation = Vector((0, 0, mean_z))
        print("Normal:", normal)
        print("Matrix:", xform)
        # TODO: check for polygons that don't lie on the given normal
        poly = Polygon.Polygon(points_2d)
        return Slice(xform, poly)

    def to_mesh(self):
        """returns a bmesh object corresponding to this slice in 3-space"""
        strips = self.polygon.triStrip()
        bm = bmesh.new()
        vertex_cache = {}
        for strip in strips:
            for tri in tristrip_to_tris(strip):
                face_verts = []
                for point in tri:
                    vertex = vertex_cache.setdefault(point,
                                bm.verts.new((point[0], point[1], 0.0)))
                    face_verts.append(vertex)
                face = bm.faces.new(face_verts)
                if not is_positive(face.normal):
                    face.normal_flip()
        bm.transform(self.transformation)
        return bm

def is_positive(vector):
    """For any two nonzero vectors X and -X, guaranteed to return true for
    exactly one of them"""
    for elem in vector:
        if elem > 0:
            return True
        elif elem < 0:
            return False
    return False  # Only gets here for zero vectors

def tristrip_to_tris(points):
    for i in range(len(points) - 2):
        yield points[i:i + 3]

def outline_polygon(poly, dist):
    #border = LinearRing(poly.boundary)
    #inner = Polygon(border.parallel_offset(dist, 'left'))
    #return poly.difference(inner)
    pass


def rotated(vector, rot):
    vec_new = vector.copy()
    vec_new.rotate(rot)
    return vec_new

