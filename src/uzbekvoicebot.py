import logging

from aiogram.utils import executor

import handlers
from main import dp
from utils.helpers import on_startup


if __name__ == '__main__':
    logging.basicConfig(
        format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
        level=logging.DEBUG
    )
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
