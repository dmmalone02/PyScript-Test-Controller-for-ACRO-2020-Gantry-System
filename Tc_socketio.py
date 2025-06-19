import socketio
import datetime
import time

# Server => User
# Client => OpenBuilds CONTROL

# Instantiate Socket.io Client
sio = socketio.Client()

# Confirmation for good connection to GRBL through OpenBuilds CONTROL
@sio.event 
def connect():
    print("Connected to OpenBuilds CONTROL")
    sio.emit('command', 'G0 X10 Y10 F1000')
# Function to send a single command to the BlackBox Controller
def send_command(cmd):
    print("Sending g-code commands: " + str(cmd))
    sio.emit('command', cmd)
# Function to send multiple commands to the BlackBox Controller
def job(cmds):
    for i in cmds:
        send_command(i)
        time.sleep(0.5)
      

@sio.event
def disconnect(reason):
    print("Disconnected from Openbuilds CONTROL! reason:", reason)
    
@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.on('serial')
def handle_serial(data):
    if data.strip() in ("ok",""):
        return
    log("📡 Serial: " + str(data))

@sio.on('status')
def handle_status(data):
    state = data.get('machine', {}).get('modals', {}).get('spindlestate')
    position = data.get('machine', {}).get('position', {}).get('work')
    if state or position:
        log(f"🔄 State: {state} | Position: X={position['x']:.2f}, Y={position['y']:.2f}")

@sio.on('alarm')
def handle_alarm(data):
    print("Alarm:", data)

# Time log for events
def log(msg):
    print(f"[{datetime.datetime.now()}] {msg}")


cmds = [
    'G21',      # Set units to mm
    'G90',      # Set absolute positioning
    '$H',       # Home the machine
    'G92 X0 Y0 Z0',  # Set current position as zero (optional, for your workflow)
]


try:
    sio.connect('http://localhost:3000')  # Connecting to controller over port 3000 using WebSockets
    sio.wait()
except Exception as e:
    log(f"Exception: {e}" )
