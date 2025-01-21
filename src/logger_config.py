import logging
import os
import datetime
import platform
import pytz

from settings.settings_dict import settings_dict


def generate_log_file():
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

    save_file_name = str(now)[:10].replace('-', '') + '.log'  # YYYYMMDD.log

    # get save dir
    save_dir = settings_dict["DIR"]["LOG_SAVE_DIR"]
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_dir_name = os.path.join(save_dir, save_file_name)
    print("save_dir_name: ", save_dir_name)

    return save_dir_name


dict_config = {
    "version": 1,
    "formatters": {
        "Formatter": {
            "format": "%(asctime)s -  [%(levelname)-8s] - %(filename)s:%(lineno)s %(funcName)s %(message)s"
        }
    },
    "handlers": {
        "FileHandlers": {
            "filename": generate_log_file(),
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
    "loggers": {
        "root": {
            "handlers": ["FileHandlers, StreamHandlers"],
            "level": logging.DEBUG,
            "propagate": 0
        },
        "server": {
            "handlers": ["FileHandlers"],
            "level": logging.INFO,
            "propagate": 0
        }
    }
}
