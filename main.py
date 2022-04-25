import logging
from os import getenv

from aiogram import Bot, Dispatcher, executor, types

from misc import on_startup, on_shutdown
from misc.func import custom_time

logging.basicConfig(format='%(asctime)s:%(funcName)s:%(message)s', level=logging.INFO)
logging.Formatter.converter = custom_time

bot = Bot(token=getenv("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

if __name__ == '__main__':
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
