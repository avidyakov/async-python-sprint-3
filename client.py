import asyncio
from asyncio import StreamReader, StreamWriter

import click
from aioconsole import ainput, aprint

PROMPT = 'You: '


async def read(reader: StreamReader) -> None:
    while data := await reader.readline():
        await aprint(f'\r{data.decode()}{PROMPT}', end='')


async def write(username: str, writer: StreamWriter) -> None:
    while True:
        if data := (await ainput(PROMPT)).strip():
            writer.write(f'{username}: {data}\n'.encode())
            await writer.drain()


async def main(username: str, host: str, port: str) -> None:
    reader, writer = await asyncio.open_connection(host, port)
    writer.write(f'{username}\n'.encode())
    await asyncio.gather(write(username, writer), read(reader))


@click.command()
@click.option('-u', '--username', required=True)
@click.option('-h', '--host', default='0.0.0.0')
@click.option('-p', '--port', default='8080')
def client(**kwargs):
    asyncio.run(main(**kwargs))


if __name__ == '__main__':
    client()
