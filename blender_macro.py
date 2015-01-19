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

reload(slicer)

s1 = (Vector((3, 0, 0)), Vector((1, 0, 0)))
s2 = (Vector((0, 1, 0)), Vector((0, 1, 0)))

#normal = mathutils.Vector((0.23537658154964447, 0.044095613062381744, 0.9709033370018005))


def selected():
    return bpy.context.selected_objects[0]

def bisect_to_slice(obj, origin, normal):
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
    return slicer.Slice(origin, normal, bm)

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
sli = bisect_to_slice(blender_object, s1[0], s1[1])
sli2 = bisect_to_slice(blender_object, s2[0], s2[1])

sli.intersect(sli2, invert_cuts=False)
#IPython.embed()

add_bmesh_to_scene(sli.solid_mesh(), "slice1")
add_bmesh_to_scene(sli2.solid_mesh(), "slice2")

#IPython.embed()
