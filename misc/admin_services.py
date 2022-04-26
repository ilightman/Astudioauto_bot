import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo


async def _log_and_notify_admin(message: str, exception: bool = False) -> None:
    """Send message to admin and logging it"""
    if exception:
        logging.exception(message)
        try:
            from main import dp
            dt = datetime.now(tz=ZoneInfo("Europe/Moscow")).strftime("%d.%m.%Y-%H:%M:%S")
            await dp.bot.send_message(os.getenv("ADMIN"), f'{dt} - {message}')
        except Exception as e:
            logging.exception(f'Exception: {e}')
    else:
        logging.info(message)

