# Exploring an app specifically for making
# patterns for box-joint crates.

# Specify dimensions as (W, L, H) in inches.
# Exterior dimensions. Inside of container will
# be smaller because of wood thickness.
#
#     /-------/|
#    /-------/ |
#    |       | |
#   H|       |/L
#    o-------/
#       W
#
# Face order: HW, HW', HL, HL', WL, WL'
# WL' is open by default


import itertools
import svgwrite
from shapely.geometry import box
from shapely.affinity import translate, rotate
from shapely.ops import unary_union

# Constants for types of edges
EDGE_SOLO = 0     # No face sharing the edge
EDGE_UNDER = 1    # The other face is the "master" in the edge
EDGE_OVER = 2     # This face is the master. If a face has two adjacent
                  # EDGE_OVERs, it also owns the corner.

FACE_FRONT = 0
FACE_BACK = 1
FACE_LEFT = 2
FACE_RIGHT = 3
FACE_BOTTOM = 4
FACE_TOP = 5


class Cube(object):
    def __init__(self, dims, thickness, tooth_width=None, tooth_slop=0.02):
        (self.width, self.length, self.height) = dims
        self.thickness = thickness

        if tooth_width:
            self.tooth_width = tooth_width
        else:
            self.tooth_width = self.thickness * 2

        self.tooth_slop = tooth_slop

    def gen_faces(self):
        return [self.get_face(i) for i in range(5)]

    def get_face(self, ind):
        if ind < 2:     # Front/back face
            return self.gen_face(self.width, self.height,
                                 (EDGE_UNDER, EDGE_OVER,
                                  EDGE_SOLO, EDGE_OVER))
        elif ind < 4:   # Left/right face
            return self.gen_face(self.length, self.height,
                                 (EDGE_UNDER, EDGE_UNDER,
                                  EDGE_SOLO, EDGE_UNDER))
        elif ind < 5:   # Bottom face
            return self.gen_face(self.width, self.length,
                                 (EDGE_OVER, EDGE_OVER,
                                  EDGE_OVER, EDGE_OVER))

    def gen_face(self, width, height, edges):
        """
        Generate a Shapely polygon with the specified params.
        edges is a list of four EDGE_* constant values. They are the
        types of edges for bottom, right, top, left.
        """

        outer = box(0, 0, width, height)

        cutouts = []
        for i, edge_type in enumerate(edges):
            translation = [0, 0]
            if i == 1 or i == 2:
                translation[0] = width

            if i > 1:
                translation[1] = height

            if i % 2 == 0:
                distance = width
            else:
                distance = height

            teeth = self.cutout_teeth(distance, edge_type)
            teeth = rotate(teeth, 90*i, origin=(0, 0))
            teeth = translate(teeth, xoff=translation[0], yoff=translation[1])
            cutouts.append(teeth)

        negative = unary_union(cutouts)
        return outer.difference(negative)

    def cutout_teeth(self, distance, edge_type):
        """
        Returns a list of shapes to cut out to make teeth. They are positioned
        starting at roughly (0, 0) going +x. The tops (toward center of the
        overall shape) is along y=thickness.
        """
        teeth = []
        if edge_type == EDGE_SOLO:
            return unary_union(teeth)

        num_teeth = round_nearest_odd(distance / self.tooth_width)
        real_width = distance / num_teeth

        if edge_type == EDGE_OVER:
            start_ind = 0
        else:
            start_ind = 1

        base_tooth = box(-self.tooth_slop/2, 0,
                         real_width + self.tooth_slop/2, self.thickness)

        for tick in range(start_ind, num_teeth, 2):
            tooth = translate(base_tooth, xoff=tick*real_width)
            teeth.append(tooth)

        return unary_union(teeth)

def round_nearest_odd(num):
    return round((num + 1) / 2) * 2 - 1

