include <BOSL2/std.scad>;

/**
 * Propeller Generator
 *      
 * Author: Jason Koolman  
 * Version: 1.1 (Modified to support dual pin holes)
 *
 * Description:
 * This OpenSCAD script generates fully parametric propellers with elliptical blades
 * using NACA 4-digit airfoil profiles. The propeller can have any number of blades,
 * and the blade geometry can be customized with various parameters including pitch,
 * sweep, and fairing.
 *
 * Based on the original work by Alex Matulich in 2022, found at:
 * - Thingiverse: https://tinyurl.com/zxybe5hc
 * - Printables: https://tinyurl.com/34rr4av4
 *
 * License:
 * This script is shared under the CC BY-NC-SA 4.0 license.
 * https://creativecommons.org/licenses/by-nc-sa/4.0/
 */

/* [❌️️️ Propeller] */

// Number of blades
Blades = 3;

// Propeller diameter (mm)
Diameter = 150;

// Rotation direction
Direction = -1; // [1: Clockwise, -1: Counterclockwise]

// Diameter where blade root starts
Root_Diameter = 14;

// Axial limit for the blade root chord (mm)
Root_Height = 8;

// Pitch in mm per revolution (-1 = auto)
Pitch = -1;

/* [🔪 Blade] */

// How chord width tapers along blade span
Chord_Mode = "ellipse"; // [ellipse: Ellipse, linear: Linear, constant: Uniform]

// Maximum chord fraction of blade length
Chord_Fraction = 0.15; // [0.05:0.01:0.8]

// Ellipse length factor for planform taper
Ellipse_Length = 1.1;  // [1.0:0.01:2]

// Centerline position along the chord for alignment (0 = LE, 1 = TE)
Centerline = 1.0; // [0:0.1:1]

// Fairing thickness to blend into hub
Fairing = 3;   

// Sweep in degrees per mm
Sweep = 0.0;

// Shift blades along axis
Offset = 0;

// Pitch at the blade tip (-1 = same as base pitch)
Pitch_Tip = -1; 

/* [🪶️️️ Airfoils] */

// 4-digit NACA airfoil at root
NACA_Root = 8430; // [0:9999]

// 4-digit NACA airfoil at mid
NACA_Mid = 6412; // [0:9999]

// 4-digit NACA airfoil at tip
NACA_Tip = 3412; // [0:9999]

// Where root blends into mid (fraction of blade length)
Transition_Point = 0.33; // [0:0.01:1]

// Thickness of trailing edge for printability
Trailing_Thickness = 0.4; // [0:0.05:1]

/* [🔩 Hub] */

// Extend hub length along axis
Hub_Extend = 2;

// Shaft type
Shaft_Type = "cylinder"; // [none: None, cylinder: Cylinder, keyway: Keyway, hex: Hex, D]

// Shaft diameter (or WAF for hex bores)
Shaft_Diameter = 5;

// Shaft depth (-1 = same as hub height)
Shaft_Depth = -1;

// Chamfer shaft edges
Shaft_Chamfer = 0.4;

// Override keyway size as [width, height]
Keyway_Size = [0, 0];

// Enable two side pin/mounting holes parallel to shaft
Pin_Holes = false;

// Distance from the center to each of the two pin holes (mm)
Pin_Holes_Distance = 5;

// Diameter of the pin holes (mm)
Pin_Holes_Diameter = 2;

/* [🛑️️️ Spinner] */

// Spinner type to add
Spinner = "none"; // [none: None, ogive: Ogive, parabolic: Parabolic]

// Place spinner on hub
Spinner_On_Hub = true;

// Spinner diameter (if not on hub)
Spinner_Diameter = 20;

// Spinner length
Spinner_Length = 20;

// Spinner nose rounding
Spinner_Rounding = 0.5; // [0:0.05:1]

/* [⭕️️️ Shroud] */

// Add a shroud (ring around blade tips)
Shroud = false;

// Offset from propeller diameter
Shroud_Offset = 0;

// Wall thickness of the ring
Shroud_Wall = 1.8;

// Length of the ring
Shroud_Length = 10;

// Edge chamfer for style
Shroud_Chamfer = 0.4;

/* [📷️️️ Render] */

// Number of points to generate for airfoils surfaces (0 = auto)
Points = 0;

// Number of blade slices (0 = auto)
Slices = 0;

// Color of the model
Color = "#E0E0E0"; // color

/* [Hidden] */

_Hub_Diameter = Root_Diameter;
_Hub_Length = Root_Height + Hub_Extend;
_Shiftout = 0.01;

