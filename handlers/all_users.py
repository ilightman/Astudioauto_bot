import logging
from datetime import datetime

from aiogram import types, filters

from handlers.admin import admins
from main import dp, bot
from misc import pochta_parcel_tracking, cdek_parcel_tracking, inline_kb_constructor, \
    retail_info_by_phone_number


@dp.callback_query_handler(filters.Text(startswith='track'))
async def process_callback_button_track(callback_query: types.CallbackQuery):
    code = callback_query.data[6:]
    track_number = callback_query.message.text.split()[-1]
    if code == 'pochta':
        await bot.send_message(callback_query.message.chat.id, await pochta_parcel_tracking(track_number))
    elif code == 'cdek':
        await bot.send_message(callback_query.message.chat.id, await cdek_parcel_tracking(track_number))
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-{"ADMIN" if callback_query.message.from_user.id in admins else "User"}'
                 f'-{callback_query.from_user.id}'
                 f'-{callback_query.from_user.full_name}'
                 f'-{"pochta_tracking from cb" if code == "pochta" else "cdek_tracking from cb"}')


@dp.message_handler(filters.Regexp(r'(^\d{14}$)|(^[A-Z]{2}\d{9}[A-Z]{2}$)'))
async def pochta_tracking(message: types.Message):
    message_resp = await pochta_parcel_tracking(message.text)
    await message.answer(message_resp)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-{"ADMIN" if message.from_user.id in admins else "User"}'
                 f'-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-pochta_tracking-{message.text}')


@dp.message_handler(filters.Regexp(r'(^[^9]\d{9}$)'))
async def cdek_tracking(message: types.Message):
    message_resp = await cdek_parcel_tracking(message.text)
    await message.answer(message_resp)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-{"ADMIN" if message.from_user.id in admins else "User"}'
                 f'-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-cdek_tracking_{message.text}')


@dp.message_handler(content_types='contact')
@dp.message_handler(filters.Regexp(r'(^[+][7]\d{10}$)|(^[7-8]\d{10}$)|(^[9]\d{9}$)'))
async def contact(message: types.Message):
    try:
        phone_num = message.contact.phone_number
    except AttributeError:
        phone_num = message.text
    resp = retail_info_by_phone_number(phone_num)
    if resp:
        delivery_code, track_number, kb = resp.split()[-4], resp.split()[-1], {}
        if delivery_code == 'Почта России':
            kb = {'Отследить тут': 'track_pochta',
                  delivery_code: f'https://www.pochta.ru/tracking#{track_number}'}
        elif delivery_code == 'СДЭК':
            kb = {'Отследить тут': 'track_cdek',
                  delivery_code: f'https://www.cdek.ru/ru/tracking?order_id={track_number}'}
        kb_inl = await inline_kb_constructor(kb, 2)
        await message.answer(resp, reply_markup=kb_inl)
    else:
        await message.answer(f'Трек номера по активным заказам в системе не найдено',
                             reply_markup=types.ReplyKeyboardRemove())
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-{"ADMIN" if message.from_user.id in admins else "User"}'
                 f'-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-sends_contact_or_number-{phone_num}')


@dp.message_handler(commands=['start', 'help'])
async def print_menu(message: types.Message):
    """
        This handler will be called when user sends `/start` or `/help` command
    """
    message_text = 'Вот, что я умею:\n' \
                   '/start , /help - отображает список моих команд\n' \
                   'Умею отслеживать информацию по номеру телефона или по трек номеру, просто отправь мне свой номер'
    kb1 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb1.add(types.KeyboardButton('Этот номер', request_contact=True))
    await message.answer(message_text, reply_markup=kb1)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-{"ADMIN" if message.from_user.id in admins else "User"}'
                 f'-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-command-{message.text}')


@dp.message_handler()
async def echo(message: types.Message):
    """
    echo
    """
    await message.answer('Сработала функция Эхо: ' + message.text)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-{"ADMIN" if message.from_user.id in admins else "User"}'
                 f'-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-echo-{message.text}')
