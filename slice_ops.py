import slicer
import shapely.ops
import shapely.geometry

def border(sli, amount):
    cuts = [cut.polygon(True) for cut in sli.cuts]
    cut_outline = shapely.ops.cascaded_union(cuts) \
                             .buffer(amount / 2)
    shape_outline = sli.poly.boundary.buffer(amount)
    outlines = cut_outline.union(shape_outline)
    newpoly = outlines.intersection(sli.poly)
    sli.poly = newpoly

