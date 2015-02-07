from sly.slicer import biggest_polygon
import shapely.ops
import shapely.geometry

def border(sli, amount):
    cuts = [cut.polygon(True) for cut in sli.cuts]
    cut_outline = shapely.ops.cascaded_union(cuts) \
                             .buffer(amount / 2)
    shape_outline = sli.poly.boundary.buffer(amount)
    outlines = cut_outline.union(shape_outline)
    newpoly = outlines.intersection(sli.poly)
    sli.poly = biggest_polygon(newpoly)

def apply_cuts(sli):
    cut_shapes = []
    for cut in sli.cuts:
        shape = sli.get_cut_shape(cut)
        if shape:
            cut_shapes.append(shape)

    if not cut_shapes:
        return

    cuts = shapely.ops.cascaded_union(cut_shapes) \
                      .buffer(sli.thickness / 1000, cap_style=3)
                      # To make sure we cut through the piece
    out = sli.poly.difference(cuts)
    sli.poly = biggest_polygon(out)


