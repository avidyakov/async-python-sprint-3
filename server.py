from collections import deque
from functools import partial
from operator import ne

from aiohttp import web
from loguru import logger

clients: dict[str, list[web.WebSocketResponse]] = {}
messages: deque[str] = deque(maxlen=20)
routes = web.RouteTableDef()


@routes.get('/chats')
async def chat(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    username = request.query['username']
    clients.setdefault(username, []).append(ws)
    logger.info(f'Client {username} connected')

    for msg in messages:
        await _send_a_message_to_client(msg, username)

    async for msg in ws:
        if msg.data == 'exit':
            clients[username].remove(ws)
            await ws.close()
            logger.info(f'Client {username} disconnected')
        else:
            new = f'{username}: {msg.data}'
            messages.append(new)
            await _send_a_message_to_clients(new, username)

    return ws


async def _send_a_message_to_clients(new: str, username: str) -> None:
    for receiver in filter(partial(ne, username), clients):
        await _send_a_message_to_client(new, receiver)


async def _send_a_message_to_client(new: str, receiver: str) -> None:
    for socket in clients[receiver]:
        await socket.send_str(new)


def main():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)


if __name__ == '__main__':
    main()
