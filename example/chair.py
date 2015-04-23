"""Sly script included with chair.blend"""

from sly.slicer import SliceDef, to_slices
import sly.plotter
import sly.bcontext

svg_outfile = '/path/to/output.svg'

thickness = 0.15

x_dir = (1, 0, 0)
y_dir = (0, 1, 0)

# legs are at X=+/-1.5, Y=[-1.5, 1.75]

slice_specs = [
        SliceDef((-1.5, 0, 0), x_dir),
        SliceDef((1.5, 0, 0), x_dir),
        SliceDef((0, -1.5, 0), y_dir),
        SliceDef((0, 1.75, 0), y_dir),

        SliceDef((-0.5, 0, 0), x_dir),
        SliceDef((0.5, 0, 0), x_dir),
        SliceDef((0, -0.5, 0), y_dir),
        SliceDef((0, 0.5, 0), y_dir),
        ]


bmesh = sly.bcontext.selected_bmesh()

slices = to_slices(bmesh, slice_specs, thickness)

page = sly.plotter.Page(30, 30)

for sli in slices:
    # page.add_slice(sli)
    sly.bcontext.add_slice(sli)

# Uncomment to export SVG
# sly.plotter.SVGEncoder.encode(page, svg_outfile)

