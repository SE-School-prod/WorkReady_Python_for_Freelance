"""
@file change_status.py
@date 2023/010/27(金)
@author 林田翼
@brief notionのステータス変更bot
@details 管理者用のチャンネルに指定したコマンド入力に応じてnotion上の進捗管理DBの在籍状況を変更する。
@bar 編集日時 編集者 編集内容
@bar 2023/010/27(金) 林田翼 新規作成
@bar 2023/010/27(金) 林田翼 同一名前4
"""
import datetime
import discord
import platform
import pytz

from settings.settings_dict import settings_dict
from settings.database_id_list import database_id_list
from error_handling.error_message import ErrorMessage
from .notion import Notion
from .change_roll import check_cariculam
import re


def check_custom_format(author, input_string):
    # メッセージの送り主がボットかつ先頭6文字が「ignore」の場合はチェックしない
    if author.id == settings_dict["GUILD_ID"]["BOT"] and input_string[:6] == 'ignore':
        return True

    pattern = r'^\d{18,19}:(?:強制退会|受講中|自主退会|転職中|転職済)（[^\x00-\x7F]{1,7}_\d{5}）$'
    # パターンの説明:
    # ^ : 行の先頭
    # \d{18,19} : 18桁または19桁の数字
    # : : 半角コロン
    # (?:強制退会|受講中|自主退会|転職中|転職済) : リスト内のいずれかのテキスト
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


