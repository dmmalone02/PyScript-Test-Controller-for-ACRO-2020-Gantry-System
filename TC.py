import sys
import socketio  # type: ignore
import datetime
import time
import csv

sio = socketio.Client(logger=False, engineio_logger=False)

## Socket.io Decorator Functions 
is_connected = False
@sio.event 
def connect():
    print("Connected to OpenBuilds CONTROL") # Connection established
    is_connected = True


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
    time.sleep(20)

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

def bash_command():
    x, y, z = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
    cmd = (f'G0 X{x} Y{y} Z{z}')
    runCommand(cmd)

def dataOutput():
    with open('data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows()


# Main function to connect to the OpenBuilds CONTROL GUI and perform operations

def main():
    try:
        sio.connect('http://localhost:3000')  # Connecting to controller over port 3000
        
    except Exception as e:
        log(f"Exception: {e}" )
        
    time.sleep(2) 
    print("Status: Connection established successfully")
    bash_command()
    sio.wait()


if __name__ == "__main__":
    main()


