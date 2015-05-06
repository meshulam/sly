from mathutils import Vector
from shapely.geometry import Polygon
from sly.slicer import Slice
from sly.utils import to_2d

Z_UNIT = Vector((0, 0, 1))
# Assumptions:
#  - 1:1 slices to faces
#  - Edges form a joint
#  - Verts need to be "owned" by a single neighboring face
#  -

def to_slices(bm, thickness):
    slys = {}
    for face in bm.faces:
        co = face.calc_center_median()
        rot = Z_UNIT.rotation_difference(face.normal)  # Quaternion to rotate Z to the normal
        poly = face_to_poly(face, co, rot)
        slys[face.index] = Slice(co, rot, poly, thickness, name=str(face.index))

    for edge in bm.edges:
        if len(edge.link_faces) != 2:
            continue

        pts = [vert.co for vert in edge.verts]

        # Look up the slices from the dictionary based on the face index
        attached = [slys[face.index] for face in edge.link_faces]

        attached[0].add_joint(pts[0], pts[1], start_positive=True, width=thickness*2, length=thickness)
        attached[1].add_joint(pts[0], pts[1], start_positive=False, width=thickness*2, length=thickness)

    return slys.values()

def face_to_poly(face, co, rot):
    """Convert a bmesh face to a 2D polygon"""
    points_2d = []
    for vert in face.verts:
        pt = to_2d(vert.co, co, rot)
        points_2d.append(pt)
    return Polygon(points_2d)