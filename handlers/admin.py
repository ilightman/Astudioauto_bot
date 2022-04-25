import io
import logging
from os import getenv

from aiogram import types, filters

from main import dp
from misc import pochta_delivery, inline_kb_constructor, Url, qr_response

admins = getenv("ADMINS").split()
admins.append(getenv("ADMIN"))


@dp.callback_query_handler(filters.Text(startswith='url'), user_id=admins)
async def process_callback_button_url(callback_query: types.CallbackQuery):
    code = callback_query.data
    url = Url(callback_query.message.text)
    await callback_query.message.delete()
    if code == 'url_short':
        url_s = await url.shorten()
        await callback_query.message.answer(f"{url_s}\n\n<code>{url_s}</code>\n нажми ^ чтобы скопировать",
                                            disable_web_page_preview=True)
    elif code == 'url_mini_desc':
        await callback_query.message.answer(await url.mini_description())
    logging.info(f'{code}:ADMIN:{callback_query.message.from_user.id}:{callback_query.message.from_user.full_name}')


@dp.message_handler(regexp=r'(^\d{6}$)', user_id=admins)
async def delivery_time_by_index(message: types.Message):
    """
        If User message is 6 digit return delivery days
    """
    delivery_response = await pochta_delivery(to_index=message.text)
    await message.answer(delivery_response)
    logging.info(f':ADMIN:{message.from_user.id}:{message.from_user.full_name}')


@dp.message_handler(regexp=r'^(\d{6})(\s{1,})(\d{3,})(\s{1,})(\d{4,})$', user_id=admins)
async def delivery_index_price_weight(message: types.Message):
    """
        If User message is 6 digit index, 3+ digit weight, 4+ digit price return delivery days and price
    """
    to_index, weight, price = message.text.split()
    delivery_response = await pochta_delivery(to_index=to_index, weight=weight, price=price)
    await message.answer(delivery_response)
    logging.info(f':ADMIN:{message.from_user.id}:{message.from_user.full_name}')


@dp.message_handler(regexp=r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*', user_id=admins)
async def url_shortener(message: types.Message):
    """
        If message is URL, then choose url_short or product_description
    """
    kb_inl = await inline_kb_constructor({'Сократить ссылку': 'url_short',
                                          'Краткое описание': 'url_mini_desc'})
    await message.answer(message.text, disable_web_page_preview=True, reply_markup=kb_inl)
    logging.info(f':ADMIN:{message.from_user.id}:{message.from_user.full_name}')


@dp.message_handler(content_types=['photo', 'document'], user_id=admins)
async def barcode_response(message: types.Message):
    """
        Если прислать фото проверяет есть ли на фото штрихкод,
        если есть то присылает наименование товаров в данном заказе
    """
    file_in_io = io.BytesIO()
    if message.content_type == 'photo':
        await message.photo[-1].download(destination_file=file_in_io)
    elif message.content_type == 'document':
        await message.document.download(destination_file=file_in_io)
    msg = await qr_response(file_in_io)
    await message.answer(msg)
    logging.info(f':ADMIN:{message.from_user.id}:{message.from_user.full_name}')


@dp.message_handler(commands=['start', 'help'], user_id=admins)
async def start_help(message: types.Message):
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
                   '├ <code>12345678901234</code> - для Почтовых отправления с 14 значными номерами (только цифры)\n' \
                   '└ <code>RU123456789CH</code> - для EMS и Международных отправлений c 13 значными номерами\n'

    await message.answer(message_text)
    logging.info(f':ADMIN:{message.from_user.id}:{message.from_user.full_name}')
