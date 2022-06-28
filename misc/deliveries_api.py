from datetime import timedelta
import requests
from datetime import datetime
from math import acos, sin, cos, radians
from os import getenv

from aiogram import types
from cdek.api import CDEKClient


def _calculate_distance(location_1: types.Location, location_2: types.Location) -> int:
    """Считает приблизительное расстояние в метрах между двумя точками по координатам"""
    earth_radius = 6372795
    lx1, ly1 = radians(location_1.latitude), radians(location_1.longitude)
    lx2, ly2 = radians(location_2.latitude), radians(location_2.longitude)
    c_lx1, c_lx2 = cos(lx1), cos(lx2)
    s_lx1, s_lx2 = sin(lx1), sin(lx2)
    distance1 = acos(s_lx1 * s_lx2 + c_lx1 * c_lx2 * cos(ly2 - ly1))
    return round(distance1 * earth_radius)


def _get_nearby_points_distance(points_list: list[dict[str, list]], ) -> str:
    pass


def cdek_nearby_delivery_point(index: int):
    cdek_id = getenv('CDEK_ID')
    cdek_pass = getenv('CDEK_PASS')
    client = CDEKClient(cdek_id, cdek_pass)
    cdek_points = client.get_delivery_points(city_post_code=index, point_type='ALL', allowed_cod=True)
    _get_nearby_points_distance(cdek_points.get('pvz'))
    # pprint(cdek_points.get('pvz'))


# cdek_nearby_delivery_point(143405)
# y             x
# 55.815340, 37.353062
# 55.874826, 37.357528
# my_cords = types.Location(latitude=55.815340, longitude=37.353062)
# test_cords = types.Location(latitude=55.814826, longitude=37.357528)
# my_cords.latitude, my_cords.longitude = 55.81534, 37.353062
# test_cords.latitude, test_cords.longitude = 55.874826, 37.357528


async def pochta_delivery(to_index: int, price: str = None, weight: str = None, from_index: int = 125476) -> str:
    url_base = 'https://delivery.pochta.ru/v2/calculate'
    if price and weight:
        # расчет стоимость и срока доставки
        url_base += '/tariff/'
        pack = 40 if int(weight) > 2000 else 20 if 1000 < int(weight) <= 2000 else 10  # s-10, m-20, l-30, xl-40
        params = {'object': '4040', 'weight': weight, 'pack': pack,
                  'sumoc': f'{price}00'}
    else:
        # расчет только срока доставки
        params = {'object': '27040', 'weight': '1000', 'pack': '20'}

    params['from'], params['to'] = from_index, to_index
    params['date'] = f'&date={(datetime.now() + timedelta(days=2 if not price else 3)).strftime("%Y%m%d")}'

    resp = requests.get(url_base + '/delivery?json', params=params)
    resp_json = resp.json()

    try:
        delivery_days = resp_json["delivery"]["max"]
        delivery_deadline = datetime.strptime(resp_json["delivery"]["deadline"][0:8], "%Y%m%d").strftime("%d.%m.%Y")
        delivery_days_str = f'Срок доставки:  <b>{delivery_days}</b> дн.\nДоставка:  до <b>{delivery_deadline}</b>'
        if price:
            pay_nds = resp_json["paynds"]
            return f'Стоимость:  <b>{float(pay_nds / 100):5.2f}</b> руб. \n {delivery_days_str}'
        else:
            return delivery_days_str

    except KeyError:
        return resp_json['errors'][0]['msg']
