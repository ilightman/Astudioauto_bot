import re
from datetime import datetime
from os import getenv

import requests
from bs4 import BeautifulSoup
from cdek.api import CDEKClient
from pochta import tracking


class Url:

    def __init__(self, url):
        self.url = url

    async def shorten(self) -> str:
        """Return shortened url by https://clck.ru/ service

        :rtype: str
        :return: shortened url
        """
        resp = requests.get('https://clck.ru/--?url=' + self.url)
        return resp.text

    async def mini_description(self) -> str:
        if 'astudioauto.ru' in self.url or 'carautostudio.ru' in self.url:
            resp = requests.get(self.url)
            soup = BeautifulSoup(resp.content, 'html.parser')
            try:
                pict = ''.join(i for i in str(soup.find_all('img')[1]).split() if i.startswith('src='))[5:-1]
                pict_url = 'https://carautostudio.ru' + pict
                mini_desc = soup.find(attrs={'class': 'item_info_section product-element-preview-text'})
                mini_desc = (i.replace('\xa0', '') for i in [i.text for i in mini_desc.find_all('li')])
                mini_desc = '\n'.join(mini_desc)
                return f'<a href="{pict_url}">{await self.shorten()}</a>\n{mini_desc}'
            except AttributeError:
                return 'Описание не найдено'
        else:
            return 'Не является ссылкой одного из магазинов'


class TrackNumber:

    def __init__(self, track: str):
        self.number = track

    @property
    def type(self):
        if re.match(r'(^\d{14}$)|(^[A-Z]{2}\d{9}[A-Z]{2}$)', self.number):
            return 'Почта России'
        elif re.match(r'(^[^9]\d{9}$)', self.number):
            return 'СДЭК'
        else:
            return 'Other'

    async def track_down(self):
        if self.type == 'Почта России':
            pochta_login = getenv('POCHTA_LOGIN')
            pochta_password = getenv('POCHTA_PASSWORD')
            try:
                data = []
                resp = tracking.SingleTracker(pochta_login, pochta_password).get_history(self.number)
                for j in resp:
                    data.append(f"{(j['OperationParameters']['OperDate']).strftime('%d.%m.%Y-%H:%M:%S')} - "
                                f"{j['OperationParameters']['OperType']['Name']}" +
                                f" - {j['OperationParameters']['OperAttr']['Name']}"
                                if j['OperationParameters']['OperAttr']['Name'] else '')
                return '\n'.join(data if len(data) <= 14 else data[-10:])
            except TypeError:
                return 'Некорректный номер трека или информация отсутствует'
        elif self.type == 'СДЭК':
            cdek_id = getenv('CDEK_ID')
            cdek_pass = getenv('CDEK_PASS')
            client = CDEKClient(cdek_id, cdek_pass)
            order_info = client.get_orders_statuses([int(self.number)], show_history=1)[0]
            try:
                data = []
                for i in order_info['Status']['State']:
                    if i['CityName'] == 'Управляющая Компания':
                        continue
                    else:
                        date = datetime.fromisoformat(i['Date']).strftime('%d.%m.%Y-%H:%M:%S')
                        data.append(f"{date} - {i['CityName']} - {i['Description']}")
                if data:
                    return '\n'.join(data if len(data) <= 14 else data[-10:])
                else:
                    return 'Информация по отслеживанию пока недоступна'
            except KeyError:
                return 'Не найден трек номер'
        else:
            return 'Не является трек номером Почты России или СДЭК'

    def ext_tracking_link(self):
        if self.type == 'Почта России':
            return f'https://www.pochta.ru/tracking#{self.number}'
        elif self.type == 'СДЭК':
            return f'https://www.cdek.ru/ru/tracking?order_id={self.number}'

    def __repr__(self):
        return f'{self.type} - {self.number}'


class RetailCrmOrder:

    def __init__(self, order: dict = {}):
        self.number = order['number'] if order else None
        self.status_code = order['status'] if order else None
        try:
            self.track_number = TrackNumber(order['delivery']['data']['trackNumber'])
        except KeyError:
            self.track_number = None

    @property
    def status(self):
        order_statuses = {'complete': 'Выполнен', 'prepayed': 'Оплачен - формируется к доставке',
                          'send-to-delivery': 'Формируется к доставке', 'delivering': 'В доставке',
                          'ojidaet-v-punkte-vidachi': 'Ожидает в пункте выдачи'}
        return order_statuses[self.status_code]
