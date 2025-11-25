# CentralWebSocket – fixed version
# -------------------------------------------------
# Requirements:
#   pip install fastapi uvicorn[standard] python-multipart
#   ffmpeg must be installed and accessible in $PATH
# -------------------------------------------------

import asyncio
import base64
import subprocess
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


# ----------------------------------------------------------------------
# Helper: start the ffmpeg process that streams raw MJPEG frames
# ----------------------------------------------------------------------
def start_ffmpeg(
    device: str = "/dev/video0",
    width: int = 640,
    height: int = 480,
    fps: int = 60,
    quality: int = 5,  # 2‑31 (lower = higher quality) for MJPEG
) -> subprocess.Popen:
    """
    Launches ffmpeg and returns a Popen object whose stdout yields a raw MJPEG byte stream.
    """
    cmd = [
        "ffmpeg",
        "-f", "v4l2",                     # input format (Linux V4L2)
        "-framerate", str(fps),
        "-video_size", f"{width}x{height}",
        "-i", device,
        "-c:v", "mjpeg",                  # force MJPEG output
        "-q:v", str(quality),             # quality (2‑31, 2 = best)
        "-f", "mjpeg",                    # output container
        "pipe:1",                         # write to stdout
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=0,                        # unbuffered – we want frames ASAP
    )
    return proc


# ----------------------------------------------------------------------
# Async generator: split the raw MJPEG stream into individual JPEG frames
# ----------------------------------------------------------------------
async def mjpeg_frame_generator(proc: subprocess.Popen) -> AsyncGenerator[bytes, None]:
    """
    Reads the stdout of the FFmpeg process and yields each JPEG frame.
    MJPEG frames are delimited by the JPEG SOI (0xFFD8) and EOI (0xFFD9) markers.
    """
    buffer = b""

    while True:
        # Read a chunk – 4096 bytes is a reasonable size.
        chunk = await asyncio.to_thread(proc.stdout.read, 4096)
        if not chunk:
            # EOF – FFmpeg terminated unexpectedly.
            break

        buffer += chunk

        # Extract all complete JPEGs from the buffer.
        while True:
            start = buffer.find(b"\xff\xd8")  # SOI
            end = buffer.find(b"\xff\xd9")    # EOI
            if start != -1 and end != -1 and end > start:
                # Include the EOI marker (+2 bytes).
                jpeg = buffer[start : end + 2]
                yield jpeg
                # Remove the consumed bytes from the buffer.
                buffer = buffer[end + 2 :]
            else:
                # Not enough data for a full frame yet.
                break


# ----------------------------------------------------------------------
# Command handlers – replace these with your actual logic
# ----------------------------------------------------------------------
def move(payload: dict):
    print("MOVE:", payload)


def turn(payload: dict):
    print("TURN:", payload)


def sensor(payload: dict):
    print("SENSOR:", payload)


def stop(payload: dict):
    print("STOP:", payload)


# ----------------------------------------------------------------------
# Receive side – parses incoming JSON commands
# ----------------------------------------------------------------------
async def receive(ws: WebSocket):
    try:
        while True:
            data = await ws.receive_json()
            cmd_type = data.get("type")
            match cmd_type:
                case "move":
                    move(data)
                case "turn":
                    turn(data)
                case "sensor":
                    sensor(data)
                case "stop":
                    stop(data)
                case _:
                    print(f"Unknown command: {cmd_type}")
    except WebSocketDisconnect:
        print("[ws] Client disconnected (receive loop)")


# ----------------------------------------------------------------------
# Send side – streams camera frames back to the client
# ----------------------------------------------------------------------
async def send(ws: WebSocket):
    ffmpeg_proc = start_ffmpeg(width=1280, height=720, fps=60, quality=5)

    try:
        async for frame in mjpeg_frame_generator(ffmpeg_proc):
            payload = {
                "type": "camera_data",
                "data": {"image": base64.b64encode(frame).decode("ascii")},
            }
            await ws.send_json(payload)
    finally:
        ffmpeg_proc.terminate()
        ffmpeg_proc.wait()
        print("[ws] FFmpeg stopped")


# ----------------------------------------------------------------------
# WebSocket endpoint – launches both send and receive coroutines
# ----------------------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("[ws] Client connected")

    # Run receive and send concurrently.
    receive_task = asyncio.create_task(receive(ws))
    send_task = asyncio.create_task(send(ws))

    # Wait for either side to finish (e.g., client disconnects).
    done, pending = await asyncio.wait(
        {receive_task, send_task},
        return_when=asyncio.FIRST_COMPLETED,
    )

    # Cancel whatever is still running.
    for task in pending:
        task.cancel()
    print("[ws] Connection closed")