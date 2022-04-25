import logging
import datetime
from os import getenv
from zoneinfo import ZoneInfo

from aiogram import Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from misc.price_download import _download_to_io_upload_yadisk


async def price_download_scheduler(dp: Dispatcher, scheduler: AsyncIOScheduler):
    cur_time = datetime.datetime.now(tz=ZoneInfo('Europe/Moscow')).time()
    start_time = (datetime.time(hour=9), datetime.time(hour=12))
    if cur_time > start_time[0]:
        scheduler.add_job(_download_to_io_upload_yadisk, args=(dp,), timezone=ZoneInfo('Europe/Moscow'))
        if cur_time < start_time[1]:
            scheduler.add_job(_download_to_io_upload_yadisk, "cron", day_of_week='mon-sun',
                              hour=12, minute=10, args=(dp,), timezone=ZoneInfo('Europe/Moscow'))
    elif cur_time < start_time[0]:
        scheduler.add_job(_download_to_io_upload_yadisk, "cron", day_of_week='mon-sun',
                          hour=9, minute=10, args=(dp,), timezone=ZoneInfo('Europe/Moscow'))
        scheduler.add_job(_download_to_io_upload_yadisk, "cron", day_of_week='mon-sun',
                          hour=12, minute=10, args=(dp,), timezone=ZoneInfo('Europe/Moscow'))


async def admin_notify(dp: Dispatcher, key: str):
    try:
        await dp.bot.send_message(getenv("ADMIN"),
                                  f'{datetime.datetime.now(tz=ZoneInfo("Europe/Moscow")).strftime("%d.%m.%Y-%H:%M:%S")}'
                                  f'{"Бот запущен и готов к работе" if key == "on" else "Бот выключается"}')
    except Exception as err:
        logging.exception(err)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
    ])


async def on_startup(dp):
    await admin_notify(dp, key='on')
    await set_default_commands(dp)

    from main import scheduler
    await price_download_scheduler(dp, scheduler)
    scheduler.start()


async def on_shutdown(dp):
    from main import scheduler
    scheduler.shutdown()
    await admin_notify(dp, key='off')
