import itertools

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
    return itertools.izip(a, b)


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

