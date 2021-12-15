import requests


def retail_delivery_info(track_number: str, delivery_type: str) -> str:
    url = 'https://astudioauto.retailcrm.ru/api/v5/orders'
    param = {'filter[trackNumber]': track_number,
             'apiKey': 'bxc4npBsLqpf9OZIsOvvLR0CwWQleux5'
             }
    r = requests.get(url, params=param)
    order = r.json()
    order = order['orders'][0]
    li = f"<b>{delivery_type}</b>\n" \
         f"<b>Марка:</b> {order['customFields']['markaavto'].title()}\n" \
         f"<b>Модель:</b> {order['customFields']['modelavto']}\n" \
         f"<b>Год:</b> {order['customFields']['godavto']}\n\n <b>В заказе:</b>\n\n"
    for i, item in enumerate(order['items'], 1):
        li += f"{i}. {item['offer']['name']} - {item['prices'][0]['quantity']}шт.\n" \
              f"{item['prices'][0]['price']}\n\n"
    li += f"<b>{order['summ']}\n</b>" \
          f"<code>{order['managerComment']}</code>"
    return li
