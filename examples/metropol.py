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

svg_outfile = '/path/to/output.svg'

thickness = 0.5

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


bmesh = sly.bcontext.selected_bmesh()

slices = to_slices(bmesh, slice_specs, thickness)

page = sly.plotter.Page(30, 30)

for sli in slices:
    print("adding slice " + sli.name)
    sly.ops.border(sli, thickness * 4)

    page.add_slice(sli)
    sly.bcontext.add_slice(sli)

sly.plotter.SVGEncoder.encode(page, svg_outfile)