$fa = 4;
$fs = 0.2;

// Render
color(Color) generate();

module generate() {
    difference() {
        union() {
            // Propeller
            up(Offset)
                propeller(
                    blades=Blades,
                    propdia=Diameter,
                    hubdia=Root_Diameter,
                    bladepitch=Pitch,
                    pitch_mode=Pitch_Tip < 0 ? "constant" : "linear",
                    pitch_tip=Pitch_Tip < 0 ? Pitch : Pitch_Tip,
                    maxchordfrac=Chord_Fraction,
                    hublen=Root_Height,
                    elenfrac=Ellipse_Length,
                    dir=Direction,
                    centerline=Centerline,
                    angle_sweep=Sweep,
                    te_thickness=Trailing_Thickness,
                    fairing=Fairing,
                    naca_root=NACA_Root,
                    naca_mid=NACA_Mid,
                    naca_tip=NACA_Tip,
                    root_transition=Transition_Point,
                    profilepoints=Points,
                    slices=Slices
                );

            // Hub
            cyl(d=_Hub_Diameter, l=_Hub_Length, anchor=BOTTOM);
            
            // Shroud
            if (Shroud) {
                shroud(
                    d=Diameter + Shroud_Offset,
                    wall=Shroud_Wall,
                    l=Shroud_Length,
                    chamfer=Shroud_Chamfer,
                    $fa = $fa/2
                );
            }
            
            // Spinner
            if (Spinner != "none") {
                spinner(
                    type=Spinner,
                    d=Spinner_Diameter,
                    l=Spinner_Length,
                    rounding=Spinner_Rounding
                );
            }
        }
        shaft();
        
        // Symmetrical pin holes parallel to shaft
        if (Pin_Holes) {
            h = (Shaft_Depth > 0 ? Shaft_Depth : _Hub_Length) + _Shiftout;
            up(h / 2) {
                translate([Pin_Holes_Distance, 0, 0])
                    cyl(d=Pin_Holes_Diameter, h=h);
                translate([-Pin_Holes_Distance, 0, 0])
                    cyl(d=Pin_Holes_Diameter, h=h);
            }
        }
    }
}

/**
 * Creates a propeller with N blades.
 *
 * See blade() for parameter explanations.
 */
module propeller(
    blades=2,
    propdia=100, hubdia=10, bladepitch=-1,
    maxchordfrac=0.15, hublen=10, elenfrac=1.1,
    dir=-1, centerline=1, angle_sweep=0,
    te_thickness=0.4, fairing=3,
    naca_root=9430, naca_mid=6412, naca_tip=4412,
    pitch_mode = "constant",
    pitch_tip = 100,
    root_transition=0.33,
    profilepoints=0, slices=0
) {
    assert(blades >= 1, "Propeller must have at least 1 blade.");
    assert(propdia > hubdia, "Propeller diameter must be greater than hub diameter.");
    
    rhub = hubdia/2;
    blength = propdia/2 - rhub;
    bpitch = bladepitch>=0 ? bladepitch : blength;
    esemimajor = elenfrac*blength;
    shift = hublen*(1-centerline);
    
    blade_vnf = blade(
        propdia=propdia,
        hubdia=hubdia,
        bladepitch=bladepitch,
        pitch_mode=pitch_mode,
        pitch_tip=pitch_tip,
        maxchordfrac=maxchordfrac,
        hublen=hublen,
        elenfrac=elenfrac,
        dir=dir,
        centerline=centerline,
        angle_sweep=angle_sweep,
        te_thickness=te_thickness,
        naca_root=naca_root,
        naca_mid=naca_mid,
        naca_tip=naca_tip,
        root_transition=root_transition,
        profilepoints=profilepoints,
        slices=slices,
        fairing=fairing
    );

    zrot_copies(n=blades)
        xrot(90)
            blade(blade_vnf, esemimajor, shift);
}

/**
 * Creates a single propeller blade and returns its VNF.
 */
