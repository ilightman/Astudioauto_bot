import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from pyzbar.pyzbar import decode
from PIL import Image
from dadata import Dadata


def delivery(to_index: int, weight=None, price=None, from_index=125476) -> str:
    url_base = 'https://delivery.pochta.ru/v2/calculate'
    if weight and price:
        # расчет тарифа и контрольные сроки
        url_base += '/tariff/'
        pack = 40 if int(weight) > 2000 else 20 if 1000 < int(weight) <= 2000 else 10  # s-10, m-20, l-30, xl-40
        params = {'object': '4040',
                  'from': from_index,
                  'to': from_index,
                  'weight': weight,
                  'pack': pack,
                  'sumoc': f'{price}00'
                  }
    else:
        # только сроки доставки
        params = {'object': '27040',
                  'from': from_index,
                  'to': to_index,
                  'weight': '1000',
                  'pack': '20'
                  }
    params['date'] = f'&date={(datetime.now() + timedelta(days=2 if not price else 3)).strftime("%Y%m%d")}'

    resp = requests.get(url_base + '/delivery?json', params=params)
    resp_json = resp.json()

    try:
        delivery_days = resp_json["delivery"]["max"]
        delivery_deadline = datetime.strptime(resp_json["delivery"]["deadline"][0:8], "%Y%m%d").strftime("%d.%m.%Y")
        delivery_days_str = f'Срок доставки:  <b>{delivery_days}</b> дн.\nДоставка:  до <b>{delivery_deadline}</b>'
        if price:
            pay_nds = resp_json["paynds"]
            return f'Стоимость:  <b>{float(pay_nds / 100):5.2f}</b> руб. \n' + delivery_days_str
        else:
            return delivery_days_str

    except KeyError:
        return resp_json['errors'][0]['msg']


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
    dadata = Dadata(token, secret)
    adr_resp = dadata.clean(name='address', source=full_address_str)
    return f'{adr_resp["postal_code"]}, {adr_resp["result"]}'


def barcode_response(file):
    result = decode(Image.open(file))
    for i in result:
        data = i.data.decode("utf-8")
        if data.startswith('[CDK]'):
            return data[5:], 'СДЭК'
        elif data.startswith('125476'):
            return data, 'Почта России'
        else:
            return False


def retail(track_number: str, delivery_type: str) -> str:
    url = 'https://astudioauto.retailcrm.ru/api/v5/orders'
    param = {'filter[trackNumber]': track_number,
             'apiKey': 'bxc4npBsLqpf9OZIsOvvLR0CwWQleux5'
             }
    r = requests.get(url, params=param)
    order = r.json()
    order = order['orders'][0]
    li = f"<b>{delivery_type}</b>\n"
    li += f"<b>Марка:</b> {order['customFields']['markaavto'].title()}\n"
    li += f"<b>Модель:</b> {order['customFields']['modelavto']}\n"
    li += f"<b>Год:</b> {order['customFields']['godavto']}\n\n <b>В заказе:</b>\n\n"
    for i, item in enumerate(order['items'], 1):
        li += f"{i}. {item['offer']['name']} - {item['prices'][0]['quantity']}шт.\n"
        li += f"{item['prices'][0]['price']}\n\n"
    li += f"<b>{order['summ']}\n</b>"
    li += f"<code>{order['managerComment']}</code>"
    return li
