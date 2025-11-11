# API specsheet pi-mcu
date    11/11/2025
author  @lynet_101
version 1

# Overview
Language    C++
env         Bare metal
com         UART (custom)
pins        D1, D2

# Sensors
IMU [accellerometer, gyroscope, ML-core]
Moist
Temp
Pressure

---

# UART calls
## 00 | General
Arduino will by default respond with ACK. If ack not recieved within 2000ms, instruction will be retransmitted. if transmittion fails 5 times, a reset and handshake is initialised. if handshake fails OR transmission keeps failing after successfull handshake, an error is thrown

## 00.1 | Emergency stop
In case of emergency stop, the reset pin will be pulled high

## 01 | Set Speed
desc: sets the speed (duh)
byte: 0x61
request format: 2bit speed integer
00: 0
01: 50
10: 100
11: invalid

## 02 | Set Dir
angle cannot go above 180, other than 360 for backwards
byte: 0x62
request format: 9-bit signed integer
0: forward
360: backward
inbetweens and negatives: turn the decired angle

## 03 | Sensor request
byte: 0x63
request: 3-bit integer
1: accellerometer
2: gyroscope
3: moist
4: temp
5: pressure
return: data

# MCU scheme
## 01
Store speed in local variable

# 02
Calculate the desired rotation based on curent angle z-axis then turn x-amount of degrees based on gyroscope feedback 

when turning is completed if speed > 0, return to forward or backward motion. If speed = 0, do nothing

at bootup, and after completed turn, angular zeroing is to be performed

/* turn
slow: 100% 50%
medium: 100% 0%
fast: 100% -50%
super: 100% -100%

only slow keeps you moving */

prefered when speed 0: medium
prefered when speed > 0: slow

if angle > 130: super
if angle > 50 u < 130: fast