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
import slicer
import slice_ops
import plotter

reload(slicer)
reload(slice_ops)
reload(plotter)

a_dir = Vector((1, 1, 0))
a_pts = [Vector((3, 0, 0)),
         Vector((0, 0, 0)),
         Vector((8, 0, 0)),
         Vector((-5, 0, 0))]
b_dir = Vector((-1, 1, 0))
b_pts = [Vector((0, -3, 0)),
         Vector((0, 0, 0)),
         Vector((0, 3, 0))]


def selected():
    return bpy.context.selected_objects[0]

def bisect_to_slice(obj, origin, normal, thickness):
    scene = bpy.context.scene
    bm = bmesh.new()
    bm.from_object(obj, scene)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    ret = bmesh.ops.bisect_plane(bm, geom=geom,
                                 dist=0.0001,
                                 plane_co=origin, plane_no=normal,
                                 use_snap_center=False,
                                 clear_outer=True, clear_inner=True)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    ret2 = bmesh.ops.contextual_create(bm, geom=geom)
    return slicer.Slice(origin, normal, bm, thickness=thickness)

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

for a_pt in a_pts:
    a_slices.append(bisect_to_slice(blender_object, a_pt, a_dir, 0.25))

for b_pt in b_pts:
    b_slices.append(bisect_to_slice(blender_object, b_pt, b_dir, 0.25))

for asli in a_slices:
    for bsli in b_slices:
        asli.mutual_cut(bsli)

for sli in a_slices + b_slices:
    add_bmesh_to_scene(sli.solid_mesh())

#page = plotter.Page(48, 24)
#for sli in a_slices:
#    s2d = slicer.Slice2D.from_3d(sli)
#    slice_ops.border(s2d, 1)
#    s2d.apply_cuts()
#    page.add_slice(s2d)

#page.place()
#plotter.SVGEncoder.encode(page, "/Users/matt/output.svg")


