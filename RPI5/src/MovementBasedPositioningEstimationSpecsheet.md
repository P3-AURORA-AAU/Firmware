>>       Movement Based Positioning Estimation       <<
>> Sebastian Lindau-Skands | VoxVoltera - 07/02/2026 <<

---

> Constants
wheel rpm: 41
wheel Ø: 40.5cm
estimated speed: 0.995KM/h
time for 90 degree turn: 0/8 seconds
time for 'move forward 1': 0.72 seconds
cell_size: 0.2m
grid_size: variable

---

> Notes
Turning logic has been hardcoded in firmware, such that every `turn {dir}` automatically turns 90 degrees.
Movement logic has been hardcoded in firmware, such that every `move {dir}` automatically moves exactly one cell
one can only move straight, or turn in place
Start position is ALWAYS at (0,0) ori=0
coordinates and orientation are to be kept in array [x, y, ori]

---

> orientation
when (turn right) {0 > 90 > 180 > 270 > 0}
when (turn left) {0 > 270 > 180 > 90 > 0}

> coordinate
when (ori = 0) {inc x}
when (ori = 90) {inc y}
when (ori = 180) {dec x}
when (ori = 270) {dec y}

constraints: 0<x<=grid_size, 0<y<=grid_size, 0<ori<=270

---