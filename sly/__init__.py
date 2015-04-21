
if "bpy" in locals():
    import importlib
    importlib.reload(slicer)
else:
    from . import slicer
