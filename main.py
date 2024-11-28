from config import  API

import logging

import asyncio
from aiogram import Bot, Dispatcher, F , types


bot = Bot(API)
dp = Dispatcher()


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