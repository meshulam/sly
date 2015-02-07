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
from mathutils import Vector
import sly.slicer
import sly.ops
import sly.plotter
import sly.encoders

reload(sly.slicer)
reload(sly.ops)
reload(sly.plotter)
reload(sly.encoders)


a_dir = Vector((1, 2, 0))
a_pts = [Vector((12.5, 0, 0)),
         Vector((7, 0, 0)),
         Vector((3, 0, 0)),
         Vector((-4, 0, 0)),
         Vector((-6.5, 0, 0)),
         Vector((-13, 0, 0))
         ]
b_dir = Vector((-2, 1, 0))
b_pts = [Vector((11, 0, 0)),
         Vector((9, 0, 0)),
         Vector((5, 0, 0)),
         Vector((-.5, 0, 0)),
         Vector((-3.5, 0, 0)),
         Vector((-8.5, 0, 0))
         ]

## For debugging
#a_dir = Vector((1, 2, 0))
#b_dir = Vector((-2, 1, 0))
#a_pts = [Vector((12.5, 0, 0))]
#b_pts = [Vector((9, 0, 0))]


def selected():
    return bpy.context.selected_objects[0]

def add_bmesh_to_scene(bm, name="mesh"):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    ob = bpy.data.objects.new(name, mesh)
    scene = bpy.context.scene
    scene.objects.link(ob)
    scene.objects.active = ob
    ob.select = True
    mesh.update()

blender_object = selected()
a_slices = []
b_slices = []

scene = bpy.context.scene

bm = bmesh.new()
bm.from_object(blender_object, scene)

for a_pt in a_pts:
    mesh = bm.copy()
    slyce = sly.slicer.Slice.create(mesh, a_pt, a_dir, 0.25)
    a_slices.append(slyce)

for b_pt in b_pts:
    mesh = bm.copy()
    slyce = sly.slicer.Slice.create(mesh, b_pt, b_dir, 0.25)
    b_slices.append(slyce)

for asli in a_slices:
    for bsli in b_slices:
        asli.mutual_cut(bsli)

#for sli in a_slices + b_slices:
#    add_bmesh_to_scene(sli.solid_mesh())

page = sly.plotter.Page(18, 18)
for i, sli in enumerate(a_slices + b_slices):
    slices = sly.slicer.Slice2D.from_3d(sli)
    for j, sl in enumerate(slices):
        print("adding slice A{}.{}".format(i, j))
        #sly.ops.border(sl, 1)
        sly.ops.apply_cuts(sl)
        page.add_slice(sl)
        smesh = sly.encoders.to_bmesh(sl)
        add_bmesh_to_scene(smesh)


page.place()
sly.plotter.SVGEncoder.encode(page, "/Users/matt/output.svg")


