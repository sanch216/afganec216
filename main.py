from dotenv import load_dotenv
import os

import logging

import asyncio
from aiogram import Bot, Dispatcher, F
from msg_handlers import storage
load_dotenv()
API = os.getenv("tg_api")
bot = Bot(API)
dp = Dispatcher(storage=storage)


async def main() -> None:
    from msg_handlers import router
    from app.handlers import router_voice
    dp.include_router(router)
    dp.include_router(router_voice)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')