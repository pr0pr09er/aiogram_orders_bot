import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import common, first_option, second_option, third_option, authorize

admin_ids = [855836749]


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token='6839431790:AAHaQObyxjNkZrakKJfJGzMLCyIc6lc4Fd4')

    dp.include_router(common.router)
    dp.include_router(first_option.router)
    dp.include_router(second_option.router)
    dp.include_router(third_option.router)
    dp.include_router(authorize.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
