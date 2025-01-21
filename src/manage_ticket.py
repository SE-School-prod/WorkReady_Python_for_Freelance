"""
@file change_status.py
@date 2023/11/17(木)
@author 林田翼
@brief 相談会チケットの枚数を管理するbot
@details 無料相談および有料相談に使用するチケットの枚数を管理する
@bar 編集日時 編集者 編集内容
@bar 2023/11/17(木) 林田翼 新規作成
@bar 2023/11/17(木) 林田翼 同一名前4
"""

import datetime
from pickle import FALSE
from token import STAR
import discord
import platform
import pytz
from settings.settings_dict import settings_dict
from settings.database_id_list import database_id_list
from error_handling.error_message import ErrorMessage
from .notion import Notion
from .change_roll import check_cariculam
import re


async def accept_consultation_services(message, logger, guild):
    logger.info("START accept_consultation_services: {}".format(message))

    try:
        
        logger.debug("error check: before loop: {}".format(message))

        # メッセージの送り主がユーザの時
        if (message.author.display_name[-3:] != "@運営") and (message.author.id != settings_dict["GUILD_ID"]["BOT"]):
            # コマンド
            command = message.content

            # コマンドチェック
            consultation_type, result, err_message = check_command(command)
            if result == False:
                await message.channel.send(err_message)
                logger.warning(f"相談会予約のコマンドが間違っています。エラーメッセージ：{err_message}")
            else:
                # username,database_id,enrollment_statusを取得する
                get_messemger_name = message.author.display_name

                username = get_messemger_name.split('_')[0]
                database_id = database_id_list[get_messemger_name.split("_")[
                    1]]
                # user_idを取得する
                user_id = str(message.author.id)
                
                #無料チケットの有効期限確認
                expiration_date = confirm_ticket_expired(database_id, username, user_id, logger, guild)

                # user_idとdatabase_idでユーザの特定
                notion = Notion()
                filter_dict = {'ユーザーID': user_id}
                results_id = notion.select(database_id, filter_dict)
                # 在籍状況を変更する
                # 検索結果が一意に定まった時
                if len(results_id) == 1:

                    # 取得先のIDを取得する
                    page_id = results_id[0]["id"]
                    
                    #チケットの枚数確認
                    ticket_free,ticket_30,ticket_60 = get_ticket_num(database_id=database_id, user_id=user_id, logger=logger, guild=guild)
                    
                    #30分相談会の場合
                    if consultation_type == "30分相談会":
                        
                        #チケットある場合
                        if ticket_free > 0:
                            filter_dicts_list = [
                                {'30分無料相談チケット': ticket_free - 1}
                            ]
                            notion.update(page_id=page_id,
                                          filter_dicts_list=filter_dicts_list)
                            reply = (
                                f"<@{user_id}>さん\n"
                                f"ご相談内容を受理いたしました。\n"
                                f"改めて担当者から日程調整用URLをこちらのチャンネルにお送りしますので、今しばらくお待ちください。\n"
                                f"なお、システムのエラー原因となりますので、ご返信はご遠慮ください。\n"
                                fr"```diff"
                                f"\n"
                                fr"- ※キャンセルによるチケットのお戻しはありませんのでご注意ください"
                                f"\n"
                                fr"```"
                            )
                            """
                            if platform.platform().split('-')[0] == 'Linux':
                                now_tz = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
                                temp_dt = now_tz.strftime('%Y-%m-%d %H:%M:%S.%f')
                                now = datetime.datetime.strptime(temp_dt, '%Y-%m-%d %H:%M:%S.%f')
                            else:
                                now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
                            """
                            now = datetime.datetime.now(
                                pytz.timezone('Asia/Tokyo'))
                            log_message = "ユーザID: {}, ユーザ名: {}, 更新日時: {}".format(
                                user_id, username, now)
                            logger.info("アップデート成功: {}".format(log_message))
                            
                        elif ticket_30 > 0:
                            filter_dicts_list = [
                                {'30分有料相談チケット': ticket_30 - 1}
                            ]
                            notion.update(page_id=page_id,
                                            filter_dicts_list=filter_dicts_list)
                            reply = (
                                f"<@{user_id}>さん\n"
                                f"ご相談内容を受理いたしました。\n"
                                f"改めて担当者から日程調整用URLをこちらのチャンネルにお送りしますので、今しばらくお待ちください。\n"
                                f"なお、システムのエラー原因となりますので、ご返信はご遠慮ください。"
                                fr"```diff"
                                f"\n"
                                fr"- ※キャンセルによるチケットのお戻しはありませんのでご注意ください"
                                f"\n"
                                fr"```"
                            )
                            if platform.platform().split('-')[0] == 'Linux':
                                now_tz = datetime.datetime.now(
                                    pytz.timezone('Asia/Tokyo'))
                                temp_dt = now_tz.strftime(
                                    '%Y-%m-%d %H:%M:%S.%f')
                                now = datetime.datetime.strptime(
                                    temp_dt, '%Y-%m-%d %H:%M:%S.%f')
                            else:
                                now = datetime.datetime.now(
                                    pytz.timezone('Asia/Tokyo'))
                            log_message = "ユーザID: {}, ユーザ名: {}, 更新日時: {}".format(
                                user_id, username, now)
                            logger.info("アップデート成功: {}".format(log_message))

                        else:
                            #チケットない場合
                            reply = (
                                f"<@{user_id}>さん\n"
                                f"30分相談会を予約するためのチケットが不足しています。\nお手数ですが下記URLよりチケットを購入し、再度予約してください。\n\n"
                                f"★30分有料相談チケットはこちら\n"
                                f"https://buy.stripe.com/7sI3eGfSNdks1Vu00f\n"
                                f"\n"
                                f"★60分有料相談チケットはこちら\n"
                                f"https://buy.stripe.com/8wM9D4gWR3JSeIg00g\n"
                            )
                            
                    #60分有料相談の場合
                    elif consultation_type == "60分相談会":
                        
                        #チケットある場合
                        if ticket_free > 1:
                            filter_dicts_list = [
                                {'30分無料相談チケット': ticket_free - 2}
                            ]
                            notion.update(page_id=page_id,
                                          filter_dicts_list=filter_dicts_list)
                            reply = (
                                f"<@{user_id}>さん\n"
                                f"ご相談内容を受理いたしました。\n"
                                f"改めて担当者から日程調整用URLをこちらのチャンネルにお送りしますので、今しばらくお待ちください。\n"
                                f"なお、システムのエラー原因となりますので、ご返信はご遠慮ください。"
                                fr"```diff"
                                f"\n"
                                fr"- ※キャンセルによるチケットのお戻しはありませんのでご注意ください"
                                f"\n"
                                fr"```"
                            )
                            if platform.platform().split('-')[0] == 'Linux':
                                now_tz = datetime.datetime.now(
                                    pytz.timezone('Asia/Tokyo'))
                                temp_dt = now_tz.strftime(
                                    '%Y-%m-%d %H:%M:%S.%f')
                                now = datetime.datetime.strptime(
                                    temp_dt, '%Y-%m-%d %H:%M:%S.%f')
                            else:
                                now = datetime.datetime.now(
                                    pytz.timezone('Asia/Tokyo'))
                            log_message = "ユーザID: {}, ユーザ名: {}, 更新日時: {}".format(
                                user_id, username, now)
                            logger.info("アップデート成功: {}".format(log_message))
                        
                        elif ticket_free == 1 and ticket_30 > 0:
                            filter_dicts_list = [
                                {'30分無料相談チケット': ticket_free - 1,'30分有料相談チケット': ticket_30 - 1}
                            ]
                            notion.update(page_id=page_id,
                                          filter_dicts_list=filter_dicts_list)
                            reply = (
                                f"<@{user_id}>さん\n"
                                f"ご相談内容を受理いたしました。\n"
                                f"改めて担当者から日程調整用URLをこちらのチャンネルにお送りしますので、今しばらくお待ちください。\n"
                                f"なお、システムのエラー原因となりますので、ご返信はご遠慮ください。"
                                fr"```diff"
                                f"\n"
                                fr"- ※キャンセルによるチケットのお戻しはありませんのでご注意ください"
                                f"\n"
                                fr"```"
                            )
                            if platform.platform().split('-')[0] == 'Linux':
                                now_tz = datetime.datetime.now(
                                    pytz.timezone('Asia/Tokyo'))
                                temp_dt = now_tz.strftime(
                                    '%Y-%m-%d %H:%M:%S.%f')
                                now = datetime.datetime.strptime(
                                    temp_dt, '%Y-%m-%d %H:%M:%S.%f')
                            else:
                                now = datetime.datetime.now(
                                    pytz.timezone('Asia/Tokyo'))
                            log_message = "ユーザID: {}, ユーザ名: {}, 更新日時: {}".format(
                                user_id, username, now)
                            logger.info("アップデート成功: {}".format(log_message))
                            
                        elif ticket_60 > 0:
                            filter_dicts_list = [
                                {'60分有料相談チケット': ticket_60 - 1}
                            ]
                            notion.update(page_id=page_id,
                                          filter_dicts_list=filter_dicts_list)
                            reply = (
                                f"<@{user_id}>さん\n"
                                f"ご相談内容を受理いたしました。\n"
                                f"改めて担当者から日程調整用URLをこちらのチャンネルにお送りしますので、今しばらくお待ちください。\n"
                                f"なお、システムのエラー原因となりますので、ご返信はご遠慮ください。"
                                fr"```diff"
                                f"\n"
                                fr"- ※キャンセルによるチケットのお戻しはありませんのでご注意ください"
                                f"\n"
                                fr"```"
                            )
                            if platform.platform().split('-')[0] == 'Linux':
                                now_tz = datetime.datetime.now(
                                    pytz.timezone('Asia/Tokyo'))
                                temp_dt = now_tz.strftime(
                                    '%Y-%m-%d %H:%M:%S.%f')
                                now = datetime.datetime.strptime(
                                    temp_dt, '%Y-%m-%d %H:%M:%S.%f')
                            else:
                                now = datetime.datetime.now(
                                    pytz.timezone('Asia/Tokyo'))
                            log_message = "ユーザID: {}, ユーザ名: {}, 更新日時: {}".format(
                                user_id, username, now)
                            logger.info("アップデート成功: {}".format(log_message))                
                            
                        elif ticket_30 > 1:
                            filter_dicts_list = [
                                {'30分有料相談チケット': ticket_30 - 2}
                            ]
                            notion.update(page_id=page_id,
                                          filter_dicts_list=filter_dicts_list)
                            reply = (
                                f"<@{user_id}>さん\n"
                                f"ご相談内容を受理いたしました。\n"
                                f"改めて担当者から日程調整用URLをこちらのチャンネルにお送りしますので、今しばらくお待ちください。\n"
                                f"なお、システムのエラー原因となりますので、ご返信はご遠慮ください。"
                                fr"```diff"
                                f"\n"
                                fr"- ※キャンセルによるチケットのお戻しはありませんのでご注意ください"
                                f"\n"
                                fr"```"
                            )
                            if platform.platform().split('-')[0] == 'Linux':
                                now_tz = datetime.datetime.now(
                                    pytz.timezone('Asia/Tokyo'))
                                temp_dt = now_tz.strftime(
                                    '%Y-%m-%d %H:%M:%S.%f')
                                now = datetime.datetime.strptime(
                                    temp_dt, '%Y-%m-%d %H:%M:%S.%f')
                            else:
                                now = datetime.datetime.now(
                                    pytz.timezone('Asia/Tokyo'))
                            log_message = "ユーザID: {}, ユーザ名: {}, 更新日時: {}".format(
                                user_id, username, now)
                            logger.info("アップデート成功: {}".format(log_message)) 
                        
                        #チケットない場合
                        else:
                            reply = (
                                f"<@{user_id}>さん\n"
                                f"相談会の予約をするためのチケットが不足しています。\nお手数ですが、下記URLよりチケットを購入して再度予約してください。\n"
                                f"★30分有料相談チケットはこちら\n"
                                f"https://buy.stripe.com/7sI3eGfSNdks1Vu00f\n"
                                f"\n"
                                f"★60分有料相談チケットはこちら\n"
                                f"https://buy.stripe.com/8wM9D4gWR3JSeIg00g\n"
                            )

                    await message.channel.send(reply)

                elif len(results_id) == 0:
                    reply = f"該当するユーザが見つかりませんでした。"
                    await message.channel.send(reply)
                else:
                    reply = f"該当するユーザが複数人いるため特定できませんでした。"
                    await message.channel.send(reply)

    except Exception as e:
        logger.error(e)

    logger.info("END accept_consultation_services")