async def change_enrollment_status(message, logger, guild):
    logger.info("START change_enrollment_status: {}".format(message))

    try:
        logger.debug("error check: before loop: {}".format(message))
        if (message.author.display_name[-3:] == "@運営") or (message.author.id == settings_dict["GUILD_ID"]["BOT"]):

            # コマンドの解析（1126336516092858501:卒業済（石井晃_00001））
            command = message.content

            # コマンドチェック
            if check_custom_format(message.author, command) == False:
                reply = f'ignore\n'\
                        f'コマンドが間違っています。以下のフォーマットに当てはまるか再度ご確認ください。\n'\
                        f'18桁または19桁の数字 + 半角コロン + 強制退会|受講中|自主退会|転職中|転職済 のいずれか + 全角（ + 最大7文字の日本語 + 半角アンダースコア + 5桁の数字 + 全角）\n'
                await message.channel.send(reply)
            else:
                # username,database_id,enrollment_statusを取得する
                username = command.split('_')[0].split('（')[1]
                str = command.split('_')[1]
                if (str[:5] in database_id_list) == True:
                    database_id = database_id_list[str[:5]]
                    enrollment_status = command.split('（')[0].split(':')[1]
                    # user_idを取得する
                    user_id = command.split(':')[0]
                    # user_idとdatabase_idでユーザの特定
                    notion = Notion()
                    filter_dict = {'ユーザーID': user_id}
                    results_id = notion.select(database_id, filter_dict)
                    # 在籍状況を変更する
                    # 検索結果が一意に定まった時
                    if len(results_id) == 1:

                        # 取得先のIDを取得する
                        page_id = results_id[0]["id"]

                        filter_dicts_list = [
                            {'在籍状況': enrollment_status}
                        ]

                        logger.info('page_id: {}, filter_dicts_list: {}'.format(
                            page_id, filter_dicts_list))

                        notion.update(page_id=page_id,
                                      filter_dicts_list=filter_dicts_list)
                        now = datetime.datetime.now(
                            pytz.timezone('Asia/Tokyo'))

                        log_message = "ユーザID: {}, ユーザ名: {}, 在籍状況: {}, 更新日時: {}".format(
                            user_id, username, enrollment_status, now)
                        logger.info("アップデート成功: {}".format(log_message))

                        ## ロールを変更する処理 ##
                        member = discord.utils.get(
                            message.guild.members, id=int(user_id))
                        # 在籍状況が「受講中」の場合、カリキュラム番号から判別して「progate、udemy、ポートフォリオ」いずれかのロールをつける
                        if enrollment_status == "受講中":
                            for had_role in member.roles:
                                if had_role.name == "卒業生":
                                    await member.remove_roles(had_role)
                                    logger.info(
                                        f"role {had_role.name} has removed.")

                            curriculumNo = results_id[0]["properties"]["カリキュラムNo"]["rich_text"][0]["plain_text"]
                            role_name = check_cariculam(int(curriculumNo))
                            if role_name == "Portofolio":
                                role_name = "ポートフォリオ"
                            role = discord.utils.get(
                                message.guild.roles, name=f"{role_name}")
                            await member.add_roles(role)
                        elif enrollment_status == "転職中":
                            # 在籍状況が「転職中」の場合、「progate,udemy,ポートフォリオ」のロールを外して「卒業生」ロールを追加する
                            for had_role in member.roles:
                                if had_role.name == "Udemy" or had_role.name == "Progate" or had_role.name == "ポートフォリオ":
                                    await member.remove_roles(had_role)
                                    logger.info(
                                        f"role {had_role.name} has removed.")
                            role_graduation = discord.utils.get(
                                message.guild.roles, name="卒業生")
                            await member.add_roles(role_graduation)
                            logger.info(
                                f"role {role_graduation.name} has add.")
                        elif enrollment_status == "自主退会":
                            filter_dicts_list = [
                                {'請求状況': '請求書未送付'}
                            ]
                            notion.update(page_id=page_id,
                                          filter_dicts_list=filter_dicts_list)
                            # サーバからバンする
                            await member.ban(reason="自主退会のため。")
                            logger.info(f"{username}さんが自主退会のため、サーバからbanされました。")
                        elif enrollment_status == "強制退会":
                            filter_dicts_list = [
                                {'請求状況': '請求書送付済'}
                            ]
                            notion.update(page_id=page_id,
                                          filter_dicts_list=filter_dicts_list)
                        elif enrollment_status == "転職済":
                            filter_dicts_list = [
                                {'請求状況': '請求書未送付'}
                            ]
                            notion.update(page_id=page_id,
                                          filter_dicts_list=filter_dicts_list)

                        ## 返信処理 ##
                        # 受講中以外は解約のURLを返信する
                        if enrollment_status == "受講中" or enrollment_status == "転職済":
                            reply = f'ignore\n'\
                                    f"{username}さんの在籍状況を「{enrollment_status}」に変更しました。"
                            await message.channel.send(reply)
                        else:
                            target = ""
                            comment = ""
                            if enrollment_status == "強制退会":
                                # 運営陣をメンションする
                                target = '<@1093885923214753802>さん\n'\
                                         '<@888385794627235870>さん\n'\
                                         '<@683267456202047507>さん\n'\
                                         '<@1139466804973027378>さん\n'\
                                         '<@822444947994050601>さん\n'\
                                         '下記対応をおねがいします\n\n'
                            elif enrollment_status == "自主退会":
                                comment = f'{username}さんが自主退会のため、サーバからbanされました。\n'\
                                          'また、下記対応お願いします\n\n'
                            url = "https://admin.theapps.jp/client/paid.html"
                            id = "iconnect.2021.0928@gmail.com"
                            password = "iConnect20210928"
                            # 解約手順の資料
                            url_doc = "https://foam-dry-9b8.notion.site/The-Apps-a557e12ef66a4367a1c513edb0ac5ee6"
                            # 該当生徒のプラン情報を載せる
                            reply = f'ignore\n'\
                                    f'{target}{comment}{username}さんの在籍状況を「{enrollment_status}」に変更しました。\n'\
                                    f'解約ページはこちら ： {url}\n'\
                                    'ログイン情報\n'\
                                    f'メールアドレス：{id}\n'\
                                    f'パスワード：{password}\n'\
                                    f'解約手順はこちら ： {url_doc}'
                            await message.channel.send(reply)
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

    logger.info("END change_enrollment_status")
