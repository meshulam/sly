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
import slicer

reload(slicer)

origin = mathutils.Vector((4, 0, 0))
#normal = mathutils.Vector((0.23537658154964447, 0.044095613062381744, 0.9709033370018005))
normal = mathutils.Vector((1, 0, 0))


def selected():
    return bpy.context.selected_objects[0]

def bisect_to_slices(obj, origin, normal):
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
    slices = []
    for face in ret2['faces']:
        points = [vert.co for vert in face.verts]
        slices.append(slicer.Slice.from_3d_points(points, normal))
    return slices

def add_bmesh_to_scene(bm):
    mesh = bpy.data.meshes.new("newmesh")
    bm.to_mesh(mesh)
    ob = bpy.data.objects.new("meshObj", mesh)
    scene = bpy.context.scene
    scene.objects.link(ob)
    scene.objects.active = ob
    ob.select = True
    mesh.update()

blender_object = selected()
slices = bisect_to_slices(blender_object, origin, normal)
for sli in slices:
    bm = sli.to_mesh()
    add_bmesh_to_scene(bm)

#IPython.embed()
