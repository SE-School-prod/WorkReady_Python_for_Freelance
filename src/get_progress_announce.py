##
# @file get_progress_announce.py
# @date 2023/08/07(月)
# @author 藤原光基
# @brief 進捗に関する通知機能(DM or メール)
# @details 過去のメッセージを取得することで、直近の進捗状況を取得する。
# @details 現在下記botを本機能より実装予定。
# @details ・進捗ランキング機能: 毎週月曜日に、先週で進捗の進み具合が良い人たちを展開する。
# @details ・催促DM送信機能: 進捗報告が3日間確認できない場合、専用のDMメッセージを対象者に送信する。
# @details ・バン警告DM送信機能: 進捗報告が1週間確認できない場合、専用のDMメッセージを対象者に送信する。
# @details ・最終警告DM送信機能: 進捗報告が12日間確認できない場合、専用のDMメッセージを対象者に送信する。
# @details ・強制バン機能: 進捗報告が2週間確認できない場合、対象者に支払メールを送信し、強制バンを実施する。
# @bar 編集日時 編集者 編集内容
# @bar 2023/08/07(月) 藤原光基 新規作成
# @bar 2023/09/23(土) 藤原光基 全ての機能を一まとめにして、メッセージ送信手段をDMに変更する
##

import discord
import datetime
# from pytz import timezone
import pytz
import platform

from settings.settings_dict import settings_dict
# from settings.database_id_list import database_id_list
from src.mail import Mail
from src import common

"""
from .logger import Logger

logger_ = Logger()
logger = logger_.get()
"""

# async def get_messages_info(guild, after=None, before=None):


async def get_messages_info(guild, logger, after=None, before=None):

    logger.info('START get_messages_info')

    channel = discord.utils.get(
        guild.channels, name="進捗報告（日報）")  # できればnameではなくidで指定したい
    messages = [message async for message in channel.history(limit=None, after=after, before=before)]
    bans = [entry.user.id async for entry in guild.bans()]
    print("bans: ", bans)

    guild_member_info_dict = {}

    for member in channel.guild.members:
        guild_member_info_dict[member.id] = {}
        guild_member_info_dict[member.id]["name"] = member.name
        guild_member_info_dict[member.id]["joined_at"] = member.joined_at
        guild_member_info_dict[member.id]["is_bot"] = member.bot
        guild_member_info_dict[member.id]["is_graduator"] = "卒業生" in [
            role.name for role in member.roles]
        guild_member_info_dict[member.id]["is_moderator"] = "モデレーター" in [
            role.name for role in member.roles]
        guild_member_info_dict[member.id]["is_admin"] = "管理者" in [
            role.name for role in member.roles]
        guild_member_info_dict[member.id]["is_portofolio"] = "ポートフォリオ" in [
            role.name for role in member.roles]
        guild_member_info_dict[member.id]["is_standard"] = "Standard" in [
            role.name for role in member.roles]
        guild_member_info_dict[member.id]["is_premium"] = "Premium" in [
            role.name for role in member.roles]
        guild_member_info_dict[member.id]["is_ban"] = False if not member.id in bans else True

        # print(member.id)
        if member.id in bans:
            print(member.id, member.name)

    for message in messages:
        try:
            if message.author.name != "Deleted User":
                user_info = guild_member_info_dict[message.author.id]
                if not (user_info["is_bot"] or user_info["is_moderator"] or user_info["is_admin"] or user_info["is_graduator"] or user_info["is_ban"]):
                    guild_member_info_dict[message.author.id]["display_name"] = message.author.display_name
                    if not "message" in guild_member_info_dict[message.author.id].keys():
                        guild_member_info_dict[message.author.id]["message"] = {
                        }
                        guild_member_info_dict[message.author.id]["message"]["init"] = {
                        }
                        guild_member_info_dict[message.author.id]["message"]["init"][
                            "date"] = message.created_at if message.edited_at is None else message.edited_at
                        guild_member_info_dict[message.author.id]["message"]["init"]["content"] = message.content
                    else:
                        guild_member_info_dict[message.author.id]["message"]["last"] = {
                        }
                        guild_member_info_dict[message.author.id]["message"]["last"][
                            "date"] = message.created_at if message.edited_at is None else message.edited_at
                        guild_member_info_dict[message.author.id]["message"]["last"]["content"] = message.content
        except Exception as e:
            logger.error(e)

    logger.info('END get_messages_info')

    return guild_member_info_dict


