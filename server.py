import asyncio
from asyncio import StreamReader, StreamWriter

from loguru import logger

from config import settings


class Server:
    def __init__(self, host: str = settings.host, port: int = settings.port):
        self._host = host
        self._port = port

    async def listen(self):
        srv = await asyncio.start_server(
            self.client_connected,
            self._host,
            self._port,
        )

        logger.info(f'Server started: {self._host}:{self._port}')
        async with srv:
            await srv.serve_forever()

    async def client_connected(
        self, reader: StreamReader, writer: StreamWriter
    ):
        address = writer.get_extra_info('peername')
        logger.info(f'Client connected: {address}')

        while True:
            data = await reader.read(1024)
            logger.info(f'Received data: {data!r}')
            if not data:
                break

            writer.write(data)
            await writer.drain()

        logger.info(f'Client disconnected: {address}')
        writer.close()
