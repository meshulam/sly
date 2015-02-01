import shapely.ops
import shapely.geometry
import bmesh

def border(sli, amount):
    cuts = [cut.polygon(True) for cut in sli.cuts]
    cut_outline = shapely.ops.cascaded_union(cuts) \
                             .buffer(amount / 2)
    shape_outline = sli.poly.boundary.buffer(amount)
    outlines = cut_outline.union(shape_outline)
    newpoly = outlines.intersection(sli.poly)
    sli.poly = newpoly

def apply_cuts(sli):
    cut_shapes = [sli.get_cut_shape(cut) for cut in sli.cuts]
    cuts = shapely.ops.cascaded_union(cut_shapes)
    out = sli.poly.difference(cuts)
    if hasattr(out, 'geoms'):
        print("WARNING: cut produced disconnected shapes!")
    sli.poly = out

def create_slice(mesh, origin, normal, thickness):
    geom = mesh.verts[:] + mesh.edges[:] + mesh.faces[:]
    ret = bmesh.ops.bisect_plane(mesh, geom=geom,
                                 dist=0.0001,
                                 plane_co=origin, plane_no=normal,
                                 use_snap_center=False,
                                 clear_outer=True, clear_inner=True)
    geom = mesh.verts[:] + mesh.edges[:] + mesh.faces[:]
    ret2 = bmesh.ops.contextual_create(mesh, geom=geom)
    return sly.slicer.Slice(origin, normal, mesh, thickness=thickness)

