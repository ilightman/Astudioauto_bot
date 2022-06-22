import datetime
from zoneinfo import ZoneInfo

from aiogram import types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from misc.admin_services import _log_and_notify_admin
from misc.price_download import download_prices_to_yadisk, NameLink


async def price_download_scheduler(scheduler: AsyncIOScheduler):
    cur_time = datetime.datetime.now(tz=ZoneInfo('Europe/Moscow')).time()
    start_time = (datetime.time(hour=9), datetime.time(hour=12))
    if cur_time > start_time[0]:
        await _log_and_notify_admin('started to download')
        scheduler.add_job(download_prices_to_yadisk, timezone=ZoneInfo('Europe/Moscow'))
        if cur_time < start_time[1]:
            await _log_and_notify_admin('add schedule to 12:10')
            scheduler.add_job(download_prices_to_yadisk, "cron", day_of_week='mon-sun',
                              hour=12, minute=10, timezone=ZoneInfo('Europe/Moscow'))
    elif cur_time < start_time[0]:
        await _log_and_notify_admin('add schedule to 9:10')
        scheduler.add_job(download_prices_to_yadisk, "cron", day_of_week='mon-sun',
                          hour=9, minute=10, timezone=ZoneInfo('Europe/Moscow'))
        await _log_and_notify_admin('add schedule to 12:10')
        scheduler.add_job(download_prices_to_yadisk, "cron", day_of_week='mon-sun',
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
    await _log_and_notify_admin("Бот запущен и готов к работе", startup_or_shutdown=True)


async def on_shutdown(dp):
    from main import scheduler
    scheduler.shutdown()
    await _log_and_notify_admin("Бот выключается", startup_or_shutdown=True)
