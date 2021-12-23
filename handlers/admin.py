import logging
from datetime import datetime
from os import getenv

from aiogram import types, filters

from main import dp, bot
from misc import pochta_delivery, barcode_response, retail_delivery_info, inline_kb_constructor, Url

admins = getenv("ADMINS").split()
admins.append(getenv("ADMIN"))


@dp.callback_query_handler(filters.Text(startswith='url'), user_id=admins)
async def process_callback_button_url(callback_query: types.CallbackQuery):
    code = callback_query.data
    url = Url(callback_query.message.text)
    await callback_query.message.delete()
    if code == 'url_short':
        await bot.send_message(callback_query.message.chat.id, url.shorten(), disable_web_page_preview=True)
    elif code == 'url_mini_desc':
        await bot.send_message(callback_query.message.chat.id, url.mini_description())
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{callback_query.from_user.id}'
                 f'-{callback_query.from_user.full_name}'
                 f'-{"-url_short" if code == "url_short" else "-mini_description"}')


@dp.message_handler(filters.Regexp(r'(^\d{6}$)'), user_id=admins)
async def delivery_only_index(message: types.Message):
    """
        If User message is 6 digit return delivery days
    """
    delivery_response = await pochta_delivery(to_index=message.text)
    await message.answer(delivery_response)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-delivery_time')


@dp.message_handler(filters.Regexp(r'^(\d{6})(\s{1,})(\d{3,})(\s{1,})(\d{4,})$'), user_id=admins)
async def delivery_index_price_weight(message: types.Message):
    """
        If User message is 6 digit index, 3+ digit weight, 4+ digit price return delivery days and price
    """
    to_index, weight, price = message.text.split()
    delivery_response = await pochta_delivery(to_index=to_index, weight=weight, price=price)
    await message.answer(delivery_response)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-delivery_time_and_price')


@dp.message_handler(filters.Regexp(r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*'), user_id=admins)
async def url_work(message: types.Message):
    """
        If message is URL, then choose url_short or product_description
    """
    kb_inl = await inline_kb_constructor({'Сократить ссылку': 'url_short',
                                          'Краткое описание': 'url_mini_desc'})

    await message.answer(message.text, disable_web_page_preview=True, reply_markup=kb_inl)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-url_work')


@dp.message_handler(content_types='photo', user_id=admins)
async def photo_process(message: types.Message):
    """
        Если прислать фото проверяет есть ли на фото штрихкод,
        если есть то присылает наименование товаров в данном заказе
    """
    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    track_number = await barcode_response(downloaded_file)
    if track_number:
        if track_number.type in ('Почта России', 'СДЭК'):
            await message.answer(await retail_delivery_info(track_number))
        else:
            await message.answer(f"<code>{track_number.number}</code> - "
                                 f"не является трек-номером СДЭК или Почты России")
    else:
        await message.answer('Штрихкод не распознан или отсутствует на фото')

    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-barcode_response-{track_number.number if track_number else None}')


@dp.message_handler(commands=['start', 'help'], user_id=admins)
async def print_menu(message: types.Message):
    """
        This handler will be called when user sends `/start` or `/help` command
    """
    message_text = 'Вот, что умеет этот бот:\n' \
                   '/start , /help - отображает список доступных команд\n' \
                   '\n' \
                   '🌐 Сокращатель ссылок + мини описание:\n' \
                   '├ <code>https://carautostudio.ru/catalog/shtatnye_magnitoly/</code>\n' \
                   '└ пришлет сокращенную ссылку или краткое описание товара\n' \
                   '\n' \
                   '📮 Почта России\n' \
                   '├ <code>123456</code> - срок доставки по индексу \n' \
                   '└ <code>индекс вес цена</code> - стоимость доставки Почты и сроки' \
                   '\n' \
                   '📦 Отслеживание треков для посылок Почта россии и СДЭК:\n' \
                   '├ <code>1234578901234</code> - для Почтовых отправления с 14 значными номерами (только цифры)\n' \
                   '└ <code>RU123456789CH</code> - для EMS и Международных отправлений c 13 значными номерами\n' \
                   '\n' \
                   '\n\n\n<b>ВРЕМЕННО НЕДОСТУПЕН</b>🗺\n' \
                   '🗺️ Адрес:\n' \
                   '├ <code>Москва Манежная площадь 1</code>\n' \
                   '└ распознанный адрес, индекс и срок доставки Почтой России'

    await message.answer(message_text)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-command-{message.text}')
