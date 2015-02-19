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
import sly.utils

reload(sly.slicer)
reload(sly.ops)
reload(sly.plotter)
reload(sly.encoders)
reload(sly.bcontext)
reload(sly.utils)

scale_factor = 1
thickness = 0.20

a_dir = Vector((2, 1, 0))
b_dir = Vector((1, -2, 0))

slice_specs = [(Vector((8.8, 0, 0)), a_dir),
               (Vector((6, 0, 0)), a_dir),
               (Vector((0, 0, 0)), a_dir),
               (Vector((-6, 0, 0)), a_dir),
               (Vector((-8.8, 0, 0)), a_dir),
               (Vector((0, 19.2, 0)), b_dir),
               (Vector((0, 14.5, 0)), b_dir),
               (Vector((0, 11, 0)), b_dir),
               (Vector((0, 5, 0)), b_dir),
               (Vector((0, 0, 0)), b_dir),
               (Vector((0, -5, 0)), b_dir),
               (Vector((0, -11, 0)), b_dir),
               (Vector((0, -14.5, 0)), b_dir),
               (Vector((0, -19.2, 0)), b_dir)]

## For debugging
#slice_specs = [
#               (Vector((0, 0, 0)), a_dir),
 #              (Vector((-6, 0, 0)), a_dir),
 #              (Vector((0, -19.2, 0)), b_dir)]


bm = sly.bcontext.selected_bmesh()
#bm.transform(Matrix.Scale(scale_factor, 4))

slices = sly.slicer.to_slices(bm, slice_specs, thickness)

page = sly.plotter.Page(18, 18)
for sli in slices:
    print("adding slice " + sli.ident)
    sly.ops.border(sli, thickness * 4)
    sly.ops.apply_cuts(sli, fillet=0.05)
    page.add_slice(sli)
    sly.bcontext.add_slice(sli)

sly.plotter.SVGEncoder.encode(page, "/Users/matt/output.svg")


