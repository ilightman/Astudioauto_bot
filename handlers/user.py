import logging
from datetime import datetime

from aiogram import types, filters

from misc import pochta_parcel_tracking, cdek_parcel_tracking, retail_find_track_by_tel_number, inline_kb_constructor
from main import dp, bot


@dp.callback_query_handler(filters.Text(startswith='track'))
async def process_callback_button_track(callback_query: types.CallbackQuery):
    code = callback_query.data[6:]
    track_number = callback_query.message.text.split()[-1]
    if code == 'pochta':
        await bot.send_message(callback_query.message.chat.id, pochta_parcel_tracking(track_number))
    elif code == 'cdek':
        await bot.send_message(callback_query.message.chat.id, cdek_parcel_tracking(track_number))
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{callback_query.from_user.id}'
                 f'-{callback_query.from_user.full_name}'
                 f'-{"-pochta_tracking from cb" if code == "pochta" else "-cdek_tracking from cb"}')


@dp.message_handler(filters.Regexp(r'(^\d{14}$)|(^[A-Z]{2}\d{9}[A-Z]{2}$)'))
async def pochta_tracking(message: types.Message):
    message_resp = pochta_parcel_tracking(message.text)
    await message.answer(message_resp)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-USER-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-parcel tracking {message.text}')


@dp.message_handler(filters.Regexp(r'(^[^9]\d{9}$)'))
async def cdek_tracking(message: types.Message):
    message_resp = cdek_parcel_tracking(message.text)
    await message.answer(message_resp)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-USER-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-parcel tracking {message.text}')


@dp.message_handler(content_types='contact')
@dp.message_handler(filters.Regexp(r'(^[+][7]\d{10}$)|(^[7-8]\d{10}$)|(^[9]\d{9}$)'))
async def contact(message: types.Message):
    try:
        phone_num = message.contact.phone_number
    except AttributeError:
        phone_num = message.text
    resp = retail_find_track_by_tel_number(phone_num)
    if resp:
        if resp[0] == 'Почта России':
            kb_inl = inline_kb_constructor({'Отследить': 'track_pochta',
                                            'Почта России': f'https://www.pochta.ru/tracking#{resp[1]}'})
        elif resp[0] == 'СДЭК':
            kb_inl = inline_kb_constructor({'Отследить': 'track_cdek',
                                            'СДЭК': f'https://www.cdek.ru/ru/tracking?order_id={resp[1]}'})
        await message.answer(f'Трек номер {resp[0]}: {resp[1]}', reply_markup=kb_inl)
    else:
        await message.answer(f'Трек номера по активным заказам в системе не найдено',
                             reply_markup=types.ReplyKeyboardRemove())
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-USER-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-sends contact or number {phone_num}')


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
    await message.answer('Сработала функция Эхо: ' + message.text)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-USER-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-echo {message.text}')
