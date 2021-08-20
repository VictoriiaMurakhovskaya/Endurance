import asyncio
import logging

import websockets

logging.basicConfig(level=logging.DEBUG)  # Change logging level to INFO/WARNING/ERROR when done with development.
logger = logging.getLogger(__name__)

WS_CONNECTION_URI = 'ws://webserver8.sms-timing.com:10015'
WS_CONNECTION_MESSAGE = 'START 19495@2gcircuit'


async def listen_timing(uri: str, message: str):
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
        while True:
            try:
                result = await asyncio.wait_for(websocket.recv(), timeout=2)
                logger.debug('Received: %s', result)
                # TODO: implement result handler.
            except Exception as e:
                logger.error('Something went wrong. Got an error: %s', e)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(
        listen_timing(WS_CONNECTION_URI, WS_CONNECTION_MESSAGE)
    )