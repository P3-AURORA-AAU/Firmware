#CentralWebSocket
import asyncio
import subprocess
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import base64

app = FastAPI()

@app.websocket("/ws")
async def main(ws: WebSocket):
    await ws.access
    print('[ws] Client Connected')

    one = asyncio.create_task(recieve(ws))
    two = asyncio.create_task(send(ws))

    await one
    await two

async def recieve(ws: WebSocket):
    data = await ws.recieve_json()

    match data.type:
        case "move":
            move(data)
        case "turn":
            turn(data)
        case "sensor":
            sensor(data)
        case "stop":
            stop(data)

async def send(ws: WebSocket):
    async for frame in mjpeg_frame_generator(ffmpeg_proc):
        # Send the raw JPEG bytes as a binary WebSocket message
        ffmpeg_proc = start_ffmpeg(width=1280, height=720, fps=60, quality=5)

        await ws.send_json({"type": "camera_data", "data": {"image": base64.b64encode(frame).decode("ascii")}})
    

async def mjpeg_frame_generator(proc: subprocess.Popen):
    """
    Reads the stdout of the FFmpeg process and yields each JPEG frame.
    MJPEG frames are delimited by the JPEG SOI (0xFFD8) and EOI (0xFFD9) markers.
    """
    buffer = b""
    while True:
        # Read a chunk – 4096 bytes is a reasonable size
        chunk = await asyncio.to_thread(proc.stdout.read, 4096)
        if not chunk:
            # EOF – FFmpeg terminated unexpectedly
            break
        buffer += chunk

        # Extract all complete JPEGs from the buffer
        while True:
            start = buffer.find(b"\xff\xd8")  # SOI
            end = buffer.find(b"\xff\xd9")    # EOI
            if start != -1 and end != -1 and end > start:
                # Include the EOI marker (+2 bytes)
                jpeg = buffer[start : end + 2]
                yield jpeg
                # Remove the consumed bytes from the buffer
                buffer = buffer[end + 2 :]
            else:
                # Not enough data for a full frame yet
                break

def start_ffmpeg(
    device: str = "/dev/video0",
    width: int = 640,
    height: int = 480,
    fps: int = 60,
    quality: int = 5,          # 2‑31 (lower = better quality) for MJPEG
) -> subprocess.Popen:
    """
    Returns a Popen object whose stdout yields a raw MJPEG byte stream.
    """
    cmd = [
        "ffmpeg",
        "-f", "v4l2",                     # input format
        "-framerate", str(fps),
        "-video_size", f"{width}x{height}",
        "-i", device,
        "-c:v", "mjpeg",                # force MJPEG output
        "-q:v", str(quality),             # quality (2‑31, 2 = best)
       "-f", "mjpeg",                    # output container
        "pipe:1",                          # write to stdout
    ]

    # Start FFmpeg, pipe only stdout (stderr goes to console for debugging)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=0,                      # unbuffered – we want frames ASAP
    )
    return proc