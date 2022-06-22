import io
import os
from collections import namedtuple
from typing import Iterable

import requests
import yadisk_async
from imap_tools import MailBox

from misc.admin_services import _log_and_notify_admin

NameLink = namedtuple("NameLink", 'name url')
default_email_folder = 'CARAV (СтудияМосква)'
default_remote_folder = '/Прайсы/Ежедневные/'


async def _download_file_to_io(url: str) -> io.BytesIO:
    """Скачивает файл по указанному url в объект io.BytesIO"""
    response = requests.get(url)
    file_in_io = io.BytesIO()
    file_in_io.write(response.content)
    file_in_io.seek(0)
    return file_in_io


async def _download_email_messages(imap: str = 'imap.yandex.ru',
                                   email_username: str = os.getenv("YANDEX_USERNAME"),
                                   email_password: str = os.getenv("YANDEX_PASSWORD"),
                                   initial_folder: str = default_email_folder,
                                   msg_qty: int = 2, ) -> tuple:
    """Получает последние msg_qty(количество) сообщений и возвращает кортеж текстов этих сообщений"""
    with MailBox(imap).login(username=email_username, password=email_password,
                             initial_folder=initial_folder) as mailbox:
        messages = tuple(_.text for _ in mailbox.fetch(limit=msg_qty, charset='utf8', reverse=True))
    return messages


async def _parse_email_message(email_messages: Iterable) -> NameLink | None:
    """Находит в письмах элемент с названием прайс-лист и возвращает NameLink(имя файла, ссылка на скачивание)"""
    for email_message in email_messages:
        if 'Прайс-лист' in email_message:
            li = email_message.splitlines()
            name, url = li[7].strip()[1:-1], li[8][1:-2]
            return NameLink(name=name, url=url)
    else:
        return None


async def _download_file_from_yadisk(url: str):
    """Скачивает файл с yandex disk по указанной ссылке, или обращается к этой ссылке,
    если в ней редирект на ссылку яндекс диск"""
    if not url.startswith(('https://disk.yandex.ru/', 'https://yadi.sk/')):
        resp = requests.head(url)
        url = resp.next.url
    download_url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={url}"
    downloaded_file = requests.get(download_url)
    return downloaded_file


async def _carav_price_url() -> NameLink | None:
    """Находит в письме ссылка на скачку и возвращает объект NameLink с именем и ссылкой на скачивание файла"""
    email_messages = await _download_email_messages()
    email_data = await _parse_email_message(email_messages)
    response_data = await _download_file_from_yadisk(email_data.url)
    if email_data:
        await _log_and_notify_admin('successfully retrieving name and url from mail')
        return NameLink(name=f'{email_data.name} {response_data.json().get("name")}',
                        url=response_data.json().get('file'))
    else:
        await _log_and_notify_admin('couldnot find url', exception=True)
        return None


async def _clear_remote_dir(y_client: yadisk_async.YaDisk, yadisk_remote_folder: str) -> None:
    """Очищает папку yadisk_remote_folder в Я.диске"""
    try:
        async for i in await y_client.listdir(yadisk_remote_folder):
            await y_client.remove(yadisk_remote_folder + i.name)
        await _log_and_notify_admin('yadisk folder cleared')
    except Exception as e:
        await _log_and_notify_admin(f'yadisk error: {e}', exception=True)


async def download_prices_to_yadisk():
    await _log_and_notify_admin('Скачиваю прайс-листы')
    suppliers_tuple = (
        NameLink(name='farcar.xlsx', url='https://www.dropbox.com/s/3l04xay6nd5omyf/Прайс FarCar.xlsx?dl=1'),
        NameLink(name='ergo.xls', url='http://www.ergoauto.ru/uploads/Prays-list%20OBShchIY%20(XLS).xls'),
        NameLink(name='carmedia.xlsx',
                 url='https://www.dropbox.com/sh/l2ifpaeheeexht2/AAAj4FSZneMGjqdgXVaB5NhGa/Price%20List%20of%20Car%20DVD%20Navigation-%20wholesales-web2.4.xlsx?dl=1'),
    )
    carav_price: NameLink = await _carav_price_url()
    suppliers_tuple += (carav_price,) if carav_price else ()

    y = yadisk_async.YaDisk(token=os.getenv("YADISK_TOKEN"))
    await _clear_remote_dir(y, default_remote_folder)

    for supplier in suppliers_tuple:
        try:
            await _log_and_notify_admin(f'{supplier.name} item downloading')
            downloaded_file = await _download_file_to_io(url=supplier.url)
            await y.upload(downloaded_file, f'{default_remote_folder}{supplier.name}')
            await _log_and_notify_admin(supplier.name + ' скачан и загружен на Я.диск')
        except Exception as e:
            await _log_and_notify_admin(f"error: {supplier.name} wasn't downloaded: {e}", exception=True)
            continue
        finally:
            await y.close()
    await _log_and_notify_admin('Все файлы скачаны и загружены на Яндекс диск', exception=True)
