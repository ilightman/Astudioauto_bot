import requests
from PIL import Image
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
from pyzbar.pyzbar import decode


async def url_short(url: str) -> str:
    """Return shortened url by https://clck.ru/ service

    :param url: url that needs to be shortened
    :type url: str

    :rtype: str
    :return: shortened url
    """
    resp = requests.get('https://clck.ru/--?url=' + url)
    return resp.text


async def mini_description(url: str) -> str:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    try:
        pict = ''.join(i for i in str(soup.find_all('img')[1]).split() if i.startswith('src='))[5:-1]
        pict_url = 'https://carautostudio.ru' + pict

        mini_desc = soup.find(attrs={'class': 'item_info_section product-element-preview-text'})
        mini_desc = (i.replace('\xa0', '') for i in [i.text for i in mini_desc.find_all('li')])
        mini_desc = '\n'.join(mini_desc)

        return f'<a href="{pict_url}">{await url_short(url)}</a>\n{mini_desc}'

    except AttributeError:
        return 'Описание не найдено'


async def address_recognition(full_address_str: str, token: str, secret: str):  # other_token: str
    # dadata = Dadata(token, secret)
    # adr_resp = dadata.clean(name='address', source=full_address_str)
    # return f'{adr_resp["postal_code"]}, {adr_resp["result"]}'
    pass


async def barcode_response(file) -> dict:
    result = decode(Image.open(file))
    data = {}
    for i in result:
        code_data = i.data.decode("utf-8")
        if code_data.startswith('[CDK]'):
            data['Name'], data['data'] = 'СДЭК', code_data[5:]
        elif code_data.startswith('125476'):
            data['Name'], data['data'] = 'Почта России', code_data
        elif code_data:
            data['Name'], data['data'] = 'Other', code_data
        return data


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
