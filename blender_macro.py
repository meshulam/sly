import sys

lib_path = '/Users/matt/venv/blender/lib/python3.4/site-packages'
if lib_path not in sys.path:
    sys.path.append(lib_path)

module_path = '/Users/matt/Dropbox/art/slots'
if module_path not in sys.path:
    sys.path.append(module_path)

from importlib import reload
import IPython
import bpy
import bmesh
import mathutils
from mathutils import Vector, Matrix
from sly.slicer import SliceDef
import sly.slicer
import sly.ops
import sly.plotter
import sly.encoders
import sly.bcontext
import sly.utils

reload(sly.slicer)
reload(sly.ops)
reload(sly.plotter)
reload(sly.encoders)
reload(sly.bcontext)
reload(sly.utils)

scale_factor = 1
thickness = 0.493

#
#   top view:  ^y ->x
#   b-----a
#   |     |
#   c-----d
#
#   / j   \ k

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

#slice_specs = [SliceDef((0, 0, 18.8), Vector((0, 0, 1)))]
#cut_specs = []

## For debugging

bm = sly.bcontext.selected_bmesh()

slices = sly.slicer.to_slices(bm, slice_specs, thickness,
                              cut_specs=cut_specs)

page = sly.plotter.Page(18, 18)

for sli in slices:
    print("adding slice " + sli.name)
    sli.fillet = 0.125

    sly.ops.border(sli, thickness * 4)
    page.add_slice(sli)
    sly.bcontext.add_slice(sli)

sly.plotter.SVGEncoder.encode(page, "/Users/matt/output.svg")


