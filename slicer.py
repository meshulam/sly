import FreeCAD
import Mesh
import Part
from FreeCAD import Base

MODEL = "/Users/matt/Dropbox/art/Coffee table/attempt3-lines2.stl"
MODEL_DIMS = [48, 24, 20]

SLICE_A_DIR = (1, 0, 0)
SLICE_B_DIR = (0, 1, 0)

SLICES_A = [4, 10, 20, 30, 40, 42, 44]
SLICES_B = [4, 8, 12, 16, 20, 22]

THICKNESS = 0.5

###############
slice_a_vec = FreeCAD.Vector(SLICE_A_DIR)
slice_b_vec = FreeCAD.Vector(SLICE_B_DIR)


# Import STL file
model_mesh = Mesh.read(MODEL)
box = model_mesh.BoundBox
model_mesh.translate(-box.XMin, -box.YMin, -box.ZMin)

box = model_mesh.BoundBox
scale_matrix = FreeCAD.Matrix()
scale_matrix.scale(MODEL_DIMS[0] / box.XMax,
                   MODEL_DIMS[1] / box.YMax,
                   MODEL_DIMS[2] / box.ZMax)
print scale_matrix
model_mesh.transform(scale_matrix)

# model_mesh is now normalized to the provided dimensions in the first octant

model_shape = Part.Shape()    # Make an empty shape to put the mesh into
model_shape.makeShapeFromMesh(model_mesh.Topology, 0.001)  # Tolerance hardcoded for now


doc = FreeCAD.activeDocument()
if doc is None:
    print("No active document! Exiting procedure")

# Cut cross-section
# slice accepts two arguments:
#+ the normal of the cross section plane
#+ the distance from the origin to the cross section plane.
# returns a list of wires

wiresA = []

for d in SLICES_A:
    slice_wires = model_shape.slice(slice_a_vec, d)
    wiresA.extend(slice_wires)

slice = doc.addObject("Part::Feature", "A_Wires")
slice.Shape = Part.Compound(wiresA)


wiresB = []

for d in SLICES_B:
    slice_wires = model_shape.slice(slice_b_vec, d)
    wiresB.extend(slice_wires)

part = doc.addObject("Part::Feature", "B_Wires")
part.Shape = Part.Compound(wiresB)

doc.recompute()
# Intersection btwn two slices in A and B planes has an intersection vector A
# (X) B.


# For each wire make a 2D slice shape.
# Then find intersection surfaces (new object? face+intersections)
# For each intersection surface, figure out where to actually cut
#
