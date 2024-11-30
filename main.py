from config import  API

import logging

import asyncio
from aiogram import Bot, Dispatcher, F
from app.handlers import storage



bot = Bot(API)
dp = Dispatcher(storage=storage)


async def main() -> None:
    from app.handlers import router
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')