from datetime import datetime, timedelta

import requests


def delivery(to_index: int, weight=None, price=None, from_index=125476) -> str:
    url_base = 'https://delivery.pochta.ru/v2/calculate'
    if weight and price:
        # расчет тарифа и контрольные сроки
        url_base += '/tariff/'
        pack = 40 if int(weight) > 2000 else 20 if 1000 < int(weight) <= 2000 else 10  # s-10, m-20, l-30, xl-40
        params = {'object': '4040',
                  'from': from_index,
                  'to': to_index,
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