function blade(
    propdia=100, hubdia=10, bladepitch=-1,
    maxchordfrac=0.15, hublen=10, elenfrac=1.1,
    dir=-1, centerline=0.3, angle_sweep=0,
    te_thickness=0.4, fairing=3,
    naca_root=9430, naca_mid=6412, naca_tip=3412,
    root_transition=0.33,
    pitch_mode = "constant",
    pitch_tip = 100,
    chord_mode = Chord_Mode,
    profilepoints=0, slices=0,
    anchor=CENTER, spin=0, orient=UP
) =
    let (
        root_params = naca_params(naca_root),
        mid_params  = naca_params(naca_mid),
        tip_params  = naca_params(naca_tip),

        rootcamber     = root_params[0],
        rootcamberpos  = root_params[1],
        rootthickness  = root_params[2],

        midcamber      = mid_params[0],
        midcamberpos   = mid_params[1],
        midthickness   = mid_params[2],

        tipcamber      = tip_params[0],
        tipcamberpos   = tip_params[1],
        tipthickness   = tip_params[2],

        rhub = hubdia/2,
        blength = propdia/2 - rhub,
        bpitch = bladepitch>=0 ? bladepitch : blength,
        esemimajor = elenfrac*blength,
        maxchordlen = 2*maxchordfrac*blength,
        hh = min(maxchordlen, hublen),
        ztrans = blength*root_transition,
        blen = blength - ztrans,
        slicelen = slices > 0 ? length/slices : 0.8,
        airfoilsegs = profilepoints > 0
            ? profilepoints
            : round(2*blength * maxchordfrac),
        fairingthick =
            fairing / _ellipse_d(maxchordlen, hh, -dir*atan(bpitch/(2*PI*rhub))),
        sweep = angle_sweep*sign(dir),
        
        root = ztrans > 0 ? [
            for (z = [0 : slicelen : max(0, ztrans - EPSILON)])
                let(
                    rz          = rhub + z,
                    interp      = sin(90*z/ztrans),
                    fthick      = _fairing_thickness(z, fairing, fairingthick),
                    thick       = lerp(rootthickness, midthickness, interp) + fthick,
                    cam         = lerp(rootcamber, midcamber, interp),
                    campos      = lerp(rootcamberpos, midcamberpos, interp),
                    attackangle = _attack_angle_r(
                      rz, dir, bpitch,
                      tspan = z / blength,
                      pitch_mode = pitch_mode,
                      pitch_tip = pitch_tip,
                    ),
                    elen        = maxchordlen * sqrt(max(0, 1 - (z*z)/(esemimajor*esemimajor))),
                    chordlen    = _chord_length(z, blength, maxchordlen, hh, attackangle, esemimajor, chord_mode)
                )
                airfoil_section3d(
                    naca_profile(airfoilsegs, cam, campos, thick, chordlen, centerline, dir, te_thickness),
                    rz, attackangle, sweep
                )
        ] : [],

        main = [
            for(bz = [0 : slicelen : blen + 0.9 * slicelen])
                let(
                    z           = min(bz,blen),
                    ze          = ztrans+z,
                    rz          = rhub+ze,
                    interp      = 1-cos(90*z/blen),
                    fthick      = _fairing_thickness(ze, fairing, fairingthick),
                    thick       = lerp(midthickness, tipthickness, interp) + fthick,
                    cam         = lerp(midcamber, tipcamber, interp),
                    campos      = lerp(midcamberpos, tipcamberpos, interp),
                    attackangle = _attack_angle_r(
                      rz, dir, bpitch,
                      tspan = (ztrans + z) / blength,
                      pitch_mode = pitch_mode,
                      pitch_tip = pitch_tip,
                    ),
                    chordlen    = _chord_length(ze, blength, maxchordlen, hh, attackangle, esemimajor, chord_mode)
                )
                airfoil_section3d(
                    naca_profile(airfoilsegs, cam, campos, thick, chordlen, centerline, dir, te_thickness),
                    rz, attackangle, sweep
                )
        ],

        shift = hublen*(1-centerline),
        vnf = vnf_vertex_array(
            points=[each root, each main],
            col_wrap=true,
            cap1=true,
            cap2=true,
            reverse=true
        )
    ) vnf;

module blade(vnf, esemimajor, shift, anchor=CENTER, spin=0, orient=UP) {
    attachable(anchor, spin, orient, vnf=vnf, axis=BACK, cp=[0,-shift,0]) {
        difference () {
            vnf_polyhedron(vnf);
            fwd(shift) cube([2*esemimajor+1, 10, 2*esemimajor+1], anchor=BACK);
        }
        children();
    }
}

function _ellipse_d(majaxis, minaxis, angle) =
    let (a=0.5*majaxis, b=0.5*minaxis, bc = b*cos(angle), as = a*sin(angle))
        2 * a * b / sqrt(bc*bc + as*as);

function _fairing_thickness(z, fairing, fairthickness) =
    fairing > 0 ? fairthickness * (1 - sin(90*min(1, z/fairing))) : 0;
    
