import logging
from datetime import datetime

from aiogram import types

from main import dp


@dp.message_handler(commands=['start', 'help'])
async def print_menu(message: types.Message):
    """
        This handler will be called when user sends `/start` or `/help` command
    """
    message_text = 'Вот, что умеет этот бот:\n' \
                   '/start , /help - отображает список доступных команд'

    await message.answer(message_text)
    logging.info(f'{datetime.now().strftime("%m.%d.%Y-%H:%M:%S")}'
                 f'-USER-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-command {message.text}')


@dp.message_handler()
async def echo(message: types.Message):
    """
    echo
    """
    await message.answer(message.text)
    logging.info(f'{datetime.now().strftime("%m.%d.%Y-%H:%M:%S")}'
                 f'-USER-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-echo {message.text}')
