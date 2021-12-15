import requests
from PIL import Image
from pyzbar.pyzbar import decode
from bs4 import BeautifulSoup


def url_short(url: str) -> str:
    resp = requests.get('https://clck.ru/--?url=' + url)
    return resp.text


def mini_description(url: str) -> str:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    try:
        pict = ''.join(i for i in str(soup.find_all('img')[1]).split() if i.startswith('src='))[5:-1]
        pict_url = 'https://carautostudio.ru' + pict

        mini_desc = soup.find(attrs={'class': 'item_info_section product-element-preview-text'})
        mini_desc = (i.replace('\xa0', '') for i in [i.text for i in mini_desc.find_all('li')])
        mini_desk = '\n'.join(mini_desc)

        return f'<a href="{pict_url}">{url_short(url)}</a>\n{mini_desk}'

    except AttributeError:
        return 'Описание не найдено'


def address_recognition(full_address_str: str, token: str, secret: str):  # other_token: str
    # dadata = Dadata(token, secret)
    # adr_resp = dadata.clean(name='address', source=full_address_str)
    # return f'{adr_resp["postal_code"]}, {adr_resp["result"]}'
    pass


def barcode_response(file):
    result = decode(Image.open(file))
    for i in result:
        data = i.data.decode("utf-8")
        if data.startswith('[CDK]'):
            return data[5:], 'СДЭК'
        elif data.startswith('125476'):
            return data, 'Почта России'
        else:
            return data, 'Другое'
