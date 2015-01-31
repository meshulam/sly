import IPython
import svgwrite
from svgwrite import Drawing
from svgwrite.mixins import ViewBox
import slicer
import shapely

class Page(object):
    def __init__(self, width, height, unit="in"):
        self.width = width
        self.height = height
        self.unit = unit
        self.parts = []  # Slice2D contains 2d rotation/translation data

    def width_str(self):
        return str(self.width) + self.unit

    def height_str(self):
        return str(self.height) + self.unit

    def save(self, filename):
        self._drawing.saveas(filename)

    def add_slice(self, sli2d):
        self.parts.append(sli2d)

    def place(self):
        for part in self.parts:
            pass

    def to_svg(self, filename):
        viewbox = ('{} {} {} {}'.format(0, 0, self.width, self.height))
        drawing = Drawing(filename=filename, viewBox=viewbox,
                          size=(self.width_str(), self.height_str()))

        for part in self.parts:
            xformed = part.positioned()
            for ring in xformed.interiors[:] + [xformed.exterior]:
                poly = drawing.polygon(points=[pt for pt in ring.coords])
                drawing.add(poly)
        drawing.save()

