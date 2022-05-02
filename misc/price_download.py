import io
import os
from zipfile import ZipFile

import requests
import yadisk_async
from imap_tools import MailBox

from misc.admin_services import _log_and_notify_admin


async def _carav_price_url():
    c_name, c_url = '', ''
    try:
        with MailBox('imap.yandex.ru').login(username=os.getenv("YANDEX_USERNAME"),
                                             password=os.getenv("YANDEX_PASSWORD"),
                                             initial_folder='CARAV (СтудияМосква)') as mailbox:
            email_msg = list(_.text for _ in mailbox.fetch(limit=2, charset='utf8', reverse=True))
            email_msg = email_msg[0] if 'Прайс-лист' in email_msg[0] else email_msg[1]
            li = email_msg.splitlines()
            name, subscr_url = li[7].strip()[1:-1], li[8][1:-2]
            resp = requests.get(subscr_url).text
            str1 = resp.split('&retpath=')[1].split('"')[0]
            url = "https://cloud-api.yandex.net/v1/disk/public/resources?public_key=" + str1
            response_data = requests.get(url)
            c_name = response_data.json().get('name')
            c_url = response_data.json().get('file')
            c_name = name + ' ' + c_name
            await _log_and_notify_admin('successfully retrieving name and url from mail')

            return c_name, c_url
    except Exception as e:
        await _log_and_notify_admin(f"Couldn't retrieve name and url from mail: {e}", exception=True)
        return c_name, c_url


async def _download_to_io_upload_yadisk():
    await _log_and_notify_admin('Скачиваю прайс-листы')
    suppliers_dict = {
        'farcar.xlsx':
            'https://www.dropbox.com/s/3l04xay6nd5omyf/Прайс FarCar.xlsx?dl=1',
        'ergo.xls':
            'http://www.ergoauto.ru/uploads/Prays-list%20OBShchIY%20(XLS).xls',
        'carmedia.zip':
            'https://www.dropbox.com/sh/l2ifpaeheeexht2/AADPnUESLFHScNp2LiVjsqVwa?dl=1'
    }
    name, url = await _carav_price_url()
    if name:
        suppliers_dict[name] = url
    y = yadisk_async.YaDisk(token=os.getenv("YADISK_TOKEN"))
    yadisk_folder = "/Прайсы/Ежедневные/"
    # очистка я.диска
    try:
        async for i in await y.listdir(yadisk_folder):
            await y.remove(yadisk_folder + i.name)
        await _log_and_notify_admin('yadisk folder cleared')
    except Exception as e:
        await _log_and_notify_admin(f'yadisk error: {e}', exception=True)
    for name, url in suppliers_dict.items():
        try:
            await _log_and_notify_admin(f'{name} item downloading')
            resp = requests.get(url)
            resp_file_in_io = io.BytesIO()
            resp_file_in_io.write(resp.content)
            resp_file_in_io.seek(0)
            if not name.endswith('.zip'):
                resp_file_in_io.seek(0)
                await y.upload(resp_file_in_io, f'{yadisk_folder}{name}')
            else:
                with ZipFile(resp_file_in_io, 'r') as zip_file:
                    for item in zip_file.namelist():
                        if item.endswith('.xlsx') and 'конфликтующая' not in item.lower():
                            with zip_file.open(item, 'r') as file_from_zip_in_io:
                                await y.upload(file_from_zip_in_io, f'{yadisk_folder}{name[:-4]}.xlsx')
            await _log_and_notify_admin(name + ' скачан и загружен на Я.диск')
        except Exception as e:
            await _log_and_notify_admin(f"error: {name} wasn't downloaded: {e}", exception=True)
            continue
        finally:
            await y.close()
    await _log_and_notify_admin('Все файлы скачаны и загружены на Яндекс диск')
