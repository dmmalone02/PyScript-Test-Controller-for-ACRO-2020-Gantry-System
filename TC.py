import serial 
import time 

# Initialize serial port

ser = serial.Serial()
ser.baudrate = 115200 # Baud rate for BlackBox is 115200
ser.port = 'COM4'
ser.bytesize = 8
