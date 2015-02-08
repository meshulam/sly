import IPython
from triangle import triangulate
from numpy import array
import bmesh
import shapely.affinity
from shapely.geometry import Polygon
from mathutils import Matrix
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
        hole = Polygon(ring).representative_point()
        holes.append([hole.x, hole.y])

    out = {'vertices': array(verts),
           'segments': array(segments)}
    if holes:
        out['holes'] = array(holes)
    return out

def to_bmesh(obj, solid=True):
    poly = polyfile(obj)
    p2 = triangulate(poly, 'p')

    mesh = bmesh.new()
    bverts = [mesh.verts.new((pt[0], pt[1], 0)) for pt in p2['vertices']]
    for a, b in p2['segments']:
        mesh.edges.new((bverts[a], bverts[b]))
    for a, b, c in p2['triangles']:
        mesh.faces.new((bverts[a], bverts[b], bverts[c]))
    if solid:
        mesh.transform(Matrix.Translation((0, 0, -obj.thickness / 2)))
        geom = mesh.verts[:] + mesh.edges[:] + mesh.faces[:]
        res = bmesh.ops.extrude_face_region(mesh, geom=geom)
        extruded_verts = [elem for elem in res['geom']
                          if isinstance(elem, bmesh.types.BMVert)]
        bmesh.ops.translate(mesh, verts=extruded_verts,
                            vec=(0, 0, obj.thickness))
    mesh.transform(obj.transform_3d)
    return mesh

