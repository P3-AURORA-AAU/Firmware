# API specsheet pi-mcu
time 26/09/2025
author: @lynet_101
version: 0.1

# Overview
Language: C
env: bare metal
com: UART
pins: 0, 1

# sensors
- gyroscope
- ultrasonic

# Movement scheme
## CMD: Emergency stop
byte: 0x00
request_format: none
desc: stops all actions, if com is lost to rpi, or 0x00 is sent
example: AA 00 AC
example2: no connection
mode: continue op till next op recieved

## CMD: Drive
byte: 0x01
request_format: [dir]
desc: drives forwards or backwards
example: AA 01 AC (drive)
example2: AA 00 AC (don't drive)
example3: AA 03 AC (drive backwards)
mode: continue op till next op recieved

## CMD: sensor request
byte: 0x02
request_format: none
response_format: [angle], [distance_sensor_1], [distance_sensor_2]
desc: dumps all sensor data to uart
example: AA 02 AC
mode: async

## CMD: Turn
byte: 0x03
request_format: [angle]
desc: turns specified angle (without moving forward). clockwise incrementation, each inc = ~10 degrees
example: AA 03 05 (turn 50 degrees)
mode: async

# Internals
## Drive
max angel: 50
if angel < 50:
	drive
else:
	return 3
	return angle sensor
	drive backwards
if 01:
    wire config 1
    relay: state1
if 02:
    wire config 2
    relay: state1
if 00:
    relay: state 0

## sensor request
for sensor in sensors
	return sensor

## turn
if angel > 30:
	return 3
	reverse

    pwm [formula] on 4 motors
    change of individual wire config
    togle of individual relays

# Wire configs
relay will be connected with pole on motor, throws on battery
t1t2 on - = no movement (00)
t1 - t2 + = forward (01)
t1 + t2 - = backwards (02)
t1 + t2 + = NEVER EVER EVER DO THIS EVER!!!!!

# return codes
general_error - 0
OK - 1
bad request - 2
movement error - 3
404 - 4
sensor error - 5