##
# @func progress_ranking
# @brief 過去1週間の間での進捗ランキングを表示する
# @param guild Discord上のWorkReadyについての情報
# @param member_info_dict 進捗報告(日報)チャンネルにおける、過去のメッセージ情報(1週間)
# @param member_info_dict_last_week 進捗報告(日報)チャンネルにおける、過去のメッセージ情報(2週間)
# @details member_info_dict(辞書型)には(1週間前月曜日0:0:00~昨日23:59:59)のメッセージ情報が、
# @details member_info_dict_through_week_ago(辞書型)には(2週間前月曜日0:0:00~2週間前日曜日23:59:59)のメッセージ情報がそれぞれ含まれる。
# @details 具体的には、過去メッセージを発信した(進捗報告を行った)人のキーには「message」が追加される。
# @details この「message」キーが存在するか否かで判定し、無いitemを結果格納用辞書変数(target_member)に追加する。
# @details 上記「2週間前」の最終メッセージから「1週間前」の最終メッセージを取得し、
# @details その中の数字部分を比較して数値が大きい順に生徒名を出力する。
# @details その後、この中でprogate修了者、udemy修了者は別途出力する。
# @note member_info_dict, member_info_dict_through_week_ago出力元の関数は
##
# async def progress_ranking(guild, member_info_dict, member_info_dict_last_week):
async def progress_ranking(guild, logger, member_info_dict, member_info_dict_last_week):

    # 進捗ランキング開始メッセージ出力(プロンプト上)
    logger.info('START progress_ranking')

    try:
        # 結果メッセージ出力用チャンネル指定
        channel = discord.utils.get(guild.channels, name="進捗報告（日報）")  # server

        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

        # ランキング対象者(最低2回以上進捗報告を行った生徒)の情報を抽出
        target_member_with_id = {}
        for id, member in member_info_dict.items():
            if "message" in member.keys():
                target_member_with_id[id] = {}
                target_member_with_id[id]["name"] = member["display_name"]
                target_member_with_id[id]["init"] = member["message"]["init"]

                if "last" in member["message"].keys():
                    target_member_with_id[id]["last"] = member["message"]["last"]
                elif now - member["joined_at"] < datetime.timedelta(days=7):
                    target_member_with_id[id]["last"] = target_member_with_id[id]["init"]
                    target_member_with_id[id]["init"]["date"] = ""
                    target_member_with_id[id]["init"]["content"] = "/curr 0"

        # 1週間前に進捗登録した全コマンド情報を全て列挙
        # TODO 先週にudemyが完了したパターン(先週進捗報告1回以上、今週進捗報告なし↔is_portofolioがTrueの場合が抜けあり)
        # TODO 参加後しばらくして、先週進捗報告せず、今週進捗報告を1回のみしたパターンが抜けている
        for id, member in member_info_dict_last_week.items():
            if id in target_member_with_id.keys():
                if "message" in member.keys():
                    if "last" in member["message"].keys():

                        # 先週進捗報告2回以上 & 今週進捗報告2回以上
                        if "last" in target_member_with_id[id].keys():
                            target_member_with_id[id]["init"] = member["message"]["last"]

                        # 先週進捗報告2回以上 & 今週進捗報告1回のみ
                        else:
                            target_member_with_id[id]["last"] = target_member_with_id[id]["init"].copy(
                            )
                            target_member_with_id[id]["init"] = member["message"]["last"]
                    else:
                        # 先週進捗報告1回のみ & 今週進捗報告2回以上
                        if "last" in target_member_with_id[id].keys():
                            target_member_with_id[id]["init"] = member["message"]["init"]

                        # 先週進捗報告1回のみ & 今週進捗報告0回(ポートフォリオ)
                        elif not "init" in target_member_with_id[id].keys():
                            if "last" in member["message"].keys():
                                target_member_with_id[id]["init"] = member["message"]["last"].copy(
                                )
                                target_member_with_id[id]["last"] = member["message"]["last"].copy(
                                )
                            else:
                                target_member_with_id[id]["init"] = member["message"]["init"].copy(
                                )
                                target_member_with_id[id]["last"] = member["message"]["init"].copy(
                                )

                        # 先週進捗報告1回のみ & 今週進捗報告1回のみ
                        else:
                            target_member_with_id[id]["last"] = target_member_with_id[id]["init"].copy(
                            )
                            target_member_with_id[id]["init"] = member["message"]["init"]

                # 2週間前の捗進捗報告0回の場合
                else:
                    # 新規参画者の場合(進捗報告は0からスタート)
                    if now - member["joined_at"] < datetime.timedelta(days=7):
                        if not "last" in target_member_with_id[id].keys():
                            target_member_with_id[id]["last"] = target_member_with_id[id]["init"].copy(
                            )
                        target_member_with_id[id]["init"]["date"] = member_info_dict[id]["joined_at"]
                        target_member_with_id[id]["init"]["content"] = "/curr 0"

                    # 純粋に進捗報告を行わなかった場合
                    else:
                        # 先週の進捗報告が1回の場合(進捗率0) [本分岐のelseは今週2回以上進捗報告しているはずで、その区間で進捗率を算出する]
                        if not "last" in target_member_with_id[id].keys():
                            target_member_with_id[id]["last"] = target_member_with_id[id]["init"].copy(
                            )

        target_member = {}
        for member in target_member_with_id.values():
            target_member[member["name"]] = {}
            target_member[member["name"]]["init"] = member["init"]
            target_member[member["name"]]["init"]["val"] = int(
                member["init"]["content"][6:])
            target_member[member["name"]]["last"] = member["last"]
            target_member[member["name"]]["last"]["val"] = int(
                member["last"]["content"][6:])
            diff = abs(int(member["last"]["content"][6:]) -
                       int(member["init"]["content"][6:]))
            target_member[member["name"]]["diff"] = diff

        target_member_after = dict(
            sorted(target_member.items(), key=lambda item: item[1]["diff"], reverse=True))

        # progate,udemy修了者格納用変数初期化
        finished_member_progate = {}
        finished_member_udemy = {}
        finished_member_portfolio = {}

        # 進捗ランキングメッセージ生成
        message = "## 【今週の進捗ランキング】\n"
        for rank, (name, member_info) in enumerate(target_member_after.items()):
            if "_" in name:
                idx = name.index("_")
                name = name[:idx]
            message += "第" + str(rank+1) + "位: " + name + "さん  "
            message += str(member_info["init"]["val"]) + " → " + str(
                member_info["last"]["val"]) + " (進捗数: " + str(member_info["diff"]) + ")"
            if member_info["init"]["val"] < settings_dict["CURRICULUM_NUMBER_RANGE"]["UDEMY"]["MIN"] and settings_dict["CURRICULUM_NUMBER_RANGE"]["UDEMY"]["MIN"] <= member_info["last"]["val"]:
                finished_member_progate[name] = member_info
            elif member_info["init"]["val"] < settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MIN"] and settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MIN"] <= member_info["last"]["val"]:
                finished_member_udemy[name] = member_info
            elif member_info["last"]["val"] == settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MAX"]:
                finished_member_portfolio[name] = member_info
            message += "\n"

        message += "\n"
        if len(finished_member_progate) > 0:
            message += "【Progate修了者】\n"
            for name in finished_member_progate.keys():
                message += name + "さん\n"
            message += "\n"

        if len(finished_member_udemy) > 0:
            message += "【Udemy修了者】\n"
            for name in finished_member_udemy.keys():
                message += name + "さん\n"
            message += "\n"

        if len(finished_member_portfolio) > 0:
            message += "【ポートフォリオ修了者】\n"
            for name in finished_member_portfolio.keys():
                message += name + "さん\n"
            message += "\n"

        message += "\n"
        message += "皆さま、すごいです！\nこの調子でどんどん頑張りましょう!!"
        message += "\n\n--------------------------------------------------------------------------\n"

        logger.info('message:\n\n***\n\n{}\n\n***'.format(message))

    except Exception as e:
        logger.error(e)

    # 上記メッセージ出力
    # await channel.send(message)
    logger.info('END progress_ranking')


