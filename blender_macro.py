import sys
import bpy
import bmesh
import mathutils

sys.path.append('/Users/matt/venv/blender/lib/python3.4/site-packages')

blender_object = bpy.context.selected_objects[0]

origin = mathutils.Vector((-12.1, -0.16, 0.43))
normal = mathutils.Vector((0.23537658154964447, 0.044095613062381744, 0.9709033370018005))

def set_editmode(object, value=True):
    if object.data.is_editmode != value:
        print("Toggled editmode")
        bpy.ops.object.editmode_toggle()


#bpy.ops.mesh.bisect(plane_co=(-3.49123, -7.25028, -0.826019), plane_no=(-0.122268, 0.378871, 0.917337), clear_inner=True, clear_outer=True, xstart=74, xend=133, ystart=214, yend=197)

#for vert in blender_object.data.vertices:
#    print(vert.co.x)    # mathutils.Vector
    
def bisect_to_slices(obj, origin, normal):
    bpy.ops.object.duplicate(linked=False)
    #dupe = bpy.context.selected_objects[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(plane_co=origin, plane_no=normal, clear_inner=True, clear_outer=True)
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode='OBJECT')
    # now can access obj.data.polygons
    
bisect_to_slices(blender_object, origin, normal)
