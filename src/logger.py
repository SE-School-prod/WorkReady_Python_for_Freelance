import os
import datetime

from logging import ERROR, StreamHandler, FileHandler, Formatter, getLogger, DEBUG, config
# from pytz import timezone
import pytz
from logging import getLogger, config, INFO, DEBUG

from settings.settings_dict import settings_dict
from .logger_config import dict_config


class DatetimeFormatter(Formatter):
    def formatTime(self, record, datefmt):
        if datefmt is None:
            datefmt = "%Y-%m-%d %H:%M:%S,%d"
        tz = datetime.timezone(datetime.timedelta(hours=9), 'JST')
        time = datetime.datetime.fromtimestamp(record.created, tz=tz)
        strftime = time.strftime(datefmt)
        return strftime


class Logger:

    def __init__(self):
        self._logger = getLogger(__name__)
        self._logger.setLevel(ERROR)

        formatter = DatetimeFormatter(
            "%(asctime)s -  [%(levelname)-8s] - %(filename)s:%(lineno)s %(funcName)s %(message)s")

        self._sh = StreamHandler()  # 画面出力ハンドラ
        self._sh.setLevel(DEBUG)
        self._sh.setFormatter(formatter)

        self._fh = FileHandler(
            filename=self._generate_log_file(), encoding='utf-8')  # ファイル書き込みハンドラ
        self._fh.setLevel(DEBUG)
        self._fh.setFormatter(formatter)

        self._logger.addHandler(self._sh)
        self._logger.addHandler(self._fh)
        self._logger.propagate = False  # 大体同じ個所の処理のログ出力をひとまとめにする

    def __del__(self):
        self._fh.close()
        self._sh.close()

    def get(self):
        return self._logger

    def _generate_log_file(self):
        now = datetime.datetime.today() + datetime.timedelta(hours=9)

        save_file_name = str(now)[:10].replace(
            '-', '') + '.log'  # YYYYMMDD.log

        # get save dir
        save_dir = settings_dict["DIR"]["LOG_SAVE_DIR"]
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        save_dir_name = os.path.join(save_dir, save_file_name)

        return save_dir_name

    def _get_config(self):
        self._dict_config = {
            "version": 1,
            "formatters": {
                "Formatter": {
                    "format": "%(asctime)s -  [%(levelname)-8s] - %(filename)s:%(lineno)s %(funcName)s %(message)s"
                }
            },
            "handlers": {
                "FileHandlers": {
                    "filename": self._generate_log_file(),
                    "class": "logging.FileHandler",
                    "formatter": "Formatter",
                    "level": "DEBUG",
                },
                "StreamHandlers": {
                    "class": "logging.StreamHandler",
                    "formatter": "Formatter",
                    "level": "INFO",
                }
            },
            # "loggers":{
            #     '':{
            #         "handlers": ["FileHandlers, StreamHandlers"],
            #         "level": "DEBUG",
            #         "propagate": 0
            #     },
            #     "server": {
            #         "handlers": ["FileHandlers"],
            #         "level": INFO,
            #         "propagate": 0
            #     }
            # }
            "root": {
                "handlers": ["FileHandlers", "StreamHandlers"],
                "level": "DEBUG",
                "propagete": 0
            }
        }
        return self._dict_config


def main():
    logger = Logger()


if __name__ == '__main__':
    main()