function _attack_angle_r(
    r, dir, pitch, tspan,
    pitch_mode="constant",
    pitch_tip=undef
) =
    let(
        pt = is_undef(pitch_tip) ? pitch : pitch_tip,
        p  = (pitch_mode == "linear") ? (pitch + (pt - pitch) * tspan) : pitch,
    )
    -dir * atan(p / (2*PI*r));

function _chord_length(z, length, maxchord, hh, attackangle, esemimajor,mode="ellipse") =
    let(
        t = clamp(z/length, 0, 1),
        c =
            mode == "ellipse" ?
                maxchord * sqrt(max(0, 1 - (z*z)/(esemimajor*esemimajor))) :
            mode == "constant" ?
                maxchord :
            mode == "linear" ?
                lerp(maxchord, maxchord/2, t) :
            maxchord
    )
    _ellipse_d(c, hh, attackangle);

module shaft(height = Shaft_Depth > 0 ? Shaft_Depth : _Hub_Length, type = Shaft_Type, size = Shaft_Diameter, chamfer = Shaft_Chamfer, keyway_size = Keyway_Size) {
    h = height + _Shiftout;
    cb = -chamfer;
    ct = Shaft_Depth > 0 || (Spinner != "none" && Spinner_On_Hub == true) ? 0 : cb;

    up(height / 2 + _Shiftout / 2) {
        if (type == "cylinder") {
            cyl(d = size, h = h, chamfer1 = cb, chamfer2 = ct);
        } else if (type == "keyway") {
            kw_size = _keyway_size(size);
            kw_width = min(size, keyway_size.x > 0 ? keyway_size.x : kw_size.x);
            kw_height = min(kw_width, keyway_size.y > 0 ? keyway_size.y : kw_size.y);
            backing = size / 2;
            cyl(d = size, h = h, chamfer1 = cb, chamfer2 = ct);
            zrot(90)
                back(size / 2 + kw_height / 2 - backing / 2) 
                    cube([kw_width, kw_height + backing, h], center = true);
        } else if (type == "D") {
            flat_depth = size * 0.15;
            difference() {
                cyl(d = size, h = h, chamfer1 = cb, chamfer2 = ct);
                fwd(size / 2 - flat_depth / 2 + chamfer / 2) 
                    cube([size + chamfer * 2, flat_depth + chamfer, h], center = true);
            }
        } else if (type == "hex") {
            regular_prism(6, r = size / sqrt(3), h = h, chamfer1 = cb, chamfer2 = ct);
        }
    }

    function _keyway_size(diameter) =
        (diameter <= 6)  ? [2, 1.0] :
        (diameter <= 8)  ? [2, 1.2] :
        (diameter <= 10) ? [3, 1.4] :
        (diameter <= 12) ? [3, 1.8] :
        (diameter <= 17) ? [4, 2.3] :
        (diameter <= 22) ? [5, 2.8] :
        (diameter <= 30) ? [6, 3.3] :
        (diameter <= 38) ? [8, 3.3] :
        (diameter <= 44) ? [10, 4.3] :
        (diameter <= 50) ? [12, 4.3] :
        (diameter <= 58) ? [14, 4.9] :
        (diameter <= 65) ? [16, 5.4] :
        (diameter <= 75) ? [18, 6.4] :
        (diameter <= 85) ? [20, 6.4] :
        (diameter <= 95) ? [22, 7.4] :
        (diameter <= 110) ? [25, 8.4] :
        [25, 8.4];
}

module shroud(d, l, wall=2, chamfer=0) {
    tube(id = d, l = l, wall = wall, chamfer = chamfer, anchor=BOTTOM);
}

module spinner(type, d, l, rounding = 1, on_hub = Spinner_On_Hub, hub_d = _Hub_Diameter, hub_l = _Hub_Length) {
    diameter = on_hub ? min(d, hub_d) : d;

    up(on_hub ? hub_l : 0) {
        if (type == "parabolic") {
            parabolic_spinner(l=l, d=diameter, rounding=rounding);
        } else if (type == "ogive") {
            ogive_spinner(l=l, d=diameter, nose_r=rounding*0.24);
        }
    }
}

module parabolic_spinner(l=24, d=13, rounding=0.5) {
    r = d/2;
    exponent = rounding*1.5 + 0.5;
    p = [ [0,0], for(x=[0:0.05:1.001]) [ x*r, l*(1-pow(x, exponent)*pow(x, exponent)) ] ];
    rotate_extrude(angle=360) polygon(points=p);
}

