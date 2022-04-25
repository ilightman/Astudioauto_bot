import logging
from os import getenv

from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime
from zoneinfo import ZoneInfo

from misc import on_startup, on_shutdown


def custom_time(*args):
        return datetime.now(tz=ZoneInfo("Europe/Moscow")).timetuple()


logging.basicConfig(format='%(asctime)s:%(funcName)s:%(message)s', level=logging.INFO)
logging.Formatter.converter = custom_time

bot = Bot(token=getenv("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

if __name__ == '__main__':
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
