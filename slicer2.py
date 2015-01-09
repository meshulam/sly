































import math
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
slice_a_vec = FreeCAD.Vector(SLICE_A_DIR).normalize()
slice_b_vec = FreeCAD.Vector(SLICE_B_DIR).normalize()
ab_intersection = slice_a_vec.cross(slice_b_vec).normalize()

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


facesA = []

for d in SLICES_A:
    slice_wires = model_shape.slice(slice_a_vec, d)
    for wire in slice_wires:
        face = Part.Face(wire)
        facesA.append(face)

facesB = []

for d in SLICES_B:
    slice_wires = model_shape.slice(slice_b_vec, d)
    for wire in slice_wires:
        facesB.append(Part.Face(wire))

print("Created {} A faces and {} B faces".format(len(facesA), len(facesB)))



def getSliceEdges(face, face_normal, slice_normal, slice_distance):
    norm = FreeCAD.Vector(0, 0, 1)
    dist_vec = slice_normal * slice_distance
    box = Part.makeBox(100, 100, 1e-6,
                        FreeCAD.Vector(-50, -50, 0))
    place = FreeCAD.Placement(dist_vec, FreeCAD.Rotation(norm, slice_normal))
    box.transformShape(place.toMatrix())
    overlap = face.common(box)
    
    slice_dir = face_normal.cross(slice_normal)
    slices = []
    print("Intersection has {} faces".format(len(overlap.Faces)))
    for overlap_face in overlap.Faces:
        print("Face has {} edges".format(len(overlap_face.Edges)))
        for edge in overlap_face.Edges:
            dir = edgeToVector(edge)
            angle = dir.getAngle(ab_intersection)
            print("Angle from desired: "+str(angle))
            if isParallelAngle(angle):
                slices.append(edge)
                break

    return slices

def sliceFromEdge(edge, thickness, slice_normal):
    extrusion = edge.extrude(slice_normal * thickness)
    extrusion.translate(slice_normal * (-thickness/2))    # Center the face on the edge
    return extrusion

def isParallelAngle(rads):
    degrees = rads * 180/math.pi
    epsilon = 0.5    # Half a degree is close enough
    return degrees % 180 < epsilon or degrees % 180 > 180-epsilon

def edgeToVector(edge):
    (pt0, pt1) = edge.Vertexes

    return FreeCAD.Vector(pt1.X - pt0.X, 
                          pt1.Y - pt0.Y, 
                          pt1.Z - pt0.Z)

def cutHalf(edge, up_dir, top=True):
    """Return a collinear edge that's half as long as the input.
    if top=True, return the top half. else, the bottom half."""
    (p0, p1) = edge.Vertexes
    midpoint = Part.Vertex((p1.X + p0.X)/2, 
                           (p1.Y + p0.Y)/2,
                           (p1.Z + p0.Z)/2)
    top_first = edgeToVector(edge).dot(up_dir) < 0
    if top_first == top:    
        return Part.Edge(p0, midpoint) 
    else:
        return Part.Edge(midpoint, p1)

def cut_face(face, face_normal, slice_normal, slice_distances, cut_top=True):
    intersection_dir = face_normal.cross(slice_normal)
    cut_edges = []
    for dist in slice_distances:
        cut_edges.extend(getSliceEdges(face, face_normal, 
                                       slice_normal, dist))

    cut_shape = face
    for edge in cut_edges:
        line = cutHalf(edge, intersection_dir, cut_top)
        cutout = sliceFromEdge(line, THICKNESS, slice_normal)
        cut_shape = cut_shape.cut(cutout)
    return cut_shape


for face in facesA:
    out = cut_face(face, slice_a_vec, slice_b_vec, SLICES_B)
    Part.show(out)

for face in facesB:
    out = cut_face(face, slice_b_vec, slice_a_vec, SLICES_A)
    Part.show(out)

#face = facesB[8]
#Part.show(face)
#edges = getSliceEdges(face, slice_b_vec, slice_a_vec, 30)
#for edge in edges:
#    line = cutHalf(edge, ab_intersection, False)
#    cutout = sliceFromEdge(line, THICKNESS, slice_a_vec)
#    cut_shape = cut_shape.cut(cutout)
#    Part.show(cutHalf(edge, ab_intersection, False))










































