from os import getenv

import requests

from misc.classes import TrackNumber, RetailCrmOrder


async def retail_delivery_info(track: TrackNumber) -> str:
    url = 'https://astudioauto.retailcrm.ru/api/v5/orders'
    param = {'filter[trackNumber]': track.number,
             'apiKey': getenv('RETAIL_APIKEY')}
    r = requests.get(url, params=param)
    order = r.json()
    order = order['orders'][0]
    li = f"<b>{track.type}</b>\n" \
         f"<b>Авто:</b> {order['customFields']['markaavto'].title()} " \
         f"{order['customFields']['modelavto']} {order['customFields']['godavto']}\n\n" \
         f"<b>В заказе:</b>\n\n"
    for i, item in enumerate(order['items'], 1):
        li += f"{i}. {item['offer']['name']} - {item['prices'][0]['quantity']}шт.  " \
              f"{item['prices'][0]['price']} руб.\n\n"
    li += f"Общая сумма заказа - <b>{order['summ']}</b> руб.\n" \
          f"<code>{order['managerComment']}</code>"
    return li


async def retail_info_by_phone_number(phone_number: str) -> (str, TrackNumber):
    url = 'https://astudioauto.retailcrm.ru/api/v5/orders'
    param = {'filter[customer]': phone_number,
             'filter[extendedStatus][]': ['delivery-group', 'complete'],
             'apiKey': getenv('RETAIL_APIKEY')}
    r = requests.get(url, params=param)
    order = r.json()
    msg, track = '', None
    try:
        if not order['orders']:
            raise IndexError
        else:
            order = RetailCrmOrder(order['orders'][0])
            track = order.track_number
            msg = f"<b>Номер заказа:</b> {order.number}\n" \
                  f"<b>Статус заказа:</b> {order.status}\n" \
                  f"<b>Служба доставки:</b> {track.type}\n" \
                  f"<b>Номер отслеживания:</b> {track.number}"
    except AttributeError:
        msg = '<b>Ошибка</b>, заказ с указанным номером телефона в системе отсутствует, проверьте правильность ввода'
    except IndexError:
        msg = '<b>Ошибка</b>, Активные заказы с указанным номером телефона в системе отсутсвуют, ' \
              'проверьте правильность ввода'
    finally:
        return msg, track