# チケットの枚数を返すメソッド
def get_ticket_num(database_id, user_id, logger, guild):
    ticket_free,ticket_30,ticket_60 = 0,0,0

    notion = Notion()
    filter_dict = {'ユーザーID': user_id}

    try:
        results_id = notion.select(database_id, filter_dict)
        if len(results_id) == 1:
            if results_id[0]["properties"]["30分無料相談チケット"]["number"] is None:
                ticket_free = 0
            else:
                ticket_free = results_id[0]["properties"]["30分無料相談チケット"]["number"]

            if results_id[0]["properties"]["30分有料相談チケット"]["number"] is None:
                ticket_30 = 0
            else:
                ticket_30 = results_id[0]["properties"]["30分有料相談チケット"]["number"]
           
            if results_id[0]["properties"]["60分有料相談チケット"]["number"] is None:
                ticket_60 = 0
            else:
                ticket_60 = results_id[0]["properties"]["60分有料相談チケット"]["number"]

        elif len(results_id) == 0:
            reply = f"該当するユーザが見つかりませんでした。"
            logger.error(reply)
            raise reply
        else:
            reply = f"該当するユーザが複数人いるため特定できませんでした。"
            logger.error(reply)
            raise reply
    except Exception as e:
        logger.error(e)
        raise e

    return ticket_free, ticket_30, ticket_60
  
