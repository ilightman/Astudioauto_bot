import logging
from datetime import datetime
from os import getenv

from aiogram import Dispatcher, types


async def admin_notify(dp: Dispatcher, key: str):
    try:
        await dp.bot.send_message(getenv("ADMIN"),
                                  f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")} '
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


async def on_shutdown(dp):
    await admin_notify(dp, key='off')
