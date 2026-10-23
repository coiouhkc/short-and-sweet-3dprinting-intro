# Examples

## OpenSCAD

```scad
//
// PARAMETRIC L-BRACKET
// Units: millimeters
//

$fn = 64;  // Smoothness of circular holes

// ========================================
// PARAMETERS - CHANGE THESE VALUES
// ========================================

// Overall dimensions
bracket_width  = 50;  // Width along X
base_length    = 40;  // Horizontal base length
upright_height = 50;  // Vertical wall height

// Material thickness
thickness = 5;

// Mounting holes
holes_enabled = true;
hole_diameter = 5.5;
edge_offset   = 10;

// Number of holes along each plate
base_holes_x  = 2;
base_holes_y  = 1;
wall_holes_x  = 2;
wall_holes_z  = 2;

// Reinforcement
gussets_enabled = true;
gusset_thickness = 5;
gusset_size = 20;

// ========================================
// MODEL
// ========================================

difference() {
    union() {

        // Horizontal base plate
        cube([
            bracket_width,
            base_length,
            thickness
        ]);

        // Vertical mounting plate
        translate([
            0,
            0,
            thickness
        ])
        cube([
            bracket_width,
            thickness,
            upright_height
        ]);

        // Left reinforcement gusset
        if (gussets_enabled)
            gusset();

        // Right reinforcement gusset
        if (gussets_enabled)
            translate([
                bracket_width - gusset_thickness,
                0,
                0
            ])
            gusset();
    }

    // ====================================
    // HOLES IN HORIZONTAL BASE
    // ====================================

    if (holes_enabled) {

        for (i = [0 : base_holes_x - 1]) {
            for (j = [0 : base_holes_y - 1]) {

                x_pos =
                    bracket_width / 2
                    + (i - (base_holes_x - 1) / 2)
                    * (bracket_width - 2 * edge_offset)
                    / max(base_holes_x - 1, 1);

                y_pos =
                    thickness + edge_offset
                    + j * (
                        base_length
                        - thickness
                        - 2 * edge_offset
                    ) / max(base_holes_y - 1, 1);

                translate([
                    x_pos,
                    y_pos,
                    -1
                ])
                cylinder(
                    h = thickness + 2,
                    d = hole_diameter
                );
            }
        }

        // ====================================
        // HOLES IN VERTICAL WALL
        // ====================================

        for (i = [0 : wall_holes_x - 1]) {
            for (j = [0 : wall_holes_z - 1]) {

                x_pos =
                    bracket_width / 2
                    + (i - (wall_holes_x - 1) / 2)
                    * (bracket_width - 2 * edge_offset)
                    / max(wall_holes_x - 1, 1);

                z_pos =
                    thickness + edge_offset
                    + j * (
                        upright_height
                        - 2 * edge_offset
                    ) / max(wall_holes_z - 1, 1);

                translate([
                    x_pos,
                    -1,
                    z_pos
                ])
                rotate([90, 0, 0])
                cylinder(
                    h = thickness + 2,
                    d = hole_diameter
                );
            }
        }
    }
}

// ========================================
// GUSSET MODULE
// ========================================

module gusset() {

    // Right triangular reinforcement
    // Extruded across the Y-Z plane

    translate([0, thickness, thickness])
    rotate([90, 0, 90])
    linear_extrude(
        height = gusset_thickness
    )
    polygon(points = [
        [0, 0],
        [gusset_size, 0],
        [0, gusset_size]
    ]);
}

```

## G-Code

```
; Example G-code for a 20x20x20 mm cube
; Generic Cartesian FDM printer
; NOTE: Illustrative example, not a complete, ready-to-print file.

; --- Initialization ---
G21                 ; Use millimeters
G90                 ; Absolute positioning
M82                 ; Absolute extrusion mode
M104 S200            ; Set nozzle temperature to 200 C
M140 S60             ; Set bed temperature to 60 C
M190 S60             ; Wait for bed to reach temperature
M109 S200            ; Wait for nozzle to reach temperature

; --- Homing ---
G28                  ; Home all axes

; --- Prepare for printing ---
G1 Z0.2 F300         ; Move to first layer height
G1 X10 Y10 F3000     ; Move to starting position
G92 E0               ; Reset extrusion distance

; --- First layer: outline of cube ---
G1 X30 Y10 E0.8 F1200
G1 X30 Y30 E1.6
G1 X10 Y30 E2.4
G1 X10 Y10 E3.2

; --- Second layer ---
G1 Z0.4 F300
G1 X30 Y10 E4.0 F1200
G1 X30 Y30 E4.8
G1 X10 Y30 E5.6
G1 X10 Y10 E6.4

; --- Third layer ---
G1 Z0.6 F300
G1 X30 Y10 E7.2 F1200
G1 X30 Y30 E8.0
G1 X10 Y30 E8.8
G1 X10 Y10 E9.6

; Additional layers would continue in the same way,
; increasing Z by 0.2 mm each layer until Z = 20.0 mm.

; --- Finish ---
M104 S0              ; Turn off nozzle heater
M140 S0              ; Turn off bed heater
G1 Z25 F300          ; Raise nozzle
G28 X Y              ; Home X and Y axes
M84                  ; Disable motors
```