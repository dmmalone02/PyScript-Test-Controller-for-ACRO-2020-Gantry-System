import socketio 
import datetime
import time


sio = socketio.Client(logger=False, engineio_logger=False)

## Socket.io Decorator Functions ##
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

       
@sio.on('status')  # Retrieve machine position and state
def handle_status(data):
    machine = data.get('machine', {})
    state = machine.get('activeState') or machine.get('modals', {}).get('spindlestate', 'Unknown')
    position = machine.get('position', {}).get('work')  

    
    if position:    # Write state and position to external text file
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

#-----------------------------------------------------------------------------------------------------------#

# Time logger function
def log(msg):
    print(f"[{datetime.datetime.now()}] {msg}")

# Function to send a single command to the BlackBox Controller
def send_command(cmd):
    sio.call('data', {'data': cmd}, timeout=10) # Added timeout to see if the server is even receiving anything
    log(f"Sent: {cmd}")
    
# Set zero
def set_zero():
    send_command('$J=G91G21Y100F5000')
    time.sleep(2)
    log("Zeroing complete")

# We can try uploading a G-code file to the OpenBuildsCONTROL GUI and see if it will open and run it
def gcode_file_upload(gfile):
    with open(gfile, 'r') as f:
        gcode = f.read()
        sio.emit('api', {'fileContent':gcode})
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
    set_zero()
    print("status: coordinates set to zero")
   # gfile = 'gfile.gcode'
    #gcode_file_upload(gfile)
    sio.wait()
main()
