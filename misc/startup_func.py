import datetime
from zoneinfo import ZoneInfo

from aiogram import types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from misc.admin_services import _log_and_notify_admin
from misc.price_download import _download_to_io_upload_yadisk


async def price_download_scheduler(scheduler: AsyncIOScheduler):
    cur_time = datetime.datetime.now(tz=ZoneInfo('Europe/Moscow')).time()
    start_time = (datetime.time(hour=9), datetime.time(hour=12))
    if cur_time > start_time[0]:
        scheduler.add_job(_download_to_io_upload_yadisk, timezone=ZoneInfo('Europe/Moscow'))
        if cur_time < start_time[1]:
            scheduler.add_job(_download_to_io_upload_yadisk, "cron", day_of_week='mon-sun',
                              hour=12, minute=10, timezone=ZoneInfo('Europe/Moscow'))
    elif cur_time < start_time[0]:
        scheduler.add_job(_download_to_io_upload_yadisk, "cron", day_of_week='mon-sun',
                          hour=9, minute=10, timezone=ZoneInfo('Europe/Moscow'))
        scheduler.add_job(_download_to_io_upload_yadisk, "cron", day_of_week='mon-sun',
                          hour=12, minute=10, timezone=ZoneInfo('Europe/Moscow'))


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
    ])


async def on_startup(dp):
    await set_default_commands(dp)

    from main import scheduler
    await price_download_scheduler(scheduler)
    scheduler.start()
    await _log_and_notify_admin("Бот запущен и готов к работе")


async def on_shutdown(dp):
    from main import scheduler
    scheduler.shutdown()
    await _log_and_notify_admin("Бот выключается")
