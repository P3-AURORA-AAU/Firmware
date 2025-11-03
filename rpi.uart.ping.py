#!/usr/bin/env python3
"""
uart_ping.py – Sends a “PING” packet and waits for a “PONG” reply.
Run this on the “client” side of the UART link.
"""

import sys
import time
import serial

UART_PORT = "/dev/ttyAMA0"   # adjust if you use a different device
BAUDRATE  = 9600
TIMEOUT   = 2                # seconds to wait for a reply

PING_PKT = b'\x50\x49\x4E\x47'   # "PING"
PONG_PKT = b'\x50\x4F\x4E\x47'   # "PONG"

def main() -> None:
    try:
        ser = serial.Serial(port=UART_PORT,
                            baudrate=BAUDRATE,
                            timeout=TIMEOUT)
    except serial.SerialException as exc:
        sys.stderr.write(f"❌ Cannot open {UART_PORT}: {exc}\n")
        sys.exit(1)

    print(f"🔄 Starting ping‑pong test on {UART_PORT} @ {BAUDRATE} baud")
    counter = 0

    try:
        while True:
            # 1️⃣ Send PING
            ser.write(PING_PKT)
            ser.flush()
            print(f"[{counter}] ➜ Sent PING")

            # 2️⃣ Wait for PONG (exact 4‑byte response)
            reply = ser.read(len(PONG_PKT))

            if reply == PONG_PKT:
                print(f"[{counter}] ✅ Received correct PONG")
            elif reply:
                print(f"[{counter}] ⚠️ Received unexpected data: {reply.hex()}")
            else:
                print(f"[{counter}] ⏱️ Timeout – no reply")

            counter += 1
            time.sleep(1)   # pause a second between rounds
    except KeyboardInterrupt:
        print("\n🛑 Ping loop stopped by user")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
