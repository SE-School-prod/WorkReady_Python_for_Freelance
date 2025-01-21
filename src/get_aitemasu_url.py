"""
@file get_aitemasu_url.py
@date 2023/09/09(土)
@author 藤原光基
@brief 相談会予約bot
@details 「相談会予約」チャンネルで想定されたフォーマットで送信されたメッセージに対して
@details 運営人の「アイテマス」URLが記載されたメッセージをメンション付きで送信する。
@bar 編集日時 編集者 編集内容
@bar 2023/09/09(土) 藤原光基 新規作成
"""

import os
import datetime
import platform
import pytz

from error_handling.error_message import ErrorMessageReserveConsultation
from settings.settings_dict import settings_dict
# from .logger import Logger


# async def get_aitemasu_url(message):
async def get_aitemasu_url(message, logger):
    """
    logger_ = Logger()
    logger = logger_.get()
    """

    logger.info('START 相談会予約内容変更')

    try:

        # Botメッセージによる無限ループ対策
        if (message.author.display_name[-3:] != "@運営") & (message.author.id != settings_dict["GUILD_ID"]["BOT"]):

            now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

            week_day = now.weekday()
            error_message = ErrorMessageReserveConsultation(logger)

            # コマンドに対応するデータを取得して表示
            error_message.get_message(message)
            error_announce = error_message.get_error_announce()

            # send error message to user in chat
            if bool(error_announce):
                await message.channel.send(error_announce)
                return
            else:
                author_id = message.author.id
                announce = "<@" + str(author_id) + ">さん\n\n"
                announce += "ご相談内容を受理いたしました。\n"

                """
                announce += "下記URLからご希望の相談会への予約をお願いいたします。\n\n"

                if week_day == 1 or week_day == 3:
                    announce += "なお、当日のご予約につきましてはお控えくださいますよう、お願いします。\n\n"

                with open(settings_dict["DIR"]["RESERVATION_CYCLE_FILE"], 'r') as file:
                    idx = file.read()

                if idx == "4":
                    idx_write = "0"
                else:
                    idx_write = str(int(idx) + 1)

                with open(settings_dict["DIR"]["RESERVATION_CYCLE_FILE"], 'w') as file:
                    file.write(idx_write)

                # idx = "1"
                url = settings_dict["AITEMASU_URL"][idx]["url"]

                announce += url
                
                await message.channel.send(announce)

                logger.info("ユーザ名:{}, idx: {}, 講師: {}".format(message.author.display_name, idx, settings_dict["AITEMASU_URL"][idx]["name"]))
                """
                announce += "改めて担当者から日程調整用URLをこちらのチャンネルにお送りしますので、今しばらくお待ちください。\n"
                announce += "なお、システムのエラー原因となりますので、ご返信はご遠慮ください。"

                await message.channel.send(announce)

    except Exception as e:
        logger.error(e)

    logger.info('END 相談会予約内容変更')
