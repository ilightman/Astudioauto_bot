import logging
from datetime import datetime

from aiogram import types, filters

from misc import pochta_parcel_tracking, cdek_parcel_tracking
from main import dp


@dp.message_handler(filters.Regexp(r'(^\d{14}$)|(^[A-Z]{2}\d{9}[A-Z]{2}$)'))
async def pochta_tracking(message: types.Message):
    message_resp = pochta_parcel_tracking(message.text)
    await message.answer(message_resp)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-USER-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-parcel tracking {message.text}')


@dp.message_handler(filters.Regexp(r'(^\d{10}$)'))
async def cdek_tracking(message: types.Message):
    message_resp = cdek_parcel_tracking(message.text)
    await message.answer(message_resp)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-USER-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-parcel tracking {message.text}')


@dp.message_handler(content_types='contact')
async def contact(message: types.Message):
    await message.answer(f'Контакт!!! {message.contact.phone_number}', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['start', 'help'])
async def print_menu(message: types.Message):
    """
        This handler will be called when user sends `/start` or `/help` command
    """
    message_text = 'Вот, что умеет этот бот:\n' \
                   '/start , /help - отображает список доступных команд'
    kb1 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb1.add(types.KeyboardButton('Этот номер', request_contact=True))
    await message.answer(message_text, reply_markup=kb1)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-USER-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-command {message.text}')


@dp.message_handler()
async def echo(message: types.Message):
    """
    echo
    """
    await message.answer(message.text)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-USER-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-echo {message.text}')
