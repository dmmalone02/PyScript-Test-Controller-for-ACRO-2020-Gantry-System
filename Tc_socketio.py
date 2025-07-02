import socketio  # type: ignore
import datetime
import time


sio = socketio.Client(logger=False, engineio_logger=False)

## Socket.io Decorator Functions 
@sio.event 
def connect():
    print("Connected to OpenBuilds CONTROL") # Connection established

@sio.event
def disconnect(reason):
    print("\nDisconnected from Openbuilds CONTROL! reason:", reason)  # Disconnecttion detected
    
@sio.event
def connect_error(data):
    print("The connection failed!") # Failed connection
   
@sio.on('*')
def catch_all(event, data):
    if not event.startswith('sysinfo'):
        time.sleep(2)
        log(f"Recieved event: {event} with data: {data} \n")

@sio.on('serial')
def handle_serial(data):
    log(f"Grbl: {data}")       

@sio.on('status')  # Retrieve machine position and state
def handle_status(data):
    machine = data.get('machine', {})
    state = machine.get('activeState') or machine.get('modals', {}).get('spindlestate', 'Unknown')
    position = machine.get('position', {}).get('work')  

    
    if position:    # Write state and position to external text file to monitor changes
                    # Ensure position values are floats, defaulting to 0.0 if not present
                    # and handle any potential parsing errors
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



# Time logger function using datetime
def log(msg):
    print(f"[{datetime.datetime.now()}] {msg}")

# Function to send a single command to the BlackBox Controller
def send_command(type, cmd):
    sio.emit('runCommand', cmd)
    log(f"Sent: {cmd}")

# Set an individual axis to zero
def setToZero(axis):
    sio.emit('setToZero', axis)
    time.sleep(0.1)
    log(f"Set {axis} axis to zero")

# Set all axes to zero
def set_all_zero():
    setToZero('x')
    setToZero('y')
    setToZero('z')
    log("All axes set to zero")

# Go to zero point
def goto_zero():
    sio.emit('gotoZero')
    time.sleep(5)
    log("Machine moved to zero point")

# Uploading a G-code file to the OpenBuildsCONTROL GUI for multiple movements
def file_upload(gfile):
    with open(gfile, 'r') as f:
        gcode = f.read()
        sio.emit('', {'fileContent':gcode})
        log(f"Sent G-code file: {gfile}")


def main():
    try:
        sio.connect('http://localhost:3000')  # Connecting to controller over port 3000
        
    except Exception as e:
        log(f"Exception: {e}" )
        
    time.sleep(2) 
    print("status: connected")
    time.sleep(10)
    print("status: setting to zero")
    set_all_zero()  # Set all axes to zero
    time.sleep(2)
    print("status: coordinates set to zero")
    time.sleep(10) # After cooridinates are set to zero, move to a random point in CONTROL GUI
    goto_zero()
    time.sleep(2)
    print("status: moved to zero point")
    time.sleep(1)
    print("status: machine in idle state")
    sio.wait()

main()
