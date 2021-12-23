from PIL import Image
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyzbar.pyzbar import decode

from misc.classes import TrackNumber


async def address_recognition(full_address_str: str, token: str, secret: str):  # other_token: str
    # dadata = Dadata(token, secret)
    # adr_resp = dadata.clean(name='address', source=full_address_str)
    # return f'{adr_resp["postal_code"]}, {adr_resp["result"]}'
    pass


async def barcode_response(file) -> TrackNumber or None:
    result = decode(Image.open(file))
    for i in result:
        data = None
        code_data = i.data.decode("utf-8")
        if '[CDK]' in code_data:
            data = TrackNumber(code_data[5:])
        elif code_data.startswith('125476'):
            data = TrackNumber(code_data)
        elif code_data:
            data = TrackNumber(code_data)
        return data
    else:
        return None


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
