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
