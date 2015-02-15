from sly.utils import biggest_polygon
import shapely.ops
import shapely.geometry

def border(sli, amount):
    cuts = [cut.overlap_poly() for cut in sli.cuts]
    cut_outline = shapely.ops.cascaded_union(cuts) \
                             .buffer(amount * 0.5)
    shape_outline = sli.poly.boundary.buffer(amount)
    outlines = cut_outline.union(shape_outline)
    newpoly = outlines.intersection(sli.poly)
    sli.poly = biggest_polygon(newpoly)

def apply_cuts(sli, fillet=0):
    cut_shapes = []
    for cut in sli.cuts:
        shape = sli.get_cut_shape(cut, fillet=fillet)
        if shape:
            cut_shapes.append(shape)

    if not cut_shapes:
        return

    cuts = shapely.ops.cascaded_union(cut_shapes) \
                      .buffer(sli.thickness / 1000, cap_style=3)
                      # To make sure we cut through the piece
    out = sli.poly.difference(cuts)
    sli.poly = biggest_polygon(out)


