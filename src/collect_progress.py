"""
@file collect_progress.py
@date 2023/07/31(月)
@author 藤原光基
@brief 進捗登録bot
@details 進捗コマンドに応じてnotion上の進捗管理DBに進捗率を登録する。
@bar 編集日時 編集者 編集内容
@bar 2023/07/31(月) 藤原光基 新規作成
@bar 2023/09/16(土) 藤原光基 同一名前4
"""
import datetime
import platform
import pytz

from settings.settings_dict import settings_dict
from settings.database_id_list import instructor_id_list
from error_handling.error_message import ErrorMessage
from .notion import Notion
# from .logger import Logger

from src import common


async def collect_progress(message, logger, guild):
    # async def collect_progress(message, guild):
    """
    logger_ = Logger()
    logger = logger_.get()
    """

    logger.info("START collect_progress: {}".format(message))

    try:
        logger.debug("error check: before loop: {}".format(message))
        if (message.author.display_name[-3:] != "@運営") & (message.author.id != settings_dict["GUILD_ID"]["BOT"]):

            error_message = ErrorMessage(logger)

            # コマンドに対応するデータを取得して表示
            username, database_id, curr_number = error_message.get_message(
                message)
            print(username, database_id, curr_number)
            error_announce = error_message.get_error_announce()

            user_id = str(message.author.id)

            logger.debug("error check: before check error_announce: {}, username: {}".format(
                message, username))
            if bool(error_announce):
                logger.error("username: {}, error_announce: {}".format(
                    username, error_announce))
                await message.channel.send(error_announce)
                return

            notion = Notion()

            filter_dict = {'ユーザーID': user_id}
            results_id = notion.select(database_id, filter_dict)

            # now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
            now = get_notion_datetime()

            logger.info("now: {}".format(now))
            logger.info("result_id: {}".format(results_id))
            logger.info("result_id length: {}".format(len(results_id)))

            filter_dicts_list = [{
                'カリキュラムNo': curr_number,
                'ユーザーID': user_id,
                # '進捗更新日時': now
                '進捗更新日時': now.strftime("%Y-%m-%d %H:%M:%S.%f")
            }]

            logger.info('filter_dicts_list(before): {}'.format(
                filter_dicts_list))
            curriculum_info = get_curriculum_info(curr_number)
            filter_dicts_list = add_dict(filter_dicts_list, curriculum_info)
            logger.info('filter_dicts_list(after): {}'.format(
                filter_dicts_list))

            # 検索結果が一意に定まった時
            if len(results_id) == 1:

                # 取得先のIDを取得する
                page_id = results_id[0]["id"]

                logger.info('page_id: {}, filter_dicts_list: {}'.format(
                    page_id, filter_dicts_list))

                notion.update(page_id=page_id,
                              filter_dicts_list=filter_dicts_list)
                log_message = "ユーザID: {}, ユーザ名: {}, カリキュラムNo: {}, 進捗更新日時: {}".format(
                    user_id, username, curr_number, now)

                if len(results_id[0]["properties"]["講師番号"]["rich_text"]) > 0:
                    instructor_id_key = results_id[0]["properties"]["講師番号"]["rich_text"][0]['text']['content']
                    instructor_id_indivisual = instructor_id_list[instructor_id_key]["id"]
                    instructor_id_whole = instructor_id_list["講師DB"]["id"]

                    results_id_instructor_indivisual = notion.select(instructor_id_indivisual, filter_dict)
                    page_id_instructor_indivisual = results_id_instructor_indivisual[0]["id"]
                    notion.update(page_id=page_id_instructor_indivisual, filter_dicts_list=filter_dicts_list)

                    results_id_instructor_whole = notion.select(instructor_id_whole, filter_dict)
                    page_id_instructor_whole = results_id_instructor_whole[0]["id"]
                    notion.update(page_id=page_id_instructor_whole, filter_dicts_list=filter_dicts_list)

                logger.info("アップデート成功: {}".format(log_message))

            # IDから結果の紐づけに失敗した場合
            elif len(results_id) == 0:

                results_name = notion.select(
                    database_id=database_id, filter_dict={'名前': username})

                logger.info("result_name: {}".format(results_name))
                logger.info("result_name length: {}".format(len(results_name)))

                # Notionテーブル内情報を名前から取得できない場合(新規参画者とみなす)
                if not results_name:

                    error_announce = "<@" + user_id + ">さん\n\n" +\
                                     "WorkReady加入時にご登録いただいたお名前とは\n" +\
                                     "異なるお名前を検知しました。\n" +\
                                     "お手数ですがサーバニックネームの設定をご確認の上、\n" +\
                                     "再度コマンドの入力をお願いいたします。\n\n" +\
                                     "なお、システム側で検知したサーバニックネームは下記の通りです。\n\n" +\
                                     " " + username + "\n\n" +\
                                     "上記内容に関しましてご不明点がございます場合は、\n" +\
                                     "お手数ですが担当エージェント様までご連絡いただきますようお願いいたします。"

                    await message.channel.send(error_announce)

                    log_message = "ユーザID: {}, ユーザ名: {}, カリキュラムNo: {}, 進捗更新日時: {}".format(
                        user_id, username, curr_number, now)
                    logger.error("result_id not found: {}".format(log_message))

                # 名前から一意なデータを抽出できた場合
                elif len(results_name) == 1:

                    # ユーザーIDを追加して更新する
                    page_id = results_name[0]["id"]

                    logger.info('page_id: {}, filter_dicts_list: {}'.format(
                        page_id, filter_dicts_list))

                    notion.update(page_id=page_id,
                                  filter_dicts_list=filter_dicts_list)

                    log_message = "ユーザID: {}, ユーザ名: {}, カリキュラムNo: {}, 進捗更新日時: {}".format(
                        user_id, username, curr_number, now)

                    if len(results_name[0]["properties"]["講師番号"]["rich_text"]) > 0:
                        instructor_id_key = results_name[0]["properties"]["講師番号"]["rich_text"][0]['text']['content']
                        instructor_id_indivisual = instructor_id_list[instructor_id_key]["id"]
                        instructor_id_whole = instructor_id_list["講師DB"]["id"]

                        results_name_instructor_indivisual = notion.select(instructor_id_indivisual, filter_dict)
                        page_id_instructor_indivisual = results_name_instructor_indivisual[0]["id"]
                        notion.update(page_id=page_id_instructor_indivisual, filter_dicts_list=filter_dicts_list)

                        results_name_instructor_whole = notion.select(instructor_id_whole, filter_dict)
                        page_id_instructor_whole = results_name_instructor_whole[0]["id"]
                        notion.update(page_id=page_id_instructor_whole, filter_dicts_list=filter_dicts_list)

                    logger.info("アップデート成功: {}".format(log_message))

                # 同一テーブル内に同一名称で登録されている人物が複数人存在する場合
                else:
                    # ギルド内(WorkReady内)で進捗報告者と同一名称者を抽出する
                    # (WorkReady内にも同一名称者が複数存在するとみなす)
                    user_list = []
                    for member in guild.members:
                        if member.display_name[:len(username)] == username:
                            user_list.append(member)

                    # ギルド内同一名称者と、notion内同一名称者を登録時刻でソートする
                    user_list_sort_by_joined_at = sorted(
                        user_list, key=lambda user: user.joined_at)
                    result_list_sort_by_created_dt = sorted(
                        results_name, key=lambda result: result['created_time'])

                    # 進捗報告者とギルド内同一名称者のギルド参画日時を比較し、
                    # 同一の参画日時に該当する人物データとNotion内同一名称者と「同番地」の
                    # 人物を同一人物とみなす。
                    for idx, user_info in enumerate(user_list_sort_by_joined_at):
                        if user_info.joined_at == message.author.joined_at:
                            result = result_list_sort_by_created_dt[idx]
                            break

                    # notionの対象人物にユーザーIDを追加してnotionを更新する
                    page_id = result["id"]

                    logger.info('page_id: {}, filter_dicts_list: {}'.format(
                        page_id, filter_dicts_list))

                    notion.update(page_id=page_id,
                                  filter_dicts_list=filter_dicts_list)

                    log_message = "ユーザID: {}, ユーザ名: {}, カリキュラムNo: {}, 進捗更新日時: {}".format(
                        user_id, username, curr_number, now)

                    if len(result[0]["properties"]["講師番号"]["rich_text"]) > 0:
                        instructor_id_key = result[0]["properties"]["講師番号"]["rich_text"][0]['text']['content']
                        instructor_id_indivisual = instructor_id_list[instructor_id_key]["id"]
                        instructor_id_whole = instructor_id_list["講師DB"]["id"]

                        result_instructor_indivisual = notion.select(instructor_id_indivisual, filter_dict)
                        page_id_instructor_indivisual = result_instructor_indivisual[0]["id"]
                        notion.update(page_id=page_id_instructor_indivisual, filter_dicts_list=filter_dicts_list)

                        result_instructor_whole = notion.select(instructor_id_whole, filter_dict)
                        page_id_instructor_whole = result_instructor_whole[0]["id"]
                        notion.update(page_id=page_id_instructor_whole, filter_dicts_list=filter_dicts_list)

                    logger.info("アップデート成功: {}".format(log_message))

        # else:
        #     return

    except Exception as e:
        command = message.content
        get_messemger_name = message.author.display_name
        err_line = 'command: {}, error message: {}, username: {}'.format(
            command, e, get_messemger_name)
        logger.error(err_line)

    logger.info("END collect_progress")


