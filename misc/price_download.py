import io
import os
from typing import Iterable

import requests
import yadisk_async
from imap_tools import MailBox

from config import default_email_folder, NameLink, default_remote_folder, suppliers
from misc.admin_services import _log_and_notify_admin


async def _download_file_to_io(url: str) -> io.BytesIO:
    """Скачивает файл по указанному url в объект io.BytesIO"""
    response = requests.get(url)
    file_in_io = io.BytesIO()
    file_in_io.write(response.content)
    file_in_io.seek(0)
    return file_in_io


async def _download_email_messages(imap: str, email_username: str, email_password: str, initial_folder: str,
                                   msg_qty: int = 2, ) -> tuple:
    """Получает последние msg_qty(количество) сообщений и возвращает кортеж текстов этих сообщений"""
    with MailBox(host=imap).login(username=email_username, password=email_password,
                                  initial_folder=initial_folder) as mb:
        messages = tuple(_.text for _ in mb.fetch(limit=msg_qty, charset='utf8', reverse=True))
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


async def _check_or_get_yadisk_url(url: str) -> requests.Response:
    """Проверяет является ли данная ссылка - ссылкой на файл который принадлежит yadisk,
    если ссылка редиректная, то переходит по ней и там находит корректный url"""
    if not url.startswith(('https://disk.yandex.ru/', 'https://yadi.sk/')):
        resp = requests.head(url)
        url = resp.next.url
    download_url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={url}"
    downloaded_file = requests.get(download_url)
    return downloaded_file


async def _carav_price_url() -> NameLink | None:
    """Находит в письме ссылка на скачку и возвращает объект NameLink с именем и ссылкой на скачивание файла"""
    email_messages = await _download_email_messages(imap='imap.yandex.ru',
                                                    email_username=os.getenv("YANDEX_USERNAME"),
                                                    email_password=os.getenv("YANDEX_PASSWORD"),
                                                    initial_folder=default_email_folder)
    email_data = await _parse_email_message(email_messages)
    response_data = await _check_or_get_yadisk_url(email_data.url)
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
    suppliers_tuple = suppliers
    carav_price = await _carav_price_url()
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
