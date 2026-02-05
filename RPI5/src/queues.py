import asyncio


class Queues:
    def __init__(self):
        self.send_queue = asyncio.Queue()
        self.jetbot_send_queue = asyncio.Queue()
        self.camera_queue = asyncio.Queue()

queues = Queues()
