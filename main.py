import logging
from os import getenv

from src.func import delivery, url_short, mini_description, address_recognition
from aiogram import Bot, Dispatcher, executor, types, filters

logging.basicConfig(level=logging.INFO)
bot = Bot(token=getenv("ASTUDIO_BOT_TOKEN"), parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.callback_query_handler(filters.Text(startswith='url'))
async def process_callback_button_url(callback_query: types.CallbackQuery):
    code = callback_query.data
    url = callback_query.message.text
    await callback_query.message.delete()
    if code == 'url1':
        await bot.send_message(callback_query.message.chat.id, url_short(url), disable_web_page_preview=True)
    elif code == 'url2':
        await bot.send_message(callback_query.message.chat.id, mini_description(url))


@dp.message_handler(filters.Regexp(r'^\d{6}$'))
async def delivery_only_index(message: types.Message):
    """
        If User message is 6 digit return delivery days
    """
    delivery_response = delivery(to_index=message.text)
    await message.answer(delivery_response)


@dp.message_handler(filters.Regexp(r'^\d{6}(\s|\S)\d{3,}(\s|\S)\d{4,}$'))
async def delivery_index_price_weight(message: types.Message):
    """
        If User message is 6 digit index, 3+ digit weight, 4+ digit price return delivery days and price
    """
    to_index, weight, price = message.text.split(message.text[6])
    delivery_response = delivery(to_index=to_index, weight=weight, price=price)
    await message.answer(delivery_response)


@dp.message_handler(filters.Regexp(r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*'))
async def url_shortener(message: types.Message):
    """
        If User message is URL, then user choose url_short or product_description
    """
    kb_inl = types.InlineKeyboardMarkup(row_width=2)
    kb_inl.add(types.InlineKeyboardButton('Сократить ссылку', callback_data=f'url1'))
    kb_inl.add(types.InlineKeyboardButton('Краткое описание', callback_data=f'url2'))

    await message.answer(message.text, disable_web_page_preview=True, reply_markup=kb_inl)


@dp.message_handler(commands=['start', 'help'])
async def print_menu(message):
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
                   '📮 Почта России (в срок доставки уже добавлено 2 дня)\n' \
                   '├ <code>123456</code> - срок доставки по индексу \n' \
                   '└ <code>индекс вес цена</code> - стоимость доставки Почты и сроки' \
                   '\n' \
                   '🗺️ Адрес:\n' \
                   '├ <code>Москва Манежная площадь 1</code>\n' \
                   '└ распознанный адрес, индекс и срок доставки Почтой России'

    await message.answer(message_text)


@dp.message_handler()
async def address_string_message(message: types.Message):
    token = getenv('DADATA_TOKEN')
    secret = getenv('DADATA_SECRET')
    address = address_recognition(full_address_str=message.text, token=token, secret=secret)
    text = f'{address}\n' \
           f'{delivery(address[:6])}'
    await message.answer(text)


'''@dp.message_handler()
async def echo(message: types.Message):
    """
    echo
    """
    await message.answer(message.text)'''

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
