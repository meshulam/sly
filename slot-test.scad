use <scad-utils/morphology.scad>
use <scad-utils/transformations.scad>


/******** Model params *********/
MODEL_FILE = "/Users/matt/Dropbox/art/Coffee table/attempt3-lines2.stl";
MODEL_DIMENSIONS = [48, 24, 18];   // Resize the model to a bounding box of this size


/******** Slicing params *******/
THICKNESS = 0.25;       // Material thickness

NORMAL_A = [0, 1, 0];       // Normal vector for the 'A' cross section plane
SLICES_A = [-3, -1, 0, 2, 3];   // Distance from origin along NORMAL_A to 
//SLICES_A = [8, 10];
                            //create cross sections
NORMAL_B = [-1, 0, 0];
SLICES_B = [-3, -1];


//$fa = 4;
//$fs = 0.1;


/******** Mode configuration *****/
// 0: Display assembled slices
// 1: Arrange 2-D shapes on XY plane for export

MODE = 0;


/****************************************
 *********  Application logic ***********
 ****************************************/

if (MODE == 0) {
    assemble_model();
//    bisect(NORMAL_A, 0);
    %model();
} else {
    layout_model();
}


module assemble_model() {
    for (dist = SLICES_A) {
        bisect(NORMAL_A, dist);
    }
    
    for (distb = SLICES_B) bisect(NORMAL_B, distb);
}

module layout_model() {
    
}



/*** Lower level functions and modules below here ***/

module model() {
    resize(MODEL_DIMENSIONS) import(MODEL_FILE, convexity=10);
}


module bisect(normal = [0, 0, 1], d = 0) {
    xvec_calc = cross([0, 0, 1], normal);
    ang = acos(dot(normal, [0, 0, 1]) / norm(normal));
    xvec = ang == 0 ? [0, 0, 1] : xvec_calc;
    
    echo("xvec: ", xvec, "Ang: ", ang);
    rotate(a=-ang, v=xvec)
      translate([0, 0, d])
        linear_extrude(height=THICKNESS, center=true) 
          projection(cut=true) 
            translate([0, 0, -d]) 
              rotate(a=ang, v=xvec) 
                model();

}


module all_B() {
    for(slice = slices_B) {
        bisect(normal=direction_B, pt=bslice);
    }
}

module xor() {
    echo("xor children: ", $children);
    difference() {
        children(0);
        children(1);  // TODO: subtract full cutting plane, not just the cross section
        // cufrently we're getting a non-simple object
    }
    difference() {
        children(1);
        children(0);
    }
/*    difference() {
        union() { children([0:1]); }
        intersection() { children([0:1]); }
    }*/
}


function dot(a, b) = a[0]*b[0] + a[1]*b[1] + a[2]*b[2];