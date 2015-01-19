# Slicer: Classes for 3D construction from 2D parts
#
import IPython
import numpy
import bmesh
import mathutils.geometry
from mathutils.geometry import distance_point_to_plane
from mathutils import Vector, Matrix, Quaternion
import Polygon

Z_UNIT = Vector((0, 0, 1))

# Not yet used
FACETYPE = {'REGULAR': 0,
            'INTERSECTING': 1}

class Slice(object):

    def __init__(self, coord, norm, mesh=None, thickness=0.5):
        if thickness <= 0:
            raise ValueError("Slice thickness must be positive!")

        self.normal = norm.normalized()
        self.coord = coord
        self.mesh = mesh
        self.thickness = thickness
        # index tied to the mesh to look up custom data
        self.facetype = self.mesh.faces.layers.int.new('FACETYPE')

    def solid_mesh(self):
        solid = self.mesh.copy()
        solid.transform(Matrix.Translation(-self.normal * self.thickness / 2))
        geom = solid.verts[:] + solid.edges[:] + solid.faces[:]
        res = bmesh.ops.extrude_face_region(solid, geom=geom)
        extruded_verts = [elem for elem in res['geom']
                          if isinstance(elem, bmesh.types.BMVert)]
        bmesh.ops.translate(solid, verts=extruded_verts,
                            vec=(self.normal * self.thickness))
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
            self.bisect(co, other.normal)

    def all_geometry(self):
        return self.mesh.verts[:] + self.mesh.edges[:] + self.mesh.faces[:]

    def front_coord(self):
        return self.coord + (self.normal * self.thickness / 2)

    def back_coord(self):
        return self.coord - (self.normal * self.thickness / 2)

    def is_within_thickness(self, pt):
        """Does the point lie in the thickness of this slice?"""
        d1 = distance_point_to_plane(pt, self.front_coord(), self.normal)
        d2 = distance_point_to_plane(pt, self.back_coord(), self.normal)
        return (d1 * d2) < 0    # Opposite signs

    def intersect(self, other, invert_cuts=False):
        """Cut slots into this slice and another one so they fit together."""
        cut_dir = self.normal.cross(other.normal)
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

            # clear the part of this face behind the cut_dir plane
            remove_face_behind_plane(self.mesh, face, pt, cut_dir)

            # Find intersecting faces on the other slice, since this
            # proves they were created by the bisect_solid we just performed
            for oface in other.mesh.faces:
                if self.intersects_face(oface):
                    # Clear these faces in front of the cut_dir plane
                    remove_face_behind_plane(other.mesh, oface, pt, -cut_dir)

    def intersects_face(self, face):
        initial_side = is_point_behind_plane(face.verts[0].co, self.coord, self.normal)

        for vert in face.verts:
            if initial_side != is_point_behind_plane(vert.co, self.coord, self.normal):
                return True
        return False

    def _old_to_mesh(self):
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
        self._mesh = bm
        return bm

def is_point_behind_plane(point, plane_co, plane_no):
    return distance_point_to_plane(point, plane_co, plane_no) < 0

def remove_face_behind_plane(bm, face, plane_co, plane_no):
    geom = face.verts[:] + face.edges[:] + [face]
    ret = bmesh.ops.bisect_plane(bm, geom=geom,
                                 plane_co=plane_co, plane_no=plane_no)
    for elem in ret['geom']:
        if not isinstance(elem, bmesh.types.BMFace):
            continue
        if is_point_behind_plane(elem.calc_center_bounds(), plane_co, plane_no):
            bmesh.ops.delete(bm, geom=[elem], context=5)

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


def rotated(vector, rot):
    vec_new = vector.copy()
    vec_new.rotate(rot)
    return vec_new

