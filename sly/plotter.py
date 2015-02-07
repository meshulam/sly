import IPython
import svgwrite
from svgwrite import Drawing
import shapely

class SVGEncoder(object):
    def __init__(self, page, filename):
        self.page = page

        viewbox = ('{} {} {} {}'.format(0, 0, page.width, page.height))
        wstr = str(page.width) + page.unit
        hstr = str(page.height) + page.unit
        self.dwg = Drawing(filename=filename, viewBox=viewbox, debug=True,
                           size=(wstr, hstr))

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

    def add_slice(self, sli2d):
        self.parts.append(sli2d)

    def place(self):
        pass
#        for part in self.parts:
#            (minx, miny, maxx, maxy) = part.positioned().bounds
#            if minx < 0:
#                part.move(-minx, 0)
#            if miny < 0:
#                part.move(0, -miny)
#
#            if maxx > self.width:
#                part.move(self.width - maxx, 0)
#            if maxy > self.height:
#                part.move(0, self.height - maxy)


