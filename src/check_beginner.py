"""
@file check_beginner.py
@date 2023/10/23(月)
@author 藤原光基
@brief 新規ユーザ確認bot
@details 1日に1回生徒の習熟期間を検知し、
@details 4ヵ月経過した生徒のロールを「Starter(無料)」→「Standard(有料)」に自動変更する。
@note TODO 退会→再入会した際の対策
@bar 編集日時 編集者 編集内容
@bar 2023/10/23(月) 藤原光基 新規作成
"""

import discord

from .notion import Notion
from error_handling.error_message import ErrorMessage
from settings.settings_dict import settings_dict
from settings.database_id_list import database_id_list, instructor_id_list


async def check_beginner(message, logger, guild):
    logger.info("START check_beginner")
    logger.info("message: {}, content: {}".format(message, message.content))

    try:
        role_add_flag = True
        role_progate = discord.utils.get(message.guild.roles, name="Progate")
        role_beginner = discord.utils.get(message.guild.roles, name="Beginner")

        for had_role in message.author.roles:
            if ((had_role.name == "Progate")
                or (had_role.name == "Udemy")
                    or (had_role.name == "ポートフォリオ")):
                role_add_flag = False
                break

        logger.info("role_add_flag: {}".format(role_add_flag))

        if role_add_flag:
            error_message = ErrorMessage(logger)
            err_message, err_announce = error_message._check_user(message)

            if err_announce is not None:
                logger.error(err_message)
                err_announce = "<@" + str(message.author.id) + ">さん\n\n" +\
                    err_announce + "\n\n"\
                    "なお、運営側で検知しているサーバニックネームは下記のとおりです。\n" +\
                    "  ・サーバニックネーム: " + message.author.display_name + "\n\n"\
                    "上記内容に関しましてご不明点がございます場合は、\n" +\
                    "お手数ですが担当エージェント様までご連絡いただきますようお願いいたします。"
                await message.channel.send(err_announce)

            else:
                notion = Notion()

                [username, database_key] = message.author.display_name.split("_")
                database_id = database_id_list[database_key]

                results_name = notion.select(
                    database_id=database_id, filter_dict={'名前': username})

                logger.info("results_name: {}".format(results_name))

                if len(results_name) == 0:
                    err_announce = "<@" + str(message.author.id) + ">さん\n\n" +\
                        "WorkReady加入時にご登録いただいたお名前とは\n" +\
                        "異なるお名前を検知しました。\n" +\
                        "お手数ですがサーバニックネームの設定をご確認の上、\n" +\
                        "再度コマンドの入力をお願いいたします。\n\n" +\
                        "なお、システム側で検知した情報は下記の通りです。\n\n" +\
                        " ・サーバニックネーム: " + username + "\n" +\
                        " ・エージェント様対応No: " + database_key + "\n\n"\
                        "上記内容に関しましてご不明点がございます場合は、\n" +\
                        "お手数ですが担当エージェント様までご連絡いただきますようお願いいたします。"

                    await message.channel.send(err_announce)

                else:

                    # 名前から一意なデータを抽出できた場合
                    if len(results_name) == 1:

                        # ユーザーIDを追加して更新する
                        page_id = results_name[0]["id"]

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

                    print("roles: ", message.author.roles)
                    for had_role in message.author.roles:
                        role_name = had_role.name
                        if role_name[:2] == "講師":
                            print("構成ロール名: ", role_name)
                            instructor_id_key = role_name[2:7]
                            instructor_id = instructor_id_list[instructor_id_key]["id"]
                            break


                    """
                    instructor_id_key = create_notion_instructor_info(message)

                    role_name_instructor = "講師" + instructor_id_key + \
                        "_" + instructor_id_list[instructor_id_key]["name"]
                    print("role_name_instructor: ", role_name_instructor)

                    role_instructor = discord.utils.get(message.guild.roles, name=role_name_instructor)
                    await message.author.add_roles(role_instructor)
                    """
                    filter_dict_indivisual = {
                        "名前": username,
                        "代理店番号": database_key,
                        "カリキュラムNo": "0",
                        "カリキュラム名": "progate",
                        "カリキュラム進捗(%)": "0",
                        "ユーザーID": str(message.author.id),
                        "在籍状況": "受講中",
                        "請求書送付状況": "請求書未送付",
                        "30分無料相談チケット": 2,
                        "30分有料相談チケット": 0,
                        "60分有料相談チケット": 0,
                        "受講コース": 'Python',
                    }

                    filter_dict_whole = filter_dict_indivisual.copy()
                    filter_dict_whole["講師番号"] = instructor_id_key

                    notion.create(database_id=instructor_id, filter_dicts_list=[filter_dict_indivisual])
                    notion.create(database_id=instructor_id_list["講師DB"]["id"], filter_dicts_list=[filter_dict_whole])

                    notion_update_filter = [{"ユーザーID": str(message.author.id), "講師番号": instructor_id_key, "受講コース": "Python"}]
                    notion.update(page_id=page_id, filter_dicts_list=notion_update_filter)

                    await message.author.remove_roles(role_beginner)
                    await message.author.add_roles(role_progate)
                    logger.info("role {} has add.".format("Progate"))

                    # await message.delete()
                    messages = [message async for message in message.channel.history(limit=None)]

                    for message in messages:
                        # await message.delete()
                        if not (message.id == 1192816035305361498):
                            await message.delete()

        else:
            logger.info("END check_beginner due to flag")

    except Exception as e:
        logger.error(e)
