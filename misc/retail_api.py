from os import getenv

import requests


def retail_delivery_info(track_number: str, delivery_type: str) -> str:
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