module ogive_spinner(l=20, d=20, nose_r=0.20) {
    assert(nose_r < 0.25, "Nose radius must be less than 0.25.");

    rnose = nose_r*d;
    r = 0.5*d - rnose;
    ht = l-rnose;
    x = (ht*ht - r*r) / (2*r);
    circrad = x+r;
    astart = atan(ht/x);
    p = [[0,rnose], for(a=[astart:-0.05*astart:-0.001]) [ circrad*cos(a)-x, circrad*sin(a) ] ];
    
    rotate_extrude(angle=360) {
        difference() {
            offset(r=rnose) polygon(points=p);
            translate([-rnose-1,-1]) square(size=[rnose+1,l+2]);
            translate([-1,-rnose-1]) square(size=[r+2+rnose, rnose+1]);
        }
    }
}
    
function airfoil_section3d(p, r, attackangle=0, sweep=0) =
    let (
        n    = len(p) - 1,
        ca   = cos(attackangle), 
        sa   = sin(attackangle),
        rot  = [[ca, -sa], [sa, ca]],
        p2   = [ for (i=[0:n]) rot * p[i] ],
        ang0 = r * sweep,
        kdeg = (180/PI) / r
    )
    [ for (i=[0:n]) let(a = p2[i][0] * kdeg + ang0)
        [ r*sin(a), p2[i][1], r*cos(a) ]
    ];

function naca_params(code) = 
    assert(code >= 0 && code <= 9999, "NACA code must be between 0000 and 9999")
    [
        0.01*floor(code/1000),
        0.1 *(floor(code/100)%10),
        0.01*(code%100)
    ];

function naca_profile(n, M, P, T, chordlen=1, origin=0, dir=1, te_thick=0.2) =
    dir < 0 ?
    [
        for (x=[1.0:-1/n:0.1/n]) naca_lower_profile(x, M, P, T, chordlen, origin, dir, te_thick),
        for (x=[0:1/n:1-0.1/n]) naca_upper_profile(x, M, P, T, chordlen, origin, dir, te_thick),
        naca_upper_profile(1, M, P, T, chordlen, origin, dir, te_thick)
    ]
    : [
        for (x=[1.0:-1/n:0.1/n]) naca_upper_profile(x, M, P, T, chordlen, origin, dir, te_thick),
        for (x=[0:1/n:1-0.1/n]) naca_lower_profile(x, M, P, T, chordlen, origin, dir, te_thick),
        naca_lower_profile(1, M, P, T, chordlen, origin, dir, te_thick)
    ];

function naca_surface(x, M, P, T, chordlen=1, origin=0, dir=1, te_thick=0.2, s=1) =
    let(
        xp    = 0.5 * (1 - cos(180*x)),
        theta = atan(naca_gradient(xp, M, P)),
        yc    = naca_camber(xp, M, P),
        yt    = naca_thickness(xp, T),
        d     = (dir < 0 ? -1 : 1),
        org   = clamp(origin, 0, 1)
    )
    [ chordlen*d*(xp - s*yt*sin(theta) - org),
      chordlen*(yc + s*yt*cos(theta)) + s*xp*te_thick/2 ];

function naca_upper_profile(x, M, P, T, chordlen=1, origin=0, dir=1, te_thick=0.2) =
    naca_surface(x, M, P, T, chordlen, origin, dir, te_thick, 1);

function naca_lower_profile(x, M, P, T, chordlen=1, origin=0, dir=1, te_thick=0.2) =
    naca_surface(x, M, P, T, chordlen, origin, dir, te_thick, -1);

function naca_camber(x, M, P) =
    let (Pc = clamp(P, EPSILON, 1-EPSILON))
    (M == 0) ? 0
    : let(a = 2*Pc*x - x*x)
      (x < Pc ? M * a / (Pc*Pc)
              : M * (1 - 2*Pc + a) / ((1-Pc)*(1-Pc)));

function naca_gradient(x, M, P) =
    let (Pc = clamp(P, EPSILON, 1-EPSILON))
    (M == 0) ? 0
    : (2*M*(Pc - x)) / ((x < Pc ? Pc : (1-Pc)) * (x < Pc ? Pc : (1-Pc)));

function naca_thickness(x, T) =
    let(a0=0.2969, a1=-0.126, a2=-0.3516, a3=0.2843,
        a4=-0.1036, x2=x*x)
    5*T*(a0*sqrt(x) + a1*x + a2*x2 + a3*x2*x + a4*x2*x2);

function clamp(x, lo, hi) = max(lo, min(hi, x));
