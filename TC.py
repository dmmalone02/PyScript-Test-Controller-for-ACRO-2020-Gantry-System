import sys
import socketio  # type: ignore
import datetime
import time
import csv
import numpy as np # type: ignore
import subprocess
import os
import re

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

@sio.on('status')  # Retrieve machine position and state
def handle_status(data):
    machine = data.get('machine', {})
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

            with open('data.csv', 'w') as f:
                f.write(f"[{datetime.datetime.now()}] Position: X={x:.2f}, Y={y:.2f}, Z={z:.2f}\n")
        except (TypeError, ValueError) as e:
            print(f"[ERROR] Failed to parse position: {e}")
    else:
        print(f"[{datetime.datetime.now()}] Position: Unknown")


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


def gridJob():
    # Set total space size
    limitX = 1850
    limitY = 1850

    print("Enter grid size:")
    print(f"Maximum space is {limitX}x{limitY} units (X x Y).")
    try:
        grid_size_x = int(input("Grid size X: "))
        grid_size_y = int(input("Grid size Y: "))
        if grid_size_x <= 0 or grid_size_y <= 0:
            raise ValueError("Grid dimensions must be positive integers.")
    except ValueError as e:
        print(f"Invalid grid size. {e}")
        return None

    # Create grid and compute size of each cell in units
    grid_size = (grid_size_x + 1, grid_size_y +1)
    cell_width = limitX / (grid_size_x + 1)
    cell_height = limitY / (grid_size_y + 1)
    cell_height = limitY / grid_size_y
    matrix = np.zeros(grid_size, dtype=int) # Create a matrix to store the grid values (initiallly with zeros)

    # Get start position
    print("Enter start position (grid coordinates):")
    try:
        start_x = int(input("Start X (grid): "))
        start_y = int(input("Start Y (grid): "))
        if not (0 <= start_x < grid_size_x) or not (0 <= start_y < grid_size_y):
            raise ValueError("Start position out of bounds.")
    except ValueError as e:
        print(f"Invalid start position. {e}")
        return None

    start_position = (start_x, start_y)

    # Get end position
    print("Enter end position (grid coordinates):")
    try:
        end_x = int(input("End X (grid): "))
        end_y = int(input("End Y (grid): "))
        if not (0 <= end_x < grid_size_x) or not (0 <= end_y < grid_size_y):
            raise ValueError("End position out of bounds.")
    except ValueError as e:
        print(f"Invalid end position. {e}")
        return None

    end_position = (end_x, end_y)

    # Generate coordinate mapping for each cell
    coordinate_map = np.empty(grid_size, dtype=object)
    for i in range(grid_size_x):
        for j in range(grid_size_y):
            x_coord = round(i * cell_width, 2)
            y_coord = round(j * cell_height, 2)
            coordinate_map[i, j] = (x_coord, y_coord)
            #runJob(f"G0 X{x_coord} Y{y_coord}\n")
            time.sleep(30)

    return grid_size, start_position, end_position, matrix, coordinate_map   


def rssi_collection():
    # Default parameter 
    node_id = "171" 
    iterations = 10
    username = "ucanlab"
    network = 2
    positions = [ (185,0), (370,0), (555, 0), (740, 0) ]

    # Output file and matching pattern from bash output (regex)
    output_csv = os.path.expanduser("~/rssi_collection.csv")
    rssi_pattern = re.compile(r"\b(\d+)\s+(-\d+)\s*dBm", re.MULTILINE)


    # Empty matrix to store the extracted datas
    data = []
    
    for x,y in positions: 
        cmd = [ "bash", "test.sh", "-l", node_id, "-k", str(iterations), "-n", str(network), "-u", username ]

        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0: 
            print(f" Error at ({x},{y}): {result.stderr.strip()}")

        matches = rssi_pattern.findall(result.stdout)

        rssi_values = []
        
        for node,rssi in matches:
            if node == node_id:
                rssi_values.append(int(rssi))

        data.append([x, y, rssi_values])

    print(matches)

    header = ["X", "Y", "Pi"]
    with open(output_csv, "w", newline="") as file: 
        writer = csv.writer(file)

        writer.writerow(header)
        for row in data: 
            writer.writerow([row[0], row[1], row[2]])


def display_menu():
    print("\n=== Main Menu ===")
    print("1. Home machine")
    print("2. Set origin (zero)")
    print("3. Define grid")
    print("4. Run full sweep")
    print("5. Exit")

def home_machine():
    print(">> Sending homing command...")
    runCommand("$H")  # Home all axes
    print(">> Homing command sent. Waiting for completion...")
    time.sleep(10)  # Wait for homing to complete
    print(">> Homing completed successfully.")

def set_origin():
    print(">> Setting origin to current position...")
    set_all_zero()  # Set all axes to zero
    print(">> Origin set to current position.")

def define_grid():
    gridJob()
    c = input("Run RSSI sweep? (y/n): ")
    if c.lower() == 'y':
        print(">> Running RSSI sweep...")
        rssi_collection()  # Collect RSSI data




def run_sweep():
    print(">> Running RSSI sweep...")
    rssi_collection(grid_x, grid_y)

def menu():
    while True:
        display_menu()
        time.sleep(1)
        choice = input("Enter your choice: ")

        if choice == "1":
            home_machine()
        elif choice == "2":
            set_origin()
        elif choice == "3":
            define_grid()
        elif choice == "4":
            run_sweep()
        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")
        


# Main function to connect to the OpenBuilds CONTROL GUI and perform operations

def setup():
    try:
        sio.connect('http://localhost:3000')  # Connecting to controller over port 3000
        
    except Exception as e:
        log(f"Exception: {e}" )
        
    time.sleep(2) 
    print("Status: Connection established successfully")
    time.sleep(1)
    print("Status: Homing all axes...")
    runCommand("$H")  # Home all axes
    time.sleep(10)  # Wait for homing to complete
    print("Status: Homing completed")
    time.sleep(2)


if __name__ == "__main__":
    setup()
    print("Welcome to the OpenBuilds CONTROL Python Client V1.01!")
    print("You can run commands, jobs, or set axes to zero externally to control gantry")
    print("You can also specify grid points in coordinate space and have gantry collect RSSI values at each point.")
    try:
        a = input("Press Enter to continue or type 'exit' to quit: ")
        if a.lower() == 'exit':
            print("Exiting...")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Exiting...")
    menu()
    

    
    
 
    
    if result:
        grid_size, start_position, end_position, matrix, coordinate_map = result

        print("\nGrid created with size:", grid_size)
        print("Start position (grid):", start_position)
        print("End position (grid):", end_position)
        print("\nStart real-world coordinates:", coordinate_map[start_position])
        print("End real-world coordinates:", coordinate_map[end_position])
        print("\nExample of coordinate map [i][j] = (x, y):")
        for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                print(f"[{i}][{j}] -> {coordinate_map[i][j]}")
            print()  # Newline between rows
    
    sio.wait()       

