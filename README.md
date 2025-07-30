# PyScript-Test-Controller-for-ACRO-2020-Gantry-System

A Python client that is able to send commands to the BlackBox controller and interact with the OpenBuilds CONTROL GUI.The connection is established through the use of the Socket.io library that enables real-time bidirectional event-based communication between a client and a server.

The purpose of this script is to be able to control the OpenBuilds ACRO 2020 Gantry System through an external controller. It will act as a main controller to all of the additional components that will be added to the system. Eventually, we plan to implement an OptiTrack motion capture system to aquire locational data, and we would like it to be able to be controlled through this same python script such that we have everything in one place.

## Built using:
- python-socketio (https://python-socketio.readthedocs.io/en/stable/intro.html#what-is-socket-io)
- OpenBuilds CONTROL (https://github.com/OpenBuilds/OpenBuilds-CONTROL/blob/master/index.js#L2234)
- GRBL Firmware (https://github.com/grbl/grbl)

## Functionality
- Monitor system status
- Monitor position of gantry and output to text file
- Recieve responses directly from GRBL (type, response)
- Send g-code commands to CONTROL to be executed by machine

<details>
<summary>G-Code Command List</summary>

-- in progress--
### G0,G1: Linear Motions (G0 for non-extrusion movements)
G
G1 
### G2: Clockwise Arc
G2 
### G3: Counter-clockwise Arc
G3 
### G10 L2, G10 L20: Set Work Coordinate Offsets
### G17, G18,G19: Plane Selection
### G20: Set inch Units, 
### G21: Set milimeter Units
### G28,G30: go to Pre-Defined Position
### G28.1, G30.1: Set Pre-Defined Position
### G38.2: Probing
### G53: Move in Absolute Coordinates
### G54, G55, G56, G57, G58, G59: Work Coordinate Systems
### G61: Path Control Modes
### G80: Motion Mode Cancel
### G90, G91: Distance Modes
### G91.1: Arc IJK Distance Modes
### G92: Coordinate Offset
### G92.1 Clear Coordinate system Offsets
### G93, G94: Feedrate modes
### M0, M2, M30: Program Pause and End
### M3, M4, M5: Spindle Control
### M7, M8, M9: Coolant Control
### M56: Parking Motion Override Control
</details>


# From https://builds.openbuilds.com/threads/reading-values-from-openbuilds-control-software.15867/
#socket.emit("runJob", {
    #data = "G1 .... gcode block with \n linebreaks etc",
    #isJob = true, // if isjob==true, it gets stored and can be retrieved when the UI restart/refreshes, use for actual jobs, for quick little tasks, set to false
    #completedMsg = "String you want to print in control in a popup on completion"
#});
