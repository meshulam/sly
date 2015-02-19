import math
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
        xformed = part.poly
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

    def add_slice(self, sli):
        self.parts.append(sli)

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

class PagePosition(object):
    def __init__(self, xoff=0, yoff=0, rot_deg=0):
        self.xoff = xoff
        self.yoff = yoff
        self.rotation = math.radians(rot_deg)

    def to_matrix(self):
        return (math.cos(self.rotation), -math.sin(self.rotation),
                math.sin(self.rotation), math.cos(self.rotation),
                self.xoff, self.yoff)

# This was on slice previously
def positioned(self):
    return shapely.affinity.affine_transform(self.poly,
                                             self.page_position.to_matrix())