def check_command(command):
    print("START check_command")
    consultation_type = ""
    err_message = ""
    result = True
    message_key_word_list = ['【相談会の種類】', '【カリキュラム番号】',
                             '【質問内容】', '【何をどう調べたか】', '【Gitクローン用URL】', 'https://']
    error_key_word_list = list(
        filter(lambda key_word: not key_word in command, message_key_word_list))
    print("error_key_word_list: ", error_key_word_list)

    if len(error_key_word_list) > 0:
        err_message = "ご相談内容につきまして下記項目が検知されませんでした。\n"\
            "***\n\n"

        for error_key_word in error_key_word_list:
            if error_key_word == 'https://':
                err_message += '・' + '(Gitクローン用URL)\n'
            else:
                err_message += '・' + error_key_word + "\n"

        err_message += "***\n\n" +\
            "お手数ですが、\n" +\
            "上記項目(文字列完全一致)を追加の上\n" +\
            "再度相談内容をご展開いただきますようお願いいたします。"
        result = False

    else:
        #相談会のタイプを判別する【30分相談会】【60分相談会】のいづれか
        replaced = command.replace('\n', '')
        splited = replaced.split('【相談会の種類】')[1]
        splited = splited.split('【カリキュラム番号】')[0]
        target = splited[:6]

        if( check_keyword(target) == True):
            consultation_type = target
        else:
            consultation_type = ""
            err_message = (
                "相談会の種類を下記より選択して記載してください\n"
                "「30分相談会」「60分相談会」"
            )
            result = False
       
    return consultation_type, result, err_message


