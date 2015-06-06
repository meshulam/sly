import svgwrite
from shapely.affinity import translate


def plot_polys(polys, filename):
    box_w = max([poly.bounds[2] for poly in polys])
    page_w = box_w * 5
    page_h = max([poly.bounds[3] for poly in polys])

    viewbox = ('{} {} {} {}'.format(0, 0, page_w, page_h))
    wstr = str(page_w) + "in"
    hstr = str(page_h) + "in"
    dwg = svgwrite.Drawing(filename=filename, viewBox=viewbox, debug=True,
                           size=(wstr, hstr))

    cursor = [0, 0]

    for poly in polys:
        positioned_poly = translate(poly, xoff=cursor[0], yoff=cursor[1])
        grp = dwg.g(stroke='red', fill='none', stroke_width=1)
        for ring in [positioned_poly.exterior] + positioned_poly.interiors[:]:
            grp.add(dwg.polygon(points=ring.coords[:]))

        cursor[0] += box_w

        dwg.add(grp)

    dwg.save()