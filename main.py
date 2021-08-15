import logging
import os
from src.func import delivery, url_short
from aiogram import Bot, Dispatcher, executor, types, filters

# Configure logging
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
bot = Bot(token=os.environ['ASTUDIO_BOT_TOKEN'])
dp = Dispatcher(bot)


@dp.message_handler(filters.Regexp(r'^\d{6}$'))
async def mail_delivery_period(message: types.Message):
    """
    If User message is 6 digit returns Russian post estimated delivery time
    """
    await message.answer(delivery(message.text))


@dp.message_handler(filters.Regexp(r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*'))
async def url_shortener(message: types.Message):
    """
    If User message is URL, returns shortened_url
    """
    await message.answer(url_short(message.text), disable_web_page_preview = True)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler()
async def echo(message: types.Message):
    """
    echo
    """
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
