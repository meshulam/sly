use <scad-utils/morphology.scad>
use <scad-utils/transformations.scad>


/**
===========

Successful run:

Module cache size: 7 modules
Compiling design (CSG Tree generation)...
Compiling design (CSG Products generation)...
Geometry Cache insert: import(file="../Coffee table/attempt3-li (14208 bytes)
Geometry Cache hit: import(file="../Coffee table/attempt3-li (14208 bytes)
Geometry Cache insert: multmatrix([[1,0,0,0],[0,0.0174524,-0.99 (14208 bytes)
Geometry Cache insert: projection(cut=true,convexity=0){multmat (1104 bytes)
Geometry Cache hit: import(file="../Coffee table/attempt3-li (14208 bytes)
Geometries in cache: 3



========
Failed run (a=90, v=[1, 0, 0])



Module cache size: 7 modules
Compiling design (CSG Tree generation)...
Compiling design (CSG Products generation)...
Geometry Cache insert: import(file="../Coffee table/attempt3-li (14208 bytes)
Geometry Cache hit: import(file="../Coffee table/attempt3-li (14208 bytes)
Geometry Cache insert: multmatrix([[1,0,0,0],[0,6.12323e-17,-1, (14208 bytes)
ERROR: CGAL error in CGALUtils::project during bigbox intersection: CGAL ERROR: assertion violation! Expr: cet->get_index() == ce->twin()->get_index() File: /Users/matt/code/openscad/../libraries/install/include/CGAL/Nef_3/SNC_external_structure.h Line: 1169
WARNING: projection() failed.
Geometry Cache insert: projection(cut=true,convexity=0){multmat (0 bytes)
Geometry Cache hit: import(file="../Coffee table/attempt3-li (14208 bytes)
Geometries in cache: 3



Geometry Cache insert: multmatrix([[1,0,0,0],[0,1,0,0],[0,0,1,0 (14208 bytes)
ERROR: CGAL error in CGALUtils::project during bigbox intersection: CGAL ERROR: assertion violation! Expr: cet->get_index() == ce->twin()->get_index() File: /Users/matt/code/openscad/../libraries/install/include/CGAL/Nef_3/SNC_external_structure.h Line: 1169
WARNING: projection() failed.
Geometry Cache insert: projection(cut=true,convexity=0){multmat (0 bytes)

**/

/******** Model params *********/
MODEL_FILE = "/Users/matt/Dropbox/art/Coffee table/attempt3-lines2.stl";
THICKNESS = 0.5;


//rotate(a=-90, v=[-1, 0, 0])
projection(cut=true) 
  rotate(a=90, v=[1, 0, 0]) 
    import(MODEL_FILE, convexity=10);
                
                
%import(MODEL_FILE, convexity=10);