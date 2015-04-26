# A reference and starting point for your own Sly scripts.
#
# Python nano-tutorial:
# * Anything after a # character on a line is a comment, so Python will
#   ignore it.
# * Indentation matters. Make sure every line in a section is indented the
#   same number of spaces.
# * Python is case-sensitive.
#

# Import statements. These load in any special functions you use in your
# script. Shouldn't have to change these.
from sly.slicer import SliceDef, to_slices
import sly.plotter
import sly.ops
import sly.bcontext
import bpy
import mathutils

# Path to the SVG file if you're exporting one.
# On OSX this would probably look like
#     "/Users/myuser/Documents/blabla.svg"
# and on Windows something like
#     "C:\Users\myuser\Documents\blabla.svg"
# Unix/Linux users shouldn't need any help with this :-)
SVG_OUTFILE = '/path/to/output.svg'

# How thick should the slice parts be? Ex. If you've scaled your
# model so that 1 unit=1 inch, and you measured your material
# to be 0.24 inches thick, enter 0.24 here.
THICKNESS = 0.5


# These variables are handy for specifying slice directions.
X_DIR = (1, 0, 0)  # A plane with its face pointing in the X direction
Y_DIR = (0, 1, 0)  # ... in the Y direction
Z_DIR = (0, 0, 1)  # ... in the Z direction


# A SliceDef is how you define the slices that you want created.
# At a minimum, it must define the location of the slice plane.
# Plane locations are expressed in "co, no" form: A COordinate that
# lies on the plane, and the 3D NOrmal vector of the plane. Each of these
# are expressed as (X, Y, Z) vectors.
slice_defs = [
        SliceDef((0, 0, 0), X_DIR),  # The YZ plane
        SliceDef((3, 0, 0), X_DIR),  # The YZ plane moved 3 units in the X dir.

        # Optional arguments for SliceDef:
        #
        # * name - A string to override the generated name for this slice.
        # * z_index - Integer. Higher values will stack above slices with lower
        #             values. Useful for making sure that all slices in your
        #             construction are supported below by another slice (or the
        #             (ground).
        SliceDef((0, -2, 0), Y_DIR, z_index=1),
        SliceDef((0, 2, 0), Y_DIR, name="Front Part", z_index=1)
        ]


# Ask Blender for the mesh of whichever object you have selected in your
# scene. This needs to be executed in Object mode.
mesh = sly.bcontext.selected_bmesh()

# Hide the source object from view in Blender, so we can see the slices.
bpy.context.object.hide = True

# Where the magic happens. Sly returns a list of Slices from three required
# arguments: the mesh to slice up, the list of SliceDefs, and the thickness
# of the slices, in Blender units.
slices = to_slices(mesh, slice_defs, THICKNESS)

# to_slices has an additional optional argument:
#
# fillet_radius - Set to a positive number if you want the cutouts in your
# slice to have dogbone fillets. If you're cutting out your design on a CNC
# router, set this to the radius (half diameter) of the bit you're using. It
# will make the slices fit together better since the bit will be able to cut
# closer to the ideal square bottom.
#
# slices = to_slices(mesh, slice_defs, THICKNESS, fillet_radius=0.0625)


# Create a page to draw our 2D slice shapes onto. The numbers are the width
# and height of the output SVG, but we don't do any automatic placement. So
# you'll still probably want to use a program like Illustrator or Inkscape
# to position the slices.
page = sly.plotter.Page(10, 10)

# Do this stuff for each slice that was created by to_slices
for sli in slices:
    # Add the slice to the page we created above (for SVG output)
    page.add_slice(sli)

    # Apply the "border" operation to the slice. Cuts out the centers of the
    # slice and leaves a border of the specified thickness. Good for a
    # more lightweight-looking end result. We're making our border 2x the
    # thickness of our material; that should produce a nice effect without
    # weakening the construction too much.
    sly.ops.border(sli, THICKNESS * 2)

    # Finally, add the slice to the Blender scene as a new object. The object
    # will include the 'name' attribute you specified in the
    # SliceDef.
    sly.bcontext.add_slice(sli)


# Uncomment the next line if you want to export an SVG file as well.
# Make sure you specified a valid file path above!
# sly.plotter.SVGEncoder.encode(page, SVG_OUTFILE)
