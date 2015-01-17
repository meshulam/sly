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
#IPython.embed()


origin = mathutils.Vector((-12.1, -0.16, 0.43))
normal = mathutils.Vector((0.23537658154964447, 0.044095613062381744, 0.9709033370018005))

def set_editmode(object, value=True):
    if object.data.is_editmode != value:
        print("Toggled editmode")
        bpy.ops.object.editmode_toggle()


#for vert in blender_object.data.vertices:
#    print(vert.co.x)    # mathutils.Vector

def selected():
    return bpy.context.selected_objects[0]

def bisect_to_slices(obj, origin, normal):
    bpy.ops.object.duplicate(linked=False)
    #dupe = bpy.context.selected_objects[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=origin, plane_no=normal, clear_inner=True, clear_outer=True)
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode='OBJECT')
    # now can access obj.data.polygons
    mesh = selected().data

    points = [mesh.vertices[ind].co for ind in mesh.polygons[0].vertices]
    sli = slicer.Slice.from_3d_points(points, normal)
    return sli

def add_slice_to_scene(slice):
    # TODO: this one
    pass

blender_object = selected()
sli = bisect_to_slices(blender_object, origin, normal)
bm = sli.to_mesh()
bpy.ops.object.add(type='MESH')
new_mesh = bpy.data.meshes.get('Mesh')  # TODO: specify name?
IPython.embed()
