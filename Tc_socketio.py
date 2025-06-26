import socketio 
import datetime
import time


sio = socketio.Client(logger=False, engineio_logger=False)

@sio.event 
def connect():
    print("Connected to OpenBuilds CONTROL")
    
@sio.event
def disconnect(reason):
    print("\nDisconnected from Openbuilds CONTROL! reason:", reason)
    
@sio.event
def connect_error(data):
    print("The connection failed!")
   
@sio.on('console')
def handle_serial(data):
    line = str(data).strip()
    print("Console: " + line)

@sio.on('*')
def catch_all(event, data):
    time.sleep(2)
    log(f"Recieved event: {event} with data: {data} \n")

@sio.on('status')
def handle_status(data):
    machine = data.get('machine', {})
    state = machine.get('activeState') or machine.get('modals', {}).get('spindlestate', 'Unknown')
    position = machine.get('position', {}).get('work')  

    # Write state and position to external text file
    if position:
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

# Time logger function
def log(msg):
    print(f"[{datetime.datetime.now()}] {msg}")

# Function to send a single command to the BlackBox Controller
def send_command(cmd):
    sio.emit('gcode', {'code': cmd})
    log(f"Sent: {cmd}")

# Send object to limit switches and set as origin
def set_zero():
    send_command('G28')
    time.sleep(10)
    send_command('')

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
        sio.wait()
    except Exception as e:
        log(f"Exception: {e}" )
    gfile = 'gfile.gcode'
    time.sleep(5)
    gcode_file_upload(gfile)

main()
