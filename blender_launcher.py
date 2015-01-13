import sys

dir = "/Users/matt/Dropbox/art/slots"
filename = dir + "/blender_macro.py"
if dir not in sys.path:
    sys.path.append(dir)
print(sys.path)
exec(compile(open(filename).read(), filename, 'exec'))