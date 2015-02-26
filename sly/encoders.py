import IPython
from triangle import triangulate
from numpy import array
import bmesh
import shapely.affinity
from shapely.geometry import Polygon
from mathutils import Matrix
from sly.slicer import Slice
from sly.ops import cut_poly

def polyfile(slic):
    if Slice.is_valid(slic):
        poly = slic.poly
    else:
        poly = slic     # OK to just pass in Polygon obj

    verts = []
    segments = []
    holes = []

    for ring in [poly.exterior] + poly.interiors[:]:
        start = len(verts)
        for coord in ring.coords[:-1]:
            new_ind = len(verts)
            verts.append(list(coord))
            segments.append([new_ind, new_ind + 1])
        segments[-1][1] = start     # Close the loop

    for ring in poly.interiors:
        hole = Polygon(ring).representative_point()
        holes.append([hole.x, hole.y])

    out = {'vertices': array(verts),
           'segments': array(segments)}
    if holes:
        out['holes'] = array(holes)
    return out

def to_bmesh(obj, solid=True):
    with_cuts = cut_poly(obj)
    poly = polyfile(with_cuts)
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
    mesh.transform(obj.rot.to_matrix().to_4x4())
    mesh.transform(Matrix.Translation(obj.co))
    return mesh

