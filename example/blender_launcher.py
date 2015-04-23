import sys

# This is a small script that you can load in Blender and use to bootstrap
# another arbitrary script. Useful if you prefer to use an external editor
# instead of Blender's text editor. See:
# http://www.blender.org/api/blender_python_api_2_73_release/info_tips_and_tricks.html#use-an-external-editor

dir = "/path/to/script_file"
filename = dir + "/blender_macro.py"
if dir not in sys.path:
    sys.path.append(dir)
exec(compile(open(filename).read(), filename, 'exec'))