def check_keyword(target):
    target_key_word_list = ['30分相談会', '60分相談会']
    
    # targetがリスト内のどれかのキーワードに部分一致するかどうかを判定
    for keyword in target_key_word_list:
        if keyword in target:
            return True

    # どのキーワードにも一致しない場合はFalseを返す
    return False


async def confirm_ticket(message, logger, guild):
    try:      
        get_messemger_name = message.author.display_name

        if(message.content == "現在のチケット枚数"):

            username =get_messemger_name.split('_')[0]
            database_id = database_id_list[get_messemger_name.split("_")[1]]
            user_id = str(message.author.id)
    
            #無料チケットの有効期限確認
            expiration_date = confirm_ticket_expired(database_id, username, user_id, logger, guild)
            
            ticket_free,ticket_30,ticket_60 = get_ticket_num(database_id, user_id, logger, guild)
            
            
            expiration_date_str = ""
            if(expiration_date != ""):
                #チケットの有効期限を表示する
                expiration_date_str = (
                    f"30分無料チケットの有効期限：{expiration_date}\n"
                    f"\n"
                )

            reply = (
                f"<@{user_id}>さんの現在のチケット枚数は以下の通りです。\n"
                f"\n"
                f"30分無料相談チケット：{ticket_free}枚\n"
                f"30分有料相談チケット：{ticket_30}枚\n"
                f"60分有料相談チケット：{ticket_60}枚\n"
                f"\n"
                f"{expiration_date_str}"
                f"チケットを購入する場合は以下のURLよりお願いいたします。\n"
                f"★30分有料相談チケットはこちら\n"
                f"https://buy.stripe.com/7sI3eGfSNdks1Vu00f\n"
                f"\n"
                f"★60分有料相談チケットはこちら\n"
                f"https://buy.stripe.com/8wM9D4gWR3JSeIg00g\n"
                )
            await message.channel.send(reply)
        else:
            reply = "コマンドが間違っています。\n「現在のチケット枚数」と入力してください。"
            await message.channel.send(reply)

    except Exception as e:
        logger.error(e)
        await message.channel.send("エラーが発生しました。「問い合わせ」チャンネルにて運営に問い合わせてください。")

