import asyncio



class QueueManager:
    def __init__(self):
        self.create_channel_queue = asyncio.Queue()
        self.set_channel_username_queue = asyncio.Queue()
        self.set_channel_description_queue = asyncio.Queue()
        self.set_channel_photo_queue = asyncio.Queue()





queue_manager = QueueManager()