async def progress(bot, member_info_through_week_ago, logger):
    # async def progress(bot, member_info_through_week_ago):

    logger.info('START progress')

    # 「WorkReady」内情報取得
    guild = bot.get_guild(settings_dict["GUILD_ID"]["GUILD"])

    ban_ids = []
    async for entry in guild.bans():
        ban_ids.append(entry.user.id)
        # print(entry.user, entry.user.id)

    # WorkReady内メンバー一覧情報取得
    members = guild.members
    logger.info('member length:{}'.format(len(members)))

    # WorkReady加入者(8/16)
    exec_threshould_date = datetime.datetime(
        2023, 8, 16, 0, 0, 0, tzinfo=datetime.timezone.utc)  # debug

    # 処理基準判定時刻
    # (この変数から何日経過したかで処理を決定する)
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

    log_message = ""

    # WorkReady内メンバーを一人ずつ(bot込みで)取得
    for member in members:

        try:

            # メンバーのユーザID取得
            log_message += "id:{}, name:{}, display_name:{}\n".format(
                member.id, member.name, member.display_name)
            id = member.id
            # print("id:{}, name:{}, display_name:{}\n".format(member.id, member.name, member.display_name))

            if id in ban_ids:
                print("already baned.")
                continue

            # WorkReady内メンバーが「進捗報告（日報）」チャンネルでコメントしているか
            if id in member_info_through_week_ago.keys():

                # 進捗報告（日報）チャンネルと同期
                member_info = member_info_through_week_ago[id]

                # 対象メンバーが「受講生」か否か
                if not (member_info["is_bot"]
                        or member_info["is_moderator"]
                        or member_info["is_admin"]
                        or member_info["is_graduator"]
                        # or member_info["is_portofolio"]
                        or member_info["is_standard"]
                        or member_info["is_premium"]
                        or member_info["is_ban"]):

                    # 対象メンバーが「進捗DM送信対象者」か
                    # (WorkReady加入日が「2023/08/16」以降か)
                    if member_info["joined_at"] > exec_threshould_date:

                        ############## 実際の処理 ##############

                        # # 「進捗報告（日報）」チャンネルでコメントしているか
                        if "message" in member_info.keys():

                            # 最終コメント日時取得
                            if "last" in member_info["message"]:
                                last_report_date = member_info["message"]["last"]["date"]
                            else:
                                last_report_date = member_info["message"]["init"]["date"]

                            diff_date = now - last_report_date

                        else:
                            diff_date = now - member_info["joined_at"]

                        past_date = now - member_info["joined_at"]

                        # 最後に進捗報告を行ったのが3日未満の場合、何もしない
                        if diff_date < datetime.timedelta(days=3):

                            member_display_name = member.display_name
                            print("member_display_name: ", member_display_name)
                            member_name = member_display_name.split("_")[0]
                            log_message += "  name: {}, date: {}, exe: {}\n\n".format(
                                member_name, diff_date, "pass")

                        # 最後に進捗報告を行ったのが3日前の場合、「進捗報告催促DM送信処理」を実施する
                        elif datetime.timedelta(days=3) <= diff_date < datetime.timedelta(days=4):

                            # exe_mode = "NOTIFY"
                            exe_mode = '3DAYS'
                            await sending_progres_info(bot, member, exe_mode)

                            # log_message += "  notify direct message send has completed.\n\n"
                            log_message += "  3day direct message send has completed.\n\n"

                        # 最後に進捗報告を行ったのが7日前の場合、「進捗報告警告DM送信処理」を実施する
                        elif datetime.timedelta(days=7) <= diff_date < datetime.timedelta(days=8):

                            # exe_mode = "WARNING"
                            exe_mode = "1WEEK"
                            await sending_progres_info(bot, member, exe_mode)

                            # log_message += "  warning direct message send has completed.\n\n"
                            log_message += "  1week direct message send has completed.\n\n"

                        # 最後に進捗報告を行ったのが12日前の場合、「進捗報告最終通告DM送信処理」を実施する
                        # elif datetime.timedelta(days=12) <= diff_date < datetime.timedelta(days=13):
                        elif datetime.timedelta(days=10) <= diff_date < datetime.timedelta(days=11):

                            # exe_mode = "ULTIMATUM"
                            exe_mode = "10DAYS"
                            await sending_progres_info(bot, member, exe_mode)

                            # log_message += "  ultimatum direct message send has completed.\n\n"
                            log_message += "  10day direct message send has completed.\n\n"

                        # 最後に進捗報告を行ったのが2週間前の場合、「WorkReady除籍処理」を実施する
                        # (違約金支払いメール、WorkReadyバン処理)
                        # elif datetime.timedelta(days=15) <= diff_date:

                        #     exe_mode = "BAN"
                        #     await sending_progres_info(bot, member, exe_mode)
                        #     log_message += "  ban execution and mail send has completed.\n\n"
                        elif datetime.timedelta(days=14) <= diff_date < datetime.timedelta(days=15):

                            # exe_mode = "BAN"
                            exe_mode = "2WEEKS"
                            await sending_progres_info(bot, member, exe_mode)

                            # log_message += "  ban execution and mail send has completed.\n\n"
                            log_message += "  2week direct message send has completed.\n\n"

                        else:
                            member_display_name = member.display_name
                            print("member_display_name: ", member_display_name)
                            member_name = member_display_name.split("_")[0]
                            log_message += "  name: {}, date: {}, exe: {}\n\n".format(
                                member_name, diff_date, "other")
                            exe_mode = "other"
                        print("  name: {}, init-date: {}, now-date: {}, report-date: {}, exe: {}\n".format(member_name, member_info["message"]["init"]["date"], member_info["message"]["last"]["date"], diff_date, exe_mode))


                        # 入校してから1カ月が経過した場合、「入校経過時間報告連絡処理」を実施する
                        if datetime.timedelta(days=32) <= past_date < datetime.timedelta(days=33):

                            exe_mode = '1MONTH'
                            await sending_progres_info(bot, member, exe_mode)

                            log_message += "  1month direct message send has completed.\n\n"

                        # 入校してから2カ月が経過した場合、「入校経過時間報告連絡処理」を実施する
                        elif datetime.timedelta(days=63) <= past_date < datetime.timedelta(days=64):

                            exe_mode = '2MONTH'
                            await sending_progres_info(bot, member, exe_mode)

                            log_message += "  2month direct message send has completed.\n\n"

                        # 入校してから3カ月が経過した場合、「入校経過時間報告連絡処理」を実施する
                        elif datetime.timedelta(days=94) <= past_date < datetime.timedelta(days=95):

                            exe_mode = '3MONTH'
                            await sending_progres_info(bot, member, exe_mode)

                            log_message += "  3month direct message send has completed.\n\n"

                        # 入校してから4カ月が経過した場合、「入校経過時間報告連絡処理」を実施する
                        elif datetime.timedelta(days=125) <= past_date < datetime.timedelta(days=126):

                            exe_mode = "4MONTH"
                            await sending_progres_info(bot, member, exe_mode)

                            log_message += "  4month direct message send has completed.\n\n"

                        else:
                            member_display_name = member.display_name
                            print("member_display_name: ", member_display_name)
                            member_name = member_display_name.split("_")[0]
                            log_message += "  name: {}, date: {}, exe: {}\n\n".format(
                                member_name, past_date, "other")
                            exe_mode = "other"
                        print("  name: {}, init-date: {}, now-date: {}, report-date: {}, exe: {}\n".format(member_name, member_info["joined_at"], now, diff_date, exe_mode))

                    else:
                        log_message += "  joined_at: {}, thre_date: {}\n\n".format(
                            member_info["joined_at"], exec_threshould_date)

                else:
                    log_message += "  is_bot: {}, is_moderator: {}, is_admin: {}, is_graduator: {}, is_portofolio: {}\n\n".format(
                        member_info["is_bot"], member_info["is_moderator"], member_info["is_admin"], member_info["is_graduator"], member_info["is_portofolio"])

            else:
                log_message += "  id not found in member_info.\n\n"

        except Exception as e:
            logger.error(e)
            continue

    logger.info('progress result:\n\n***\n{}***\n'.format(log_message))
    logger.info('END progress')


