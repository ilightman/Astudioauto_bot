from PIL import Image
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyzbar.pyzbar import decode

from misc.classes import TrackNumber
from misc.retail_api import retail_delivery_info


async def qr_response(file) -> str:
    result = decode(Image.open(file))
    track, c_data = None, None
    for i in result:
        c_data = i.data.decode("utf-8")
        if 'CDK' in c_data:
            track = TrackNumber(c_data[5:])
        elif c_data.startswith('125476'):
            track = TrackNumber(c_data)
    if track:
        msg = f'{track.number} - {track.type}\n' \
              f'{await retail_delivery_info(track)}'
    elif c_data and not track:
        msg = f"<code>{c_data}</code> - Не является трек номером Почты России или СДЭК"
    else:
        msg = 'Штрихкод не распознан или отсутствует на фото'
    return msg


async def inline_kb_constructor(buttons: dict, row_width: int = 3) -> InlineKeyboardMarkup:
    """Return inline keyboard made from button dict

    :param buttons: buttons dict {label:value} value could be a url
    :type buttons: dict
    :param row_width: width of button row
    :type row_width: int

    :rtype: InlineKeyboardMarkup
    :return: generated inline keyboard
    """
    kb_inl = InlineKeyboardMarkup(row_width=row_width)
    button_list = []
    for label, value in buttons.items():
        if value.startswith('http'):
            button_list.append(InlineKeyboardButton(label, url=value))
        else:
            button_list.append(InlineKeyboardButton(label, callback_data=value))
    kb_inl.add(*button_list)
    return kb_inl

def custom_time(*args):
        return datetime.now(tz=ZoneInfo("Europe/Moscow")).timetuple()
