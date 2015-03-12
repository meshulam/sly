import sys

# There's probably a better way to load external modules to run within
# Blender. But this worked for me.
lib_path = '/path/to/virtualenv/blender/lib/python3.4/site-packages'
if lib_path not in sys.path:
    sys.path.append(lib_path)

from mathutils import Vector
from sly.slicer import SliceDef, to_slices
import sly.ops
import sly.plotter
import sly.bcontext

#
#   top view:  ^y ->x
#   b-----a
#   |     |
#   c-----d
#

thickness = 0.493

x_dir = Vector((1, 0, 0))
y_dir = Vector((0, 1, 0))

leg_a = Vector((17.5, 8.5, 0))
leg_c = Vector((-17.5, -8.5, 0))

slice_specs = [
                SliceDef(leg_a, x_dir, z_index=0),
                SliceDef(leg_c, x_dir, z_index=0),
                SliceDef(leg_a, y_dir, z_index=1),
                SliceDef(leg_c, y_dir, z_index=1),
                SliceDef((0, 4, 0), y_dir, z_index=2),
                SliceDef((0, -4, 0), y_dir, z_index=2),
                SliceDef((20, 0, 18), x_dir, z_index=3),
                SliceDef((-20, 0, 18), x_dir, z_index=3),
                SliceDef((12, 0, 18), x_dir, z_index=3),
                SliceDef((-12, 0, 18), x_dir, z_index=3),
                SliceDef((4, 0, 0), x_dir, z_index=3),
                SliceDef((-4, 0, 0), x_dir, z_index=3),
                ]

# Override for cuts that you don't want to be exactly 50% of the way
# through. This should be cleaned up to be aware of which way Up is,
# and to allow better ways to reference slice intersections.
cut_specs = [
                {"intersect": ("2.0", "6.0"), "z_factor": 0.25},
                {"intersect": ("2.0", "7.0"), "z_factor": 0.75},
                {"intersect": ("3.0", "6.0"), "z_factor": 0.25},
                {"intersect": ("3.0", "7.0"), "z_factor": 0.75},

                {"intersect": ("5.0", "6.0"), "z_factor": 0.35},
                {"intersect": ("5.0", "7.0"), "z_factor": 0.65},
                {"intersect": ("4.0", "6.0"), "z_factor": 0.65},
                {"intersect": ("4.0", "7.0"), "z_factor": 0.35},
            ]


bm = sly.bcontext.selected_bmesh()

slices = to_slices(bm, slice_specs, thickness,
                   cut_specs=cut_specs)

page = sly.plotter.Page(30, 30)

for sli in slices:
    print("adding slice " + sli.name)
    sli.fillet = 0.125 / 2

    sly.ops.border(sli, thickness * 4)
    page.add_slice(sli)
    sly.bcontext.add_slice(sli)

sly.plotter.SVGEncoder.encode(page, "/Users/matt/output.svg")