def confirm_ticket_expired(database_id, username, user_id, logger, guild):
    try:
        notion = Notion()
        filter_dict = {'ユーザーID': user_id}

        ticket_free = 0
        start_date = "1970-1-1"
        
        expiration_date = ""
   
        try:
            results_id = notion.select(database_id, filter_dict)
            if len(results_id) == 1:
                page_id = results_id[0]["id"]
                
                #30分無料相談チケットの情報と作成日の情報を取得する
                if results_id[0]["properties"]["30分無料相談チケット"]["number"] is None:
                    ticket_free = 0
                else:
                    ticket_free = results_id[0]["properties"]["30分無料相談チケット"]["number"]
            
                #作成日を取得したら、4か月を過ぎているかどうかを判定する
                start_date = datetime.datetime.strptime(results_id[0]["properties"]["作成日時"]["created_time"], '%Y-%m-%dT%H:%M:%S.%fZ')
                start_date_str = start_date.strftime('%Y-%m-%d')
                #過ぎている場合は
                #30分無料相談チケットを0マイにする
                if ticket_free > 0:
                    if is_over_four_months(start_date_str):
                        filter_dicts_list = [
                            {'30分無料相談チケット': 0}
                        ]
                        notion.update(page_id=page_id, filter_dicts_list=filter_dicts_list)
                        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
                        log_message = "ユーザID: {}, ユーザ名: {}, 更新日時: {}".format(user_id, username, now)
                        logger.info("チケットの有効期限チェックを行い、アップデート成功: {}".format(log_message))
                    else:
                        #有効期限情報を作成する
                        expiration_date = start_date.date() + datetime.timedelta(days=124)
                else:
                    logger.info("チケットの有効期限チェック不要")

            elif len(results_id) == 0:
                reply = f"該当するユーザが見つかりませんでした。"
                logger.error(reply)
                raise reply
            else:
                reply = f"該当するユーザが複数人いるため特定できませんでした。"
                logger.error(reply)
                raise reply
            
            return expiration_date
        
        except Exception as e:
            logger.error(e)
            raise e
        
    except Exception as e:
        logger.error(e)
        message.channel.send("エラーが発生しました。")
        
def is_over_four_months(date_a):
    # 日付Aをdatetimeオブジェクトに変換
    date_a = datetime.datetime.strptime(date_a, "%Y-%m-%d").date()

    # 今日の日付を取得
    today = datetime.datetime.now().date()

    # 4か月前の日付を計算
    four_months_ago = today - datetime.timedelta(days=124)

    # 日付Aと4か月前の日付を比較して、4か月以上経過していればTrueを返す
    return date_a <= four_months_ago

