import sys
import socketio  # type: ignore
import datetime
import time
import PythonSample
from NatNetClient import NatNetClient
import threading


sio = socketio.Client(logger=False, engineio_logger=False)

## Socket.io Decorator Functions 
@sio.event 
def connect():
    print("Connected to OpenBuilds CONTROL") # Connection established

@sio.event
def disconnect(reason):
    print("\nDisconnected from Openbuilds CONTROL! reason:", reason)  # Disconnection detected
    
@sio.event
def connect_error(data):
    print("The connection failed!") # Failed connection
   
@sio.on('*')
def catch_all(event, data):
    if not event.startswith('sysinfo'): # Ignore recurring system info messages
        time.sleep(2)
        log(f"Recieved event: {event} with data: {data} \n")      

#ADD: if user wants machine and position state to be outputted, enter yes, otherwise the output will be muted

@sio.on('status')  # Retrieve machine position and state
def handle_status(data):
    machine = data.get('machine', {})
    state = machine.get('activeState') or machine.get('modals', {}).get('spindlestate', 'Unknown')
    position = machine.get('position', {}).get('work')  

    if position:    # Write state and position to external text file to monitor changes
                    # Ensure position values are floats, defaulting to 0.0 if not present
                    # and handle any potential parsing errors
                    # Position is in millimeters
                    # Use datetime to log the time of the state and position
        try:
            x = float(position.get('x', 0.0))
            y = float(position.get('y', 0.0))
            z = float(position.get('z', 0.0))
            
            with open('output.txt', 'w') as f:
                f.write(f"[{datetime.datetime.now()}] State: {state} | Position: X={x:.2f}, Y={y:.2f}, Z={z:.2f}\n")
        except (TypeError, ValueError) as e:
            print(f"[ERROR] Failed to parse position: {e}")
    else:
        print(f"[{datetime.datetime.now()}] State: {state} | Position: Unknown")


# From https://builds.openbuilds.com/threads/reading-values-from-openbuilds-control-software.15867/
#socket.emit("runJob", {
    #data = "G1 .... gcode block with \n linebreaks etc",
    #isJob = true, // if isjob==true, it gets stored and can be retrieved when the UI restart/refreshes, use for actual jobs, for quick little tasks, set to false
    #completedMsg = "String you want to print in control in a popup on completion"
#});

# Time logger function using datetime
def log(msg):
    print(f"[{datetime.datetime.now()}] {msg}")

# Function to send a single command to the BlackBox Controller
def runCommand(cmd):
    sio.emit('runCommand', cmd)
    log(f"Sent: {cmd}")
    time.sleep(5)

# Function to run a job 
def runJob(cmd):
    sio.emit('runJob', {
        "data": cmd + "\n",
        "isJob": False,  # Set to True if this is a job that should be stored
        "completedMsg": "Command executed successfully"
    })
    log(f"Job sent: {cmd}")

# Set an individual axis to zero
def setToZero(axis):
    if axis == 'x':
        axis = {"data": "G10 L20 P1 X0\n",
         "isJob": False,
        "completedMsg": "X-axis set to zero"
        }
    elif axis == 'y':
        axis = {"data": "G10 L20 P1 Y0\n",
         "isJob": False,
        "completedMsg": "X-axis set to zero"
        }
    elif axis == 'z':   
        axis = {"data": "G10 L20 P1 Z0\n",
         "isJob": False,
        "completedMsg": "X-axis set to zero"
        }
    else:
         print(f"Invalid axis: {axis}")
         print("Valid axes are: x, y, z")
    sio.emit('runJob', axis)
    log(f"Set {axis} axis to zero")
        
    time.sleep(3)
    log(f"Set {axis} axis to zero")

# Set all axes to zero
def set_all_zero():
    sio.emit("runJob", {
        "data": "G10 L20 P1 X0 Y0 Z0\n",
        "isJob": False,
        "completedMsg": "Axes set to zero"
    })
    log("All axes set to zero")
    print("status: all axes set to zero")
    time.sleep(5)

# Go to zero point
def goto_zero():
    sio.emit("runJob", {
        "data": "G0 X0 Y0 Z0\n",
        "isJob": False,
        "completedMsg": "Machine returned to zero"
    })
    log("Sent move to zero (G0 X0 Y0 Z0)")
    print("status: moved to zero point")
    time.sleep(10)



### OptiTrack NatNet Streaming ###


# From PythonSample.py line 172
def my_parse_args(arg_list, args_dict):
    # set up base values
    arg_list_len = len(arg_list)
    if arg_list_len > 1:
        args_dict["serverAddress"] = arg_list[1]
        if arg_list_len > 2:
            args_dict["clientAddress"] = arg_list[2]
        if arg_list_len > 3:
            if len(arg_list[3]):
                args_dict["use_multicast"] = True
                if arg_list[3][0].upper() == "U":
                    args_dict["use_multicast"] = False
        if arg_list_len > 4:
            args_dict["stream_type"] = arg_list[4]
    return args_dict


def MoCap_Client():
    ask = input('Use OptiTrack Motion Capture software? [Y/N]')
    if ask == 'y':
        # Set these to appropiate parameters
        optionsDict = {}
        optionsDict["clientAddress"] = "XXX.X.X.X"
        optionsDict["serverAddress"] = "YYY.Y.Y.Y"
        optionsDict["use_multicast"] = None
        optionsDict["stream_type"] = None

        # This will create a new NatNet client
        optionsDict = my_parse_args(sys.argv, optionsDict)
        streaming_client = NatNetClient()
        streaming_client.set_client_address(optionsDict["clientAddress"])
        streaming_client.set_server_address(optionsDict["serverAddress"])
        if streaming_client.connected() is True:
            print("Client connection succesful\n")
            PythonSample.print_configuration(streaming_client)
            PythonSample.print_commands()
            run = input('Begin datastream? [Y/N]\n')
            if run == 'y':
                streaming_client.run()
        else:
            return("Could not connect properly")

    

# Main function to connect to the OpenBuilds CONTROL GUI and perform operations
def main():
    try:
        sio.connect('http://localhost:3000')  # Connecting to controller over port 3000
        
    except Exception as e:
        log(f"Exception: {e}" )
        
    time.sleep(2) 
    print("status: connected")
    time.sleep(10)
    print("status: setting to zero")
    set_all_zero()  
    goto_zero()
    print("status: machine in idle state")
    runCommand("G0 X10 Y10 Z10")  # Example command to move the machine
    MoCap_Client()
    sio.wait()

main()
