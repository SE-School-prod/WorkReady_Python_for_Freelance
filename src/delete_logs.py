"""
@file delete_logs.py
@date 2023/08/04(金)
@author 藤原光基
@brief 自動月次ログ消去bot
@details サーバ(replit)の容量上、あまりログを補完し続けたくない
@details そのため、月初に先月分のログを全て自動で削除するようにしたい。
@bar 編集日時 編集者 編集内容
@bar 2023/08/04(金) 藤原光基 新規作成
"""

import os
import datetime
import calendar
# from pytz import timezone
import pytz
import platform

from settings.settings_dict import settings_dict
"""
from .logger import Logger

logger_ = Logger()
logger = logger_.get()
"""
# def delete_logs():


def delete_logs(logger):

    logger.info("START delete_logs")

    try:
        log_dir = settings_dict["DIR"]["LOG_SAVE_DIR"]
        logs = os.listdir(log_dir)

        last_month_range = get_last_month_info()

        for log in logs:
            if not (log[:8].isdigit() and log[8:] == '.log'):
                os.remove(os.path.join(log_dir, log))
                logger.info("log file '{}' has removed.".format(log))
                continue

            file_date = int(log[:8])

            # if last_month_range[0] <= file_date <= last_month_range[1]:
            if file_date <= last_month_range[1]:
                os.remove(os.path.join(log_dir, log))
                logger.info("log file '{}' has removed.".format(log))

    except Exception as e:
        logger.error(e)

    logger.info("END delete_logs")


def get_last_month_info():
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

    if now.month == 1:
        last_month_init_day = datetime.datetime(now.year-1, 12, 1)
    else:
        last_month_init_day = datetime.datetime(now.year, now.month-1, 1)

    last_month_last_day = last_month_init_day.replace(day=calendar.monthrange(
        last_month_init_day.year, last_month_init_day.month)[1])

    return [int(last_month_init_day.strftime("%Y%m%d")), int(last_month_last_day.strftime("%Y%m%d"))]
