# PyScript-Test-Controller-for-ACRO-2020-Gantry-System
An external Python script that is able to send commands to the Blackbox and assign jobs to the gantry device. Communication trhough serial port (Pyserial) in order to send g-code commands from text string input to binary data at input of BlackBox controller.

Two Versions:

1] Using PySerial to link through USB Connection, sending commands via serial port
2] Utilizing Socket.io as a WebSocket API to communicate with OpenBuilds CONTROL GUI
    - Interfacing with CONTROL GUI
    - Automatic GRBL Handling
    - Can use both GUI and script simultaneously



################################
##### G- Code Command List #####
################################

# See https://linuxcnc.org/docs/html/gcode.html for G-code Quick Reference 
# Full command list: https://marlinfw.org/meta/gcode/ and functionality

    # G0,G1: Linear Motions (G0 for non-extrusion movements)
    # ----------->  G1 [A<pos>] [B<pos>] [C<pos>] [E<pos>] [F<rate>] [S<power>] [U<pos>] [V<pos>] [W<pos>] [X<pos>] [Y<pos>] [Z<pos>]
    # G2: Clockwise Arc
    # -----------> G2 [A<pos>] [B<pos>] [C<pos>] [E<pos>] [F<rate>] I<offset> J<offset> [P<count>] R<radius> [S<power>] [U<pos>] [V<pos>] [W<pos>] [X<pos>] [Y<pos>] [Z<pos>]
    # G3: Counter-clockwise Arc
    # -----------> G3 [A<pos>] [B<pos>] [C<pos>] [E<pos>] [F<rate>] I<offset> J<offset> [P<count>] R<radius> [S<power>] [U<pos>] [V<pos>] [W<pos>] [X<pos>] [Y<pos>] [Z<pos>]
    # G4: Dwell - pauses comand queue and waits for a period of time
    # -----------> G4 [P<time(ms)>] [S<time(sec)>]
    # G10 L2, G10 L20: Set Work Coordinate Offsets
    # G17, G18,G19: Plane Selection
    # G20: Set inch Units, 
    # G21: Set milimeter Units
    # G28,G30: go to Pre-Defined Position
    # G28.1, G30.1: Set Pre-Defined Position
    # G38.2: Probing
    # G53: Move in Absolute Coordinates
    # G54, G55, G56, G57, G58, G59: Work Coordinate Systems
    # G61: Path Control Modes
    # G80: Motion Mode Cancel
    # G90, G91: Distance Modes
    # G91.1: Arc IJK Distance Modes
    # G92: Coordinate Offset
    # G92.1 Clear Coordinate system Offsets
    # G93, G94: Feedrate modes
    # M0, M2, M30: Program Pause and End
    # M3, M4, M5: Spindle Control
    # M7, M8, M9: Coolant Control
    # M56: Parking Motion Override Control

