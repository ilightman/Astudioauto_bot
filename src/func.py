import urllib3
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dadata import Dadata


def delivery(to_index: int, weight=None, price=None, from_index=125476) -> str:
    url_base = 'https://delivery.pochta.ru/v2/calculate'
    if weight and price:
        # расчет тарифа и контрольные сроки
        url_base += '/tariff/delivery?json&object=4040'
        pack = 40 if int(weight) > 2000 else 20 if 1000 < int(weight) <= 2000 else 10  # s-10, m-20, l-30, xl-40
        params = f'&from=125476&to={to_index}&weight={weight}&pack={pack}&sumoc={price}00'
    else:
        # только сроки доставки
        weight = 1000
        url_base += '/delivery?json&object=27040'
        params = f'&from={from_index}&to={to_index}&weight={weight}&pack=20'

    date = f'&date={(datetime.now() + timedelta(days=2 if not price else 3)).strftime("%Y%m%d")}'

    http = urllib3.PoolManager()
    resp_http = http.urlopen('GET', url_base + params + date)
    resp_json = json.loads(resp_http.data)

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
    url_long = 'https://clck.ru/--?url=' + url
    http = urllib3.PoolManager()
    url_sh = http.urlopen('GET', url_long).data
    return url_sh.decode('UTF-8')


def mini_description(url: str) -> str:
    http = urllib3.PoolManager()
    url_sh = http.urlopen('GET', url).data
    soup = BeautifulSoup(url_sh.decode('UTF-8'), 'html.parser')
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
