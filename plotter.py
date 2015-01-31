import IPython
import svgwrite
from svgwrite import Drawing
from svgwrite.mixins import ViewBox
import slicer
import shapely

class SVGEncoder(object):
    def __init__(self, page, filename):
        self.page = page

        viewbox = ('{} {} {} {}'.format(0, 0, page.width, page.height))
        self.dwg = Drawing(filename=filename, viewBox=viewbox, debug=True,
                           size=(page.width_str(), page.height_str()))

    def _make_part(self, part):
        stroke = part.thickness / 4
        grp = self.dwg.g(stroke='red', fill='none', stroke_width=stroke)
        xformed = part.positioned()
        for ring in [xformed.exterior] + xformed.interiors[:]:
            grp.add(self.dwg.polygon(points=ring.coords[:]))

        self.dwg.add(grp)

    def encode_self(self):
        for part in self.page.parts:
            self._make_part(part)
        self.dwg.save()

    @classmethod
    def encode(cls, page, filename):
        encoder = cls(page, filename)
        encoder.encode_self()


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
            (minx, miny, maxx, maxy) = part.positioned().bounds
            if minx < 0:
                part.move(-minx, 0)
            if miny < 0:
                part.move(0, -miny)

            if maxx > self.width:
                part.move(self.width - maxx, 0)
            if maxy > self.height:
                part.move(0, self.height - maxy)


