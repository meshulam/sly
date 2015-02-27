from sly.utils import biggest_polygon, pairwise
from mathutils.geometry import intersect_line_plane
import shapely.ops
import shapely.geometry
import IPython

def border(sli, amount):
    cuts = [cut.overlap_poly() for cut in sli.cuts]
    cut_outline = shapely.ops.cascaded_union(cuts) \
                             .buffer(amount * 0.5)
    shape_outline = sli.poly.boundary.buffer(amount)
    outlines = cut_outline.union(shape_outline)
    newpoly = outlines.intersection(sli.poly)
    sli.poly = biggest_polygon(newpoly)

def mutual_cut(sli1, sli2, cut_spec={}):
    """Given two slices, add the appropriate cuts to them if they intersect"""
    if sli1.rot == sli2.rot:
        return      # same orientation, so nothing to intersect

    cut_dir = sli1.cut_direction(sli2)
    points = []
    for (a, b) in pairwise(sli1.poly.exterior.coords):
        pta = sli1.to_3d(a)
        ptb = sli1.to_3d(b)

        intersect = intersect_line_plane(pta, ptb, sli2.co, sli2.normal())
        # Is the intersecting point between the ends of the segment?
        if intersect and (pta - intersect).dot(ptb - intersect) <= 0:
            points.append(intersect)

    if len(points) > 2:
        print("More than one intersection between slices. Not yet supported!")

    # There should always be an even number of crossings
    assert len(points) % 2 == 0

    z_factor = cut_spec.get('z_factor', 0.5)

    if len(points) >= 2:
        midpt = points[0].lerp(points[1], z_factor)
        sli1.add_cut(midpt, cut_dir, sli2.thickness)
        sli2.add_cut(midpt, -cut_dir, sli1.thickness)


def cut_poly(sli, cutouts_only=False):
    cut_shapes = []
    for cut in sli.cuts:
        shape = sli.get_cut_shape(cut)
        if shape:
            cut_shapes.append(shape)

    if not cut_shapes:
        return sli.poly

    cuts = shapely.ops.cascaded_union(cut_shapes) \
                      .buffer(sli.thickness / 1000, cap_style=3)
                      # To make sure we cut through the piece
    if cutouts_only:
        return cuts
    else:
        return biggest_polygon(sli.poly.difference(cuts))


