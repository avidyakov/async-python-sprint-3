import asyncio

import aiohttp
import click
from aioconsole import ainput, aprint

PROMPT = 'You: '


async def read(ws):
    async for msg in ws:
        await aprint(f'\r{msg.data}\n{PROMPT}', end='')


async def write(ws):
    while True:
        raw = await ainput(PROMPT)
        msg = raw.strip()

        if msg:
            await ws.send_str(msg)

        if msg == 'exit':
            await ws.close()
            break


async def main(username, host, port):
    session = aiohttp.ClientSession(raise_for_status=True)
    url = f'http://{host}:{port}/chats?username={username}'

    async with session.ws_connect(url) as ws:
        await asyncio.gather(write(ws), read(ws))


@click.command()
@click.option('-u', '--username', required=True)
@click.option('-h', '--host', default='0.0.0.0')
@click.option('-p', '--port', default='8080')
def client(username, host, port):
    asyncio.run(main(username, host, port))


if __name__ == '__main__':
    client()
