import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from db import Database
from middlewares import BlockCheckMiddleware
import admin as admin_handlers
import user as user_handlers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=None))
dp = Dispatcher()
db = Database()


async def main():
    await db.connect()

    dp["db"] = db

    block_mw = BlockCheckMiddleware(db)
    dp.message.middleware(block_mw)
    dp.callback_query.middleware(block_mw)

    dp.include_router(admin_handlers.public_router)
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    async def expire_ads():
        while True:
            try:
                await db.expire_paid_channels()
            except Exception:
                logging.exception("Reklama muddati tekshiruvida xato")
            await asyncio.sleep(300)

    expiry_task = asyncio.create_task(expire_ads())
    print("Bot ishga tushdi...")
    try:
        await dp.start_polling(bot)
    finally:
        expiry_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
