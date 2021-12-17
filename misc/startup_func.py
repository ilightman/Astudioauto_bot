import logging
from datetime import datetime
from os import getenv

from aiogram import Dispatcher, types


async def on_startup_notify(dp: Dispatcher):
    try:
        await dp.bot.send_message(getenv("ADMIN"),
                                  f'{datetime.now().strftime("%m.%d.%Y-%H:%M:%S")} '
                                  f'Бот Запущен и готов к работе')
    except Exception as err:
        logging.exception(err)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
    ])


async def on_startup(dp):
    from misc import on_startup_notify
    # await on_startup_notify(dp)
    await set_default_commands(dp)
