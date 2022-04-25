import io
import logging
import os
from datetime import datetime
from zipfile import ZipFile
from zoneinfo import ZoneInfo

import requests
import yadisk_async
from aiogram import Dispatcher
from imap_tools import MailBox


async def _carav_price_url(dp: Dispatcher):
    c_name, c_url = '', ''
    try:
        with MailBox('imap.yandex.ru').login(username=os.getenv("YANDEX_USERNAME"),
                                             password=os.getenv("YANDEX_PASSWORD"),
                                             initial_folder='CARAV (СтудияМосква)') as mailbox:
            email_msg = list(mailbox.fetch(limit=1, charset='utf8', reverse=True))[0].text
            li = email_msg.splitlines()
            name, subscr_url = li[7].strip()[1:-1], li[8][1:-2]
            resp = requests.get(subscr_url).text
            str1 = resp.split('&retpath=')[1].split('"')[0]
            url = "https://cloud-api.yandex.net/v1/disk/public/resources?public_key=" + str1
            response_data = requests.get(url)
            c_name = response_data.json().get('name')
            c_url = response_data.json().get('file')
            c_name = name + ' ' + c_name
            logging.info('successfully retrieving name and url from mail')
            await dp.bot.send_message(os.getenv("ADMIN"),
                                      f'{datetime.now(tz=ZoneInfo("Europe/Moscow")).strftime("%d.%m.%Y-%H:%M:%S")}'
                                      ' - successfully retrieving name and url from mail')
            return c_name, c_url
    except Exception as e:
        logging.error("Couldn't retrieve name and url from mail", e)
        await dp.bot.send_message(os.getenv("ADMIN"),
                                  f'{datetime.now(tz=ZoneInfo("Europe/Moscow")).strftime("%d.%m.%Y-%H:%M:%S")}'
                                  ' - successfully retrieving name and url from mail')
        return c_name, c_url


async def _download_to_io_upload_yadisk(dp: Dispatcher):
    logging.info('скачиваю прайс-листы')
    await dp.bot.send_message(os.getenv("ADMIN"),
                              str(datetime.now(tz=ZoneInfo("Europe/Moscow"))) + ' Начинаю скачивание прайс листов')
    suppliers_dict = {
        'farcar.xlsx':
            'https://www.dropbox.com/s/3l04xay6nd5omyf/Прайс FarCar.xlsx?dl=1',
        'ergo.xls':
            'http://www.ergoauto.ru/uploads/Prays-list%20OBShchIY%20(XLS).xls',
        'carmedia.zip':
            'https://www.dropbox.com/sh/l2ifpaeheeexht2/AADPnUESLFHScNp2LiVjsqVwa?dl=1'
    }
    name, url = await _carav_price_url(dp)
    if name:
        suppliers_dict[name] = url
    y = yadisk_async.YaDisk(token=os.getenv("YADISK_TOKEN"))
    yadisk_folder = "/Прайсы/Ежедневные/"
    # очистка я.диска
    try:
        async for i in await y.listdir(yadisk_folder):
            await y.remove(yadisk_folder + i.name)
        logging.info('yadisk folder cleared')
        await dp.bot.send_message(os.getenv("ADMIN"), ' - yadisk folder cleared')
    except Exception as e:
        logging.error('yadisk error: ', e)
        await dp.bot.send_message(os.getenv("ADMIN"), ' - yadisk error: {e}')

    for name, url in suppliers_dict.items():
        try:
            logging.info(f'{name} item downloading')
            await dp.bot.send_message(os.getenv("ADMIN"), f' - {name} item downloading')
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
            logging.info(name + ' downloaded')
            await dp.bot.send_message(os.getenv("ADMIN"), f' - {name} downloaded')
        except Exception as e:
            logging.error(f"error: {name} wasn't downloaded: {e}")
            await dp.bot.send_message(os.getenv("ADMIN"), f" - error: {name} wasn't downloaded: {e}")
            continue
        finally:
            await y.close()
    await dp.bot.send_message(os.getenv("ADMIN"),
                              f'{datetime.now(tz=ZoneInfo("Europe/Moscow")).strftime("%d.%m.%Y-%H:%M:%S")}'
                              'Все файлы скачаны и загружены на Яндекс диск')
