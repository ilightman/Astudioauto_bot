from os import getenv

import requests


async def retail_delivery_info(delivery_type: str, track_number: str) -> str:
    url = 'https://astudioauto.retailcrm.ru/api/v5/orders'
    param = {'filter[trackNumber]': track_number,
             'apiKey': getenv('RETAIL_APIKEY')}
    r = requests.get(url, params=param)
    order = r.json()
    order = order['orders'][0]
    li = f"<b>{delivery_type}</b>\n" \
         f"<b>Авто:</b> {order['customFields']['markaavto'].title()} " \
         f"{order['customFields']['modelavto']} {order['customFields']['godavto']}\n\n" \
         f"<b>В заказе:</b>\n\n"
    for i, item in enumerate(order['items'], 1):
        li += f"{i}. {item['offer']['name']} - {item['prices'][0]['quantity']}шт.  " \
              f"{item['prices'][0]['price']} руб.\n\n"
    li += f"Общая сумма заказа - <b>{order['summ']}</b> руб.\n" \
          f"<code>{order['managerComment']}</code>"
    return li


async def retail_info_by_phone_number(phone_number: str) -> str:
    url = 'https://astudioauto.retailcrm.ru/api/v5/orders'
    param = {'filter[customer]': phone_number,
             'filter[extendedStatus][]': 'delivery-group',
             'apiKey': getenv('RETAIL_APIKEY')}
    r = requests.get(url, params=param)
    order = r.json()
    msg = ''
    try:
        track_number = order['orders'][0]['delivery']['data']['trackNumber']
        delivery_code = order['orders'][0]['delivery']['integrationCode']
        delivery_code = 'Почта России' if delivery_code == 'russianpost' else 'СДЭК'
        msg = f"<b>Номер заказа:</b> {order['orders'][0]['number']}\n" \
              f"<b>Служба доставки:</b> {delivery_code}\n" \
              f"<b>Номер отслеживания:</b> {track_number}"
        return msg
    except AttributeError:
        return msg
    except IndexError:
        return msg
