import logging

from os import getenv

from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)
bot = Bot(token=getenv("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

if __name__ == '__main__':
    from handlers import dp

    executor.start_polling(dp, skip_updates=True)