def get_curriculum_info(cariculam_number):
    cariculam_number_int = int(cariculam_number)

    if settings_dict["CURRICULUM_NUMBER_RANGE"]["PROGATE"]["MIN"] <= cariculam_number_int <= settings_dict["CURRICULUM_NUMBER_RANGE"]["PROGATE"]["MAX"]:
        cariculam_name = 'Progate'
        progress_rate = str(int((cariculam_number_int - settings_dict["CURRICULUM_NUMBER_RANGE"]["PROGATE"]["MIN"]) /
                                (settings_dict["CURRICULUM_NUMBER_RANGE"]["PROGATE"]["MAX"] - settings_dict["CURRICULUM_NUMBER_RANGE"]["PROGATE"]["MIN"]) * settings_dict["CURRICULUM_GUIDELINE_DATE_RANGE"]["PROGATE"]["PERCENTAGE"]))

    # 「/curr 021 ~ 326」→ ロール名:「Udemy」
    elif settings_dict["CURRICULUM_NUMBER_RANGE"]["UDEMY"]["MIN"] <= cariculam_number_int <= settings_dict["CURRICULUM_NUMBER_RANGE"]["UDEMY"]["MAX"]:
        cariculam_name = 'Udemy'
        progress_rate = str(int((cariculam_number_int - settings_dict["CURRICULUM_NUMBER_RANGE"]["UDEMY"]["MIN"]) /
                                (settings_dict["CURRICULUM_NUMBER_RANGE"]["UDEMY"]["MAX"] - settings_dict["CURRICULUM_NUMBER_RANGE"]["UDEMY"]["MIN"]) * settings_dict["CURRICULUM_GUIDELINE_DATE_RANGE"]["UDEMY"]["PERCENTAGE"]) + settings_dict["CURRICULUM_GUIDELINE_DATE_RANGE"]["PROGATE"]["PERCENTAGE"])

    # 「/curr 327」→ ロール名:「ポートフォリオ」
    elif settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MIN"] <= cariculam_number_int <= settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MAX"]:
        cariculam_name = 'ポートフォリオ'
        progress_rate = str(int((cariculam_number_int - settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MIN"]) /
                                (settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MAX"] - settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MIN"]) * settings_dict["CURRICULUM_GUIDELINE_DATE_RANGE"]["PORTOFOLIO"]["PERCENTAGE"]) + settings_dict["CURRICULUM_GUIDELINE_DATE_RANGE"]["PROGATE"]["PERCENTAGE"] + settings_dict["CURRICULUM_GUIDELINE_DATE_RANGE"]["UDEMY"]["PERCENTAGE"])

    # 上記以外は「Unknown」を返す
    # (基本ここに該当するコマンドは既にエラーとなっているため、ここまで来ないはず)
    else:
        cariculam_name = 'Unknown'
        progress_rate = '-'

    curriculum_info = {
        'カリキュラム名': cariculam_name,
        'カリキュラム進捗(%)': progress_rate
    }

    return curriculum_info


def add_dict(filter_dicts_list, curriculum_info):
    filter_dict = filter_dicts_list[0]
    for key, value in curriculum_info.items():
        filter_dict[key] = value
    return [filter_dict]

def get_notion_datetime():
    now = common.get_unit_datetime()
    now_notion = now - datetime.timedelta(hours=9)
    return now_notion