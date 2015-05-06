import bmesh
from mathutils import Matrix
from sly.ops import render_poly
from sly.utils import each_ring


def to_bmesh(obj, solid=True):
    """Convert the slice to a bmesh positioned in 3-space. If solid is True,
    extrude the polygon to the proper thickness."""
    poly = render_poly(obj)

    bm = bmesh.new()

    for ring in each_ring(poly):
        verts = []
        for pt in ring.coords[:-1]:
            verts.append(bm.verts.new((pt[0], pt[1], 0)))
            if len(verts) > 1:
                bm.edges.new(verts[-2:])
        bm.edges.new((verts[-1], verts[0]))  # Close the loop

    bmesh.ops.triangle_fill(bm, edges=bm.edges[:],
                            use_dissolve=True)

    if solid:
        bm.transform(Matrix.Translation((0, 0, -obj.thickness / 2)))
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        res = bmesh.ops.extrude_face_region(bm, geom=geom)
        extruded_verts = [elem for elem in res['geom']
                          if isinstance(elem, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=extruded_verts,
                            vec=(0, 0, obj.thickness))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.transform(obj.rot.to_matrix().to_4x4())
    bm.transform(Matrix.Translation(obj.co))
    return bm

