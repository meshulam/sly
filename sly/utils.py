import itertools
from mathutils import Quaternion, Vector, Matrix

def to_2d(vec, co=None, rot=None):
    """Transform the given 3D vector back to 2D according to co and rot.
    This should probably do some assertion
    that the vector actually lies in the XY plane. If not, this function
    is probably being used incorrectly."""
    rot_conj = rot.conjugated() if rot else Quaternion()
    newvec = (vec - co) if co else vec
    return rotated(newvec, rot_conj).to_2d()

def to_3d(vec, co=None, rot=None):
    """Take a 2D vector (or the XY of a 3D vector) and transform it
    according to co and rot."""
    newvec = Vector((vec[0], vec[1], 0))
    if rot:
        newvec.rotate(rot)
    if co:
        newvec += co
    return newvec

def each_shape(geom):
    """Takes a shapely Shape or collection and returns
    an iterable. Useful when you don't know whether you got one
    or more shapes as the result of an operation"""
    if hasattr(geom, 'geoms'):
        return geom
    else:
        return [geom]

def each_ring(poly):
    for polygon in each_shape(poly):
        for ring in [polygon.exterior] + polygon.interiors[:]:
            yield ring

def biggest_polygon(polys):
    """Returns the shape with the largest area out of the provided
    shapely object or collection. We really shouldn't need this function,
    but sometimes operations can cut little corners off a polygon, so this
    is a hacky workaround that usually does the right thing."""
    biggest = max(each_shape(polys), key=lambda p: p.area)

    if hasattr(polys, 'geoms'):    # We started with more than one
        print("Biggest poly: {} total {} ({})"
              .format(biggest.area, polys.area, len(polys)))
    return biggest

def rotated(vector, rot):
    """Returns a copy of the given mathutils vector rotated by the
    provided transformation."""
    vec_new = vector.copy()
    vec_new.rotate(rot)
    return vec_new

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

