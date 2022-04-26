import logging
from os import getenv

from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from misc import on_startup, on_shutdown


def custom_time(*args):
    return datetime.now(tz=ZoneInfo("Europe/Moscow")).timetuple()


logging.basicConfig(format='%(asctime)s:%(funcName)s:%(message)s', level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S")
logging.Formatter.converter = custom_time

admins = getenv("ADMINS").split() if getenv("ADMINS") else ''
admins.append(getenv("ADMIN"))

bot = Bot(token=getenv("BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

if __name__ == '__main__':
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