async def sending_progres_info(bot, member, exe_mode):
    print("sending_progres_info")
    from src.mail import Mail

    mail = Mail()

    chat_mail = {'name': 'メール送付報告', 'id': 1183741670248955997}
    chat_dm = {'name': 'dm送付報告', 'id': 1183741103107756082}

    guild = discord.utils.get(
        bot.guilds, id=settings_dict["GUILD_ID"]["GUILD"])
    channel_status = guild.get_channel(
        settings_dict["GUILD_ID"]["CHANNEL_ID_ENOROLLMENT_STATUS"])

    channel_mail = guild.get_channel(chat_mail["id"])
    channel_dm = guild.get_channel(chat_dm['id'])

    # TODO:
    id = member.id
    name_with_dbid = member.display_name
    name = name_with_dbid.split("_")[0]
    print(f"id: {id}, name(display): {name_with_dbid}, name: {name}")

    user = bot.get_user(id)
    print("user: ", user)
    print("exe_mode: ", exe_mode)

    # 対象が高校生(やまcさん？)の場合、処理をスキップ
    if id == 1044823685237837947 or id == 991088543680057394:
        print("pass")
        pass

    else:
        if    ((exe_mode == "3DAYS")
           or  (exe_mode == "1WEEK")
           or  (exe_mode == "10DAYS")
           or (exe_mode == "2WEEKS")):
            mail.send_mail(name_with_dbid, str(id), exe_mode)
            await channel_mail.send(common.return_mail_content(exe_mode, name))
            print("mail (" + exe_mode + ") send")

            await user.send(common.get_dm_content(exe_mode, name))
            await channel_dm.send(common.return_dm_content(exe_mode, name))
            print("dm (" + exe_mode + ") send")

        elif  ((exe_mode == "1MONTH")
           or  (exe_mode == "2MONTH")
           or  (exe_mode == "3MONTH")
           or  (exe_mode == "4MONTH")):
            mail.send_mail(name_with_dbid, str(id), exe_mode)
            await channel_mail.send(common.return_mail_past_content(exe_mode, name))
            print("mail (" + exe_mode + ") send")

            await user.send(common.get_dm_content(exe_mode, name))
            await channel_dm.send(common.return_dm_past_content(exe_mode, name))
            print("dm (" + exe_mode + ") send")

    print("executed")



async def check_mails(bot, member):

    exe_modes = [
        "3DAYS", "1WEEK", "10DAYS", "2WEEKS", "1MONTH", "2MONTH", "3MONTH", "4MONTH"
    ]

    for exe_mode in exe_modes:
        await sending_progres_info(bot, member, exe_mode)