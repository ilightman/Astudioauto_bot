import urllib3
import json
from datetime import datetime


def delivery(pindex: int, weight=4000, f_index=125476) -> str:
    url_base = 'https://delivery.pochta.ru/v2/calculate/delivery?json&object=27030'
    params = f'&from={f_index}&to={pindex}&weight={weight}&pack=40&date={datetime.now().strftime("%Y%m%d")}'
    http = urllib3.PoolManager()
    resp_json = json.loads(http.urlopen('GET', url_base + params).data)
    try:
        delivery_days = {resp_json["delivery"]["max"]}
        delivery_deadline = datetime.strptime(resp_json["delivery"]["deadline"][0:8], "%Y%m%d").strftime("%d.%m.%Y")
        return f'~{delivery_days} дней, до {delivery_deadline}'
    except KeyError:
        return resp_json['errors'][0]['msg']


def url_short(url: str) -> str:
    url_long = 'https://clck.ru/--?url=' + url
    http = urllib3.PoolManager()
    url_sh = http.urlopen('GET', url_long).data
    return url_sh.decode('UTF-8')
