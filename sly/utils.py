import itertools
from mathutils import Quaternion, Vector

def to_2d(vec, co=None, rot=None):
    rot_conj = rot.conjugated() if rot else Quaternion()
    newvec = (vec - co) if co else vec
    return rotated(newvec, rot_conj).to_2d()

def to_3d(vec, co=None, rot=None):
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

def biggest_polygon(polys):
    """Returns the shape with the largest area out of the provided
    shapely object or collection"""
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


#def point_minmax(points, direction):
#    """Returns the two points out of the given iterable
#    that represent the range when projected in the given direction"""
#    p1 = points[0]
#    p2 = p1
#    for point in points:
#        if direction.dot(point - p1) < 0:
#            p1 = point
#        elif direction.dot(point - p2) > 0:
#            p2 = point
#    return (p1, p2)

