import svgwrite
from svgwrite import Drawing
import slicer
import shapely

class Page(object):
    def __init__(self, width, height, unit="in"):
        self.width = width
        self.height = height
        self.unit = unit
        viewbox = svgwrite.mixins.ViewBox(0, 0, width, height)
        self._drawing = Drawing(size=(str(width) + unit, str(height) + unit),
                                viewbox=viewbox)

    def save(self, filename):
        self._drawing.saveas(filename)

    def add_slice(self, sli2d):
        if isinstance(sli2d.polys, shapely.geometry.MultiPolygon):
            print("It's a multipolygon :-(")
            return
        poly = Drawing.polygon(points=[pt for pt in sli2d.polys.exterior.coords])
        self._drawing.add(poly)


