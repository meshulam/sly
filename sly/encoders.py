import IPython
from triangle import triangulate
from numpy import array
import bmesh
from sly.slicer import Slice2D

def polyfile(slic):
    if not Slice2D.is_valid(slic):
        raise ValueError("Slice is not valid!")

    verts = []
    segments = []
    holes = []

    for ring in [slic.poly.exterior] + slic.poly.interiors[:]:
        start = len(verts)
        for coord in ring.coords[:-1]:
            new_ind = len(verts)
            verts.append(list(coord))
            segments.append([new_ind, new_ind + 1])
        segments[-1][1] = start     # Close the loop

    for ring in slic.poly.interiors:
        pt = ring.representative_point()
        holes.append([pt.x, pt.y])

    out = {'vertices': array(verts),
           'segments': array(segments)}
    if holes:
        out['holes'] = array(holes)
    return out

def to_bmesh(obj):
    poly = polyfile(obj)
    poly = triangulate(poly, 'pq20D')
    #IPython.embed()

    mesh = bmesh.new()

    bverts = [mesh.verts.new((pt[0], pt[1], 0)) for pt in poly['vertices']]
    for a, b in poly['segments']:
        mesh.edges.new((bverts[a], bverts[b]))

    # TODO: add faces
    mesh.transform(obj.transform_3d)
    return mesh



#    def solid_mesh(self):
#        solid = self.mesh.copy()
#        solid.transform(Matrix.Translation(-self.no * self.thickness / 2))
#        geom = solid.verts[:] + solid.edges[:] + solid.faces[:]
##        res = bmesh.ops.extrude_face_region(solid, geom=geom)
#        extruded_verts = [elem for elem in res['geom']
#                          if isinstance(elem, bmesh.types.BMVert)]
#        bmesh.ops.translate(solid, verts=extruded_verts,
#                            vec=(self.no * self.thickness))
#        return solid
