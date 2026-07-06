"""Receive updates via webhook instead of long polling.

Bale sends each update as an HTTPS POST to your ``setWebhook`` URL. Here we use
a tiny aiohttp server (aiohttp is already a baleio dependency) to receive them.

    export BALE_TOKEN=123456:xxxxxxxx
    python examples/webhook_bot.py
    # then: await bot.set_webhook("https://your-domain/webhook")
"""
from __future__ import annotations

import os

from aiohttp import web

from baleio import Bot, Dispatcher
from baleio.filters import CommandStart
from baleio.types import Message, Update

dp = Dispatcher()
bot = Bot(os.environ.get("BALE_TOKEN", "123456:placeholder-token-value"))


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer("سلام از طریق وبهوک 👋")


async def handle_webhook(request: web.Request) -> web.Response:
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return web.Response()


def build_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    return app


if __name__ == "__main__":
    web.run_app(build_app(), host="0.0.0.0", port=8080)