async def recieve_consultation_report(message, logger, guild):
    logger.info("START recieve_consultation_report: {}".format(message))

    try:
        logger.debug("error check: before loop: {}".format(message))
        # コマンドの解析（1126336516092858501:1（石井晃_00001））
        command = message.content

        # コマンドチェック
        if check_custom_format(message.author, command) == False:
            reply = f'コマンドが間違っています。以下のフォーマットに当てはまるか再度ご確認ください。\n'\
                    f'18桁または19桁の数字 + 半角コロン + 1|2 のいずれか + 全角（ + 最大7文字の日本語 + 半角アンダースコア + 5桁の数字 + 全角）\n'
            await message.channel.send(reply)
        else:
            # username,database_id,enrollment_statusを取得する
            username = command.split('_')[0].split('（')[1]
            str = command.split('_')[1]
            if (str[:5] in database_id_list) == True:
                database_id = database_id_list[str[:5]]
                consultation_type = command.split('（')[0].split(':')[1]
                # user_idを取得する
                user_id = command.split(':')[0]
                # user_idとdatabase_idでユーザの特定
                notion = Notion()
                filter_dict = {'ユーザーID': user_id}
                results_id = notion.select(database_id, filter_dict)

                #無料チケットの有効期限確認
                expiration_date = confirm_ticket_expired(database_id, username, user_id,logger, guild)
    
                # チケットの枚数を変更する
                # 検索結果が一意に定まった時
                if len(results_id) == 1:

                    # 取得先のIDを取得する
                    page_id = results_id[0]["id"]
                    
                    #相談会の種類で場合分け
                    # 1：30分相談会　2:60分相談会
                    ticket_free,ticket_30,ticket_60 = get_ticket_num(database_id, user_id, logger, guild)
                    reply = "相談会対応の報告ありがとうございます。\n"\
                            "下記内容で承りました。\n\n"\
                            "----------------------------------------------------\n"\
                            f"対応講師：{message.author.display_name}\n"\
                            f"受講生徒：{command.split('（')[1].split('）')[0]}\n"
                    if consultation_type == "1":
                        reply += "30分相談会\n"
                        if ticket_free > 0:
                            filter_dicts_list = [
                                {'30分無料相談チケット': ticket_free - 1}
                            ]
                            reply += "30分無料相談チケットを1枚消費"
                        elif ticket_30 > 0:
                            filter_dicts_list = [
                                {'30分有料相談チケット': ticket_30 - 1}
                            ]
                            reply += "30分有料相談チケットを1枚消費"
                        else:
                            reply = f"30分相談会に必要なチケットがありませんでした。<@{user_id}>さんに30分相談チケットを購入してもらい、再度相談会対応報告してください。"

                    elif consultation_type == "2":
                        reply += "60分相談会\n"
                        if ticket_free > 1:
                            filter_dicts_list = [
                                {'30分無料相談チケット': ticket_free - 2}
                            ]
                            reply += "30分無料相談チケットを2枚消費"
                        elif ticket_free == 1 and ticket_30 > 0:
                            filter_dicts_list = [
                                {'30分無料相談チケット': ticket_free - 1,'30分有料相談チケット': ticket_30 - 1}
                            ]
                            reply += "30分無料相談チケットを1枚、30分有料相談チケットを1枚消費"
                        elif ticket_60 > 0:
                            filter_dicts_list = [
                                {'60分有料相談チケット': ticket_60 - 1}
                            ]
                            reply += "60分有料相談チケットを1枚消費"
                        elif ticket_30 > 1:
                            filter_dicts_list = [
                                {'30分有料相談チケット': ticket_30 - 2}
                            ]
                            reply += "30分有料相談チケットを2枚消費"
                        else:
                            reply = f"60分相談会に必要なチケットがありませんでした。<@{user_id}>さんに30分相談チケット２枚または60分相談チケットを購入してもらい、再度相談会対応報告してください。"

                    await message.channel.send(reply)
                    
                    logger.info('page_id: {}, filter_dicts_list: {}'.format(
                        page_id, filter_dicts_list))

                    notion.update(page_id=page_id,
                                    filter_dicts_list=filter_dicts_list)
                    now = datetime.datetime.now(
                        pytz.timezone('Asia/Tokyo'))

                    log_message = "ユーザID: {}, ユーザ名: {}, 相談会種類: {}, 更新日時: {}".format(
                        user_id, username, consultation_type, now)
                    logger.info("アップデート成功: {}".format(log_message))

                elif len(results_id) == 0:
                    reply = f'ignore\n'\
                            f"該当するユーザが見つかりませんでした。"
                    await message.channel.send(reply)
                else:
                    reply = f'ignore\n'\
                            f"該当するユーザが複数人いるため特定できませんでした。"
                    await message.channel.send(reply)
            else:
                reply = f'ignore\n'\
                        f"該当するデータベースがありません。エージェント番号を見直してください。"
                await message.channel.send(reply)

    except Exception as e:
        logger.error(e)

    logger.info("END recieve_consultation_report")

def check_custom_format(author, input_string):
    # メッセージの送り主がボットの場合はチェックしない
    if author.id == settings_dict["GUILD_ID"]["BOT"]:
        return True

    pattern = r'^\d{18,19}:(?:1|2)（[^\x00-\x7F]{1,7}_\d{5}）$'
    # パターンの説明:
    # ^ : 行の先頭
    # \d{18,19} : 18桁または19桁の数字
    # : : 半角コロン
    # (?:1|2) : リスト内のいずれかのテキスト
    # （ : 全角のかっこ開き
    # [^\x00-\x7F]{1,5} : 最大5文字の日本語
    # _ : 半角のアンダースコア
    # \d{5} : 5桁の数字
    # ）$ : 全角のかっこ閉じと行の終わり

    match = re.match(pattern, input_string)
    if match:
        return True
    else:
        return False