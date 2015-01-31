
# Slice3D

    def bisect_solid(self, other):
        for co in [other.front_coord(), other.back_coord()]:
            self.bisect(co, other.no)

    def front_coord(self):
        return self.co + (self.no * self.thickness / 2)

    def back_coord(self):
        return self.co - (self.no * self.thickness / 2)

    def is_within_thickness(self, pt):
        """Does the point lie in the thickness of this slice?"""
        d1 = distance_point_to_plane(pt, self.front_coord(), self.no)
        d2 = distance_point_to_plane(pt, self.back_coord(), self.no)
        return (d1 * d2) < 0    # Opposite signs

    def intersect(self, other, invert_cuts=False):
        """Cut slots into this slice and another one so they fit together."""
        cut_dir = self.no.cross(other.no)
        if invert_cuts:
            cut_dir = -cut_dir

        self.bisect_solid(other)
        other.bisect_solid(self)

        self_faces = self.mesh.faces[:]     # make a copy since we're mutating stuff

        for face in self_faces:
            if not face.is_valid:
                continue

            # The point that defines the halfway point where the two cuts meet
            pt = face.calc_center_bounds()
            if not other.is_within_thickness(pt):
                continue         # this isn't a face formed by the bisect_solid

            for oface in other.mesh.faces:
                if bounding_boxes_intersect(face, oface):
                    # For corresponding faces on other, remove parts behind the cut_dir plane
                    remove_face_behind_plane(other.mesh, oface, pt, -cut_dir)

            # clear the part of this face behind the cut_dir plane
            remove_face_behind_plane(self.mesh, face, pt, cut_dir)
    def intersect(self, other, invert_cuts=False):
        """Cut slots into this slice and another one so they fit together."""
        cut_dir = self.no.cross(other.no)
        if invert_cuts:
            cut_dir = -cut_dir

        self.bisect_solid(other)
        other.bisect_solid(self)

        self_faces = self.mesh.faces[:]     # make a copy since we're mutating stuff

        for face in self_faces:
            if not face.is_valid:
                continue

            # The point that defines the halfway point where the two cuts meet
            pt = face.calc_center_bounds()
            if not other.is_within_thickness(pt):
                continue         # this isn't a face formed by the bisect_solid

            for oface in other.mesh.faces:
                if bounding_boxes_intersect(face, oface):
                    # For corresponding faces on other, remove parts behind the cut_dir plane
                    remove_face_behind_plane(other.mesh, oface, pt, -cut_dir)

            # clear the part of this face behind the cut_dir plane
            remove_face_behind_plane(self.mesh, face, pt, cut_dir)

def is_positive(vector):
    """For any two nonzero vectors X and -X, guaranteed to return true for
    exactly one of them"""
    for elem in vector:
        if elem > 0:
            return True
        elif elem < 0:
            return False
    return False  # Only gets here for zero vectors


def bounding_boxes_intersect(face1, face2):
    min1 = numpy.amin([vert.co for vert in face1.verts], axis=0)
    max1 = numpy.amax([vert.co for vert in face1.verts], axis=0)
    min2 = numpy.amin([vert.co for vert in face2.verts], axis=0)
    max2 = numpy.amax([vert.co for vert in face2.verts], axis=0)
    return numpy.all(numpy.greater(max1, min2)) \
        and numpy.all(numpy.greater(max2, min1))

def is_point_behind_plane(point, plane_co, plane_no):
    return distance_point_to_plane(point, plane_co, plane_no) < 0

def remove_face_behind_plane(bm, face, plane_co, plane_no):
    geom = face.verts[:] + face.edges[:] + [face]
    ret = bmesh.ops.bisect_plane(bm, geom=geom,
                                 plane_co=plane_co, plane_no=plane_no)
    newface = None
    for elem in ret['geom']:
        if not isinstance(elem, bmesh.types.BMFace):
            continue
        if is_point_behind_plane(elem.calc_center_bounds(), plane_co, plane_no):
            bmesh.ops.delete(bm, geom=[elem], context=5)
        else:
            newface = elem
    return newface
