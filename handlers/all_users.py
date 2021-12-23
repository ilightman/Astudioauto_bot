import logging
from datetime import datetime

from aiogram import types, filters

from handlers.admin import admins
from main import dp, bot
from misc import inline_kb_constructor, retail_info_by_phone_number, TrackNumber


@dp.callback_query_handler(filters.Text(startswith='tracking'))
async def process_callback_button_tracking(callback_query: types.CallbackQuery):
    track = TrackNumber(callback_query.message.text.split()[-1])
    await bot.send_message(callback_query.message.chat.id, track.track_down(), reply_markup=None)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-{"ADMIN" if callback_query.message.from_user.id in admins else "User"}'
                 f'-{callback_query.from_user.id}'
                 f'-{callback_query.from_user.full_name}'
                 f'-{track.type}-tracking-from_callback-{track.number}')


@dp.message_handler(filters.Regexp(r'(^\d{14}$)|(^[A-Z]{2}\d{9}[A-Z]{2}$)|(^[^9]\d{9}$)'))
async def tracking(message: types.Message):
    track = TrackNumber(message.text)
    await message.answer(track.track_down())
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-{"ADMIN" if message.from_user.id in admins else "User"}'
                 f'-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'- {track.type}-tracking-{track.number}')


@dp.message_handler(content_types='contact')
@dp.message_handler(filters.Regexp(r'(^[+][7]\d{10}$)|(^[7-8]\d{10}$)|(^[9]\d{9}$)'))
async def contact(message: types.Message):
    phone_num = message.contact.phone_number if message.content_type == 'contact' else message.text
    msg, track = await retail_info_by_phone_number(phone_num)
    if track:
        kb_inl = await inline_kb_constructor({'Отследить тут': 'tracking',
                                              track.type: track.ext_tracking_link()}, 2)
        await message.answer(msg, reply_markup=kb_inl)
    else:
        await message.answer(msg, reply_markup=types.ReplyKeyboardRemove())
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
