import logging
import os

from aiogram.utils import executor

import handlers
from main import dp, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from utils.helpers import on_startup


if __name__ == '__main__':
    logging.basicConfig(
        format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
        level=logging.DEBUG
    )
    if os.getenv('WEBHOOK_HOST') is not None:
        print('RUNNING WEBHOOK')
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        print('RUNNING POLLING')
        executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
