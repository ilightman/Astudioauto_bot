import urllib3
import json
from datetime import datetime
from aiogram import types


def delivery(p_index: int, price=None, weight=None, f_index=125476) -> str:
    if price:
        url_base = 'https://delivery.pochta.ru/v2/calculate/tariff/delivery?json&object=4040'
        pack = 40 if int(weight) > 2000 else 20 if 1000 < int(weight) <= 2000 else 10  # s-10, m-20, l-30, xl-40
        params = f'&from=125476&to={p_index}&weight={weight}&pack={pack}&sumoc={price}00'
    else:
        weight = 1000
        url_base = 'https://delivery.pochta.ru/v2/calculate/delivery?json&object=27040'
        params = f'&from={f_index}&to={p_index}&weight={weight}&pack=20'

    date = f'&date={datetime.now().strftime("%Y%m%d")}'
    http = urllib3.PoolManager()
    resp_json = json.loads(http.urlopen('GET', url_base + params + date).data)

    try:
        delivery_days = resp_json["delivery"]["max"]
        delivery_deadline = datetime.strptime(resp_json["delivery"]["deadline"][0:8], "%Y%m%d").strftime("%d.%m.%Y")
        delivery_days_s = f'{delivery_days} дн., до {delivery_deadline}'
        if price:
            paynds = resp_json["paynds"]
            return f'Ценная, {paynds // 100}.{paynds % 100} руб., ' + delivery_days_s
        else:
            return delivery_days_s
    except KeyError:
        return resp_json['errors'][0]['msg']


def url_short(url: str) -> str:
    url_long = 'https://clck.ru/--?url=' + url
    http = urllib3.PoolManager()
    url_sh = http.urlopen('GET', url_long).data
    return url_sh.decode('UTF-8')

