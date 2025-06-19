import serial 
import time 


# Initialize serial port
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=3)
ser.flushInput()

# Wait for the GRBL to reset and initialize
print("Waiting for GRBL to initialize...")
ser.write(b'\r\n\r\n')
time.sleep(2)

startup_lines = []
start_time = time.time()
while time.time() - start_time < 3:
    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            startup_lines.append(line)
    time.sleep(0.5)
print(f"GRBL startup messages: {startup_lines}")
ser.flushInput()

ser.write(b'$X\n')
time.sleep(0.2)
while ser.in_waiting:
    print("Unlock:", ser.readline().decode('utf-8', errors='ignore').strip())

# G-code input commands
def send_gcode(commands):
    print("Sending g-code commands: " + str(commands))
    time.sleep(2)
    print("\nExecuting job...")
    for command in commands:
        line = command.strip() + '\n'
        ser.write(line.encode('utf-8'))
        time.sleep(1)
        # Wait for response from GRBL with a timeout
        start_time = time.time()
        responses = []
        while time.time() - start_time < 2:
            while ser.in_waiting:
                response = ser.readline().decode('utf-8').strip()
                if response:
                    responses.append(response)
            if responses:
                break
            time.sleep(0.05)
        print(f"Sent: {command} | Response(s): {responses}")
        for response in responses:
            if "ALARM" in response:
                print("Alarm detected, sending unlock ($X)...")
                ser.write(b'$X\n')
                time.sleep(0.1)
                unlock_response = ser.readline().decode('utf-8').strip()
                print(f"Unlock response: {unlock_response}")
    ser.close()



gcode_commands = [
    'G21',      # Set units to mm
    'G90',      # Set absolute positioning
    '$H',       # Home the machine
    'G92 X0 Y0 Z0',  # Set current position as zero (optional, for your workflow)
]

send_gcode(gcode_commands)

print("\nJob completed successfully")




