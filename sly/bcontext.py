"""
The functions in this module can only be called from within blender.
It's basically just some convenience functions around blender's bpy module.
"""

from sly.encoders import to_bmesh
import bpy
import bmesh

def selected_bmesh():
    ob = selected()
    bm = bmesh.new()
    bm.from_object(ob, bpy.context.scene)
    return bm

def add_slice(sli):
    """Add the provided slice to the current scene"""
    smesh = to_bmesh(sli)
    name = "slice" + sli.name
    add_bmesh(smesh, name=name)

def add_bmesh(bm, name="mesh"):
    """Add the provided bmesh to the current scene"""
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    ob = bpy.data.objects.new(name, mesh)
    scene = bpy.context.scene
    scene.objects.link(ob)
    scene.objects.active = ob
    ob.select = True
    mesh.update()

def selected():
    return bpy.context.selected_objects[0]
