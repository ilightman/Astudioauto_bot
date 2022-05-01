import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo


async def _log_and_notify_admin(message: str, exception: bool = False, startup_or_shutdown: bool = False) -> None:
    """Send message to admin and logging it"""
    from main import dp
    dt = datetime.now(tz=ZoneInfo("Europe/Moscow")).strftime("%d.%m.%Y-%H:%M:%S")
    if exception:
        logging.exception(message)
        try:
            await dp.bot.send_message(os.getenv("ADMIN"), f'{dt} - {message}')
        except Exception as e:
            logging.exception(f"Couldn't send message due to exception: {e}")
    elif startup_or_shutdown:
        await dp.bot.send_message(os.getenv("ADMIN"), f'{dt} - {message}')
        logging.info(message)
    else:
        logging.info(message)

