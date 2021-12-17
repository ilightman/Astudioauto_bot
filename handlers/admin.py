import logging
from datetime import datetime
from os import getenv

from aiogram import types, filters

from main import dp, bot
from misc import pochta_delivery, url_short, mini_description, barcode_response, retail_delivery_info, \
    pochta_parcel_tracking, cdek_parcel_tracking

admins = getenv("ADMINS").split()
# admins.append(getenv("ADMIN"))


@dp.callback_query_handler(filters.Text(startswith='url'), user_id=admins)
async def process_callback_button_url(callback_query: types.CallbackQuery):
    code = callback_query.data
    url = callback_query.message.text
    await callback_query.message.delete()
    log_msg = f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}' \
              f'-ADMIN-{callback_query.from_user.id}' \
              f'-{callback_query.from_user.full_name}'
    if code == 'url1':
        await bot.send_message(callback_query.message.chat.id, url_short(url), disable_web_page_preview=True)
        log_msg += '-url_short'
    elif code == 'url2':
        await bot.send_message(callback_query.message.chat.id, mini_description(url))
        log_msg += '-mini_description'
    logging.info(log_msg)


@dp.message_handler(filters.Regexp(r'(^\d{6}$)'), user_id=admins)
async def delivery_only_index(message: types.Message):
    """
        If User message is 6 digit return delivery days
    """
    delivery_response = pochta_delivery(to_index=message.text)
    await message.answer(delivery_response)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-delivery time')


@dp.message_handler(filters.Regexp(r'^\d{6}(\s|\S)\d{3,}(\s|\S)\d{4,}$'), user_id=admins)
async def delivery_index_price_weight(message: types.Message):
    """
        If User message is 6 digit index, 3+ digit weight, 4+ digit price return delivery days and price
    """
    to_index, weight, price = message.text.split(message.text[6])
    delivery_response = pochta_delivery(to_index=to_index, weight=weight, price=price)
    await message.answer(delivery_response)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-delivery time and price')


@dp.message_handler(filters.Regexp(r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*'), user_id=admins)
async def url_work(message: types.Message):
    """
        If User message is URL, then user choose url_short or product_description
    """
    kb_inl = types.InlineKeyboardMarkup(row_width=2)
    kb_inl.add(types.InlineKeyboardButton('Сократить ссылку', callback_data=f'url1'))
    kb_inl.add(types.InlineKeyboardButton('Краткое описание', callback_data=f'url2'))

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
    resp = barcode_response(downloaded_file)
    if resp:
        if resp[1] != 'Other':
            await message.answer(retail_delivery_info(*resp))
        else:
            await message.answer(f"<code>{resp[0]}</code> - не является трек-номером СДЭК или Почты России")
    else:
        await message.answer('Штрихкод не распознан')

    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-barcode_response - {resp[1] if resp else resp}')


@dp.message_handler(filters.Regexp(r'(^\d{10}$)'))
async def cdek_tracking(message: types.Message):
    message_resp = cdek_parcel_tracking(message.text)
    await message.answer(message_resp)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-cdek tracking - {message.text}')


@dp.message_handler(filters.Regexp(r'(^\d{14}$)|(^[A-Z]{2}\d{9}[A-Z]{2}$)'))
async def pochta_tracking(message: types.Message):
    message_resp = pochta_parcel_tracking(message.text)
    await message.answer(message_resp)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-pochta tracking - {message.text}')


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
                   '\n\n\n<b>ВРЕМЕННО НЕДОСТУПЕН</b>🗺\n' \
                   '🗺️ Адрес:\n' \
                   '├ <code>Москва Манежная площадь 1</code>\n' \
                   '└ распознанный адрес, индекс и срок доставки Почтой России'

    await message.answer(message_text)
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-command {message.text}')


@dp.message_handler(user_id=admins)
async def text_string(message: types.Message):
    # token = getenv('DADATA_TOKEN')
    # secret = getenv('DADATA_SECRET')
    # address = address_recognition(full_address_str=message.text, token=token, secret=secret)
    # text = f'{address}\n' \
    #        f'{delivery(address[:6])}'
    #
    # await message.answer(text)
    #
    await message.answer('Распознавание адресов пока не доступно...')
    logging.info(f'{datetime.now().strftime("%d.%m.%Y-%H:%M:%S")}'
                 f'-ADMIN-{message.from_user.id}'
                 f'-{message.from_user.full_name}'
                 f'-text_string recognition')
