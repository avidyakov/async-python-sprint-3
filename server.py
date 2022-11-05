import asyncio
from asyncio.streams import StreamReader, StreamWriter
from collections import deque
from functools import partial
from operator import ne

import click
from loguru import logger

clients: dict[str, list[StreamWriter]] = {}
messages: deque[bytes] = deque(maxlen=20)


async def client_connected(reader: StreamReader, writer: StreamWriter) -> None:
    username = (await reader.readline()).decode().strip()
    logger.info(f'Start serving {username}')
    clients.setdefault(username, []).append(writer)

    for msg in messages:
        await write_data(writer, msg)

    while data := await reader.readline():
        messages.append(data)

        for receiver in filter(partial(ne, username), clients):
            for writer in clients[receiver]:
                await write_data(writer, messages[-1])

    logger.info(f'Stop serving {username}')
    clients[username].remove(writer)
    writer.close()


async def write_data(writer: StreamWriter, data: bytes) -> None:
    writer.write(data)
    await writer.drain()


async def main(host: str, port: int) -> None:
    srv = await asyncio.start_server(client_connected, host, port)

    async with srv:
        await srv.serve_forever()


@click.command()
@click.option('-h', '--host', default='0.0.0.0')
@click.option('-p', '--port', default='8080')
def server(**kwargs) -> None:
    asyncio.run(main(**kwargs))


if __name__ == '__main__':
    server()
