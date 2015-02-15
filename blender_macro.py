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
import sly.slicer
import sly.ops
import sly.plotter
import sly.encoders
import sly.bcontext

reload(sly.slicer)
reload(sly.ops)
reload(sly.plotter)
reload(sly.encoders)

scale_factor = 1
thickness = 0.20

a_dir = Vector((1, 0, 0))
b_dir = Vector((0, 1, 0))

slice_specs = [(Vector((8.8, 0, 0)), a_dir),
               (Vector((6, 0, 0)), a_dir),
               (Vector((0, 0, 0)), a_dir),
               (Vector((-6, 0, 0)), a_dir),
               (Vector((19.2, 0, 0)), a_dir),
               (Vector((14.5, 0, 0)), b_dir),
               (Vector((11, 0, 0)), b_dir),
               (Vector((5, 0, 0)), b_dir),
               (Vector((0, 0, 0)), b_dir),
               (Vector((-5, 0, 0)), b_dir),
               (Vector((-11, 0, 0)), b_dir),
               (Vector((-14.5, 0, 0)), b_dir),
               (Vector((-19.2, 0, 0)), b_dir)]

## For debugging
slice_specs = [(Vector((0, 0, 0)), a_dir),
               (Vector((0, 0, 0)), b_dir)]


bm = sly.bcontext.selected_bmesh()
IPython.embed()
#bm.transform(Matrix.Scale(scale_factor, 4))

slices = sly.slicer.to_slices(bm, slice_specs, thickness)


page = sly.plotter.Page(18, 18)
for i, sli in enumerate(slices):
    print("adding slice {}".format(i))
    sly.ops.border(sli, thickness * 4)
    sly.ops.apply_cuts(sli, 0.0625)
    page.add_slice(sli)
    sly.bcontext.add_slice(sli)

page.place()
sly.plotter.SVGEncoder.encode(page, "/Users/matt/output.svg")


