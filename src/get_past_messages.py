##
# @file get_past_messages.py
# @date 2023/08/07(月)
# @author 藤原光基
# @brief 過去のメッセージ取得機能
# @details 過去のメッセージを取得することで、直近の進捗状況を取得する。
# @details 現在下記botを本機能より実装予定。
# @details ・進捗ランキング機能: 毎週月曜日に、先週で進捗の進み具合が良い人たちを展開する。
# @details ・キック警告機能: 毎週月曜日に、先週進捗報告が無い人を展開する。
# @details ・強制キック機能: 隔週月曜日に、2週間全く進捗報告がない人をキックする。その後キックした旨、および請求する旨を記載したメールを本人に送る。
# @bar 編集日時 編集者 編集内容
# @bar 2023/08/07(月) 藤原光基 新規作成
##

import discord
import datetime
# from pytz import timezone
import pytz
import platform

from settings.guild_id_dict import guild_id_dict
from settings.database_id_list import database_id_list


async def get_messages_info(guild, after=None, before=None):

    channel = discord.utils.get(
        guild.channels, name="進捗報告（日報）")  # できればnameではなくidで指定したい
    messages = [message async for message in channel.history(limit=None, after=after, before=before)]

    guild_member_info_dict = {}

    for member in channel.guild.members:
        guild_member_info_dict[member.id] = {}
        guild_member_info_dict[member.id]["name"] = member.name
        guild_member_info_dict[member.id]["joined_at"] = member.joined_at
        guild_member_info_dict[member.id]["is_bot"] = member.bot
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

    for message in messages:
        if message.author.name != "Deleted User":
            user_info = guild_member_info_dict[message.author.id]
            if not (user_info["is_bot"] or user_info["is_moderator"] or user_info["is_admin"]):
                guild_member_info_dict[message.author.id]["display_name"] = message.author.display_name
                if not "message" in guild_member_info_dict[message.author.id].keys():
                    guild_member_info_dict[message.author.id]["message"] = {}
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
async def progress_ranking(guild, member_info_dict, member_info_dict_last_week):

    # 進捗ランキング開始メッセージ出力(プロンプト上)
    print("progress_ranking start...")

    # 結果メッセージ出力用チャンネル指定
    channel = discord.utils.get(
        guild.channels, name="進捗報告（日報）")  # できればnameではなくidで指定したい
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

    # 進捗ランキングメッセージ生成
    message = "## 【今週の進捗ランキング】\n"
    for rank, (name, member_info) in enumerate(target_member_after.items()):
        if "_" in name:
            idx = name.index("_")
            name = name[:idx]
        message += "第" + str(rank+1) + "位: " + name + "さん  "
        message += str(member_info["init"]["val"]) + " → " + str(
            member_info["last"]["val"]) + " (進捗数: " + str(member_info["diff"]) + ")"
        if member_info["init"]["val"] < 21 and 21 <= member_info["last"]["val"]:
            finished_member_progate[name] = member_info
        elif member_info["last"]["val"] == 327:
            finished_member_udemy[name] = member_info
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

    message += "\n"
    message += "皆さま、すごいです！\nこの調子でどんどん頑張りましょう!!"
    message += "\n\n--------------------------------------------------------------------------\n"

    print(message)

    # 上記メッセージ出力
    await channel.send(message)


##
# @func progress_warning
# @brief 1週間進捗報告が無い人達に対して警告処理を行う
# @param guild Discord上のWorkReadyについての情報
# @param member_info_dict 進捗報告(日報)チャンネルにおける、過去のメッセージ情報(1週間)
# @param member_info_dict_through_week_ago 進捗報告(日報)チャンネルにおける、過去のメッセージ情報(2週間)
# @details member_info_dict(辞書型)には1週間以内のメッセージ情報が、
# @details member_info_dict_through_week_ago(辞書型)には2週間以内のメッセージ情報がそれぞれ含まれる。
# @details 具体的には、過去メッセージを発信した(進捗報告を行った)人のキーには「message」が追加される。
# @details この「message」キーが存在するか否かで判定し、無いitemを結果格納用辞書変数(target_member)に追加する。
# @details 前提として、(1週間進捗報告が無い人の数)>(2週間進捗報告が無い人の数)である。
# @details そのため、2週間進捗報告が無い人だけをひとまずリスト化し、
# @details その後上記リストにない人で、かつ1週間進捗報告が無い人を警告処理対象者とする。
# @details 警告処理対象さhに対して下記処理を行う。
# @details ・ban対象者用メッセージを所定チャンネルに表示する
# @note member_info_dict, member_info_dict_through_week_ago出力元の関数は
# @note 上記「get_messages_info」だが、この時afterは8/16にすること
##
async def progress_warning(guild, member_info_dict, member_info_dict_through_week_ago):

    # 警告対象者処理開始メッセージ(プロンプト上に出力)
    print("progress_warning process start...")

    # 結果出力用チャンネル指定
    channel = discord.utils.get(
        guild.channels, name="進捗報告（日報）")  # できればnameではなくidで指定したい
    # channel = discord.utils.get(guild.channels, name="bot_train")  # できればnameではなくidで指定したい

    # まずban対象者のみ抽出する。
    target_member_through_week_ago = {}

    # 警告対象者選別基準日付(8/16)
    exec_threshould_date = datetime.datetime(2023, 8, 16, 0, 0, 0)

    for id, member in member_info_dict_through_week_ago.items():
        if not (member["is_bot"] or member["is_moderator"] or member["is_admin"] or member["is_portofolio"]):
            if not "message" in member.keys():
                # target_member_through_week_ago[id] = member
                # Disocrod参画時の日付が上記「警告対象者選別基準日付」以降のみ
                if member["joined_at"] > exec_threshould_date:
                    target_member_through_week_ago[id] = member

    # その後警告対象者の一覧から、ban対象者に該当しない人を抽出する
    target_member = {}

    for id, member in member_info_dict.items():
        if not (member["is_bot"] or member["is_moderator"] or member["is_admin"] or member["is_portofolio"]):
            if (not "message" in member.keys()) and (not id in target_member_through_week_ago.keys()):
                # target_member[member["name"]] = id
                # Disocrod参画時の日付が上記「警告対象者選別基準日付」以降のみ
                if member["joined_at"] > exec_threshould_date:
                    target_member[member["name"]] = id

    # 警告対象者が存在する場合警告対象者へメッセージ送信処理を行う。
    if len(target_member) > 0:
        warninig_message = "## 【進捗報告が確認できない方へ】\n"
        for member_name, id in target_member.items():
            warninig_message += "<@" + str(id) + ">さん\n"
            # warninig_message += member_name + "さん\n"

        warninig_message += "\n"
        warninig_message += "ここ1週間の進捗が確認できません。\n" +\
            "2週間の間進捗が確認できない場合\n" +\
            "契約に基づき当コミュニティより除名させていただくとともに\n" +\
            "受講料132,000円(税込)をご請求させていただきます。\n\n" +\
            "不明点により進捗が進まない場合は、相談チャンネルや週次で実施しております相談会をご利用ください。\n" +\
            "また、やむを得ない事情により進捗を勧められない場合は運営スタッフまでご連絡ください。\n\n" +\
            "以上、よろしくお願いいたします。"
        warninig_message += "\n\n--------------------------------------------------------------------------\n"

        print(warninig_message)
        await channel.send(warninig_message)
    else:
        print("進捗報告に関する、警告対象者は存在しませんでした。")


##
# @func progress_ban
# @brief 2週間進捗報告が無い人達に対してban処理を行う
# @param guild Discord上のWorkReadyについての情報
# @param member_info_dict_through_week_ago 進捗報告(日報)チャンネルにおける、過去のメッセージ情報(2週間)
# @details member_info_dict_through_week_ago(辞書型)には2週間以内のメッセージ情報が含まれる。
# @details 具体的には、過去メッセージを発信した(進捗報告を行った)人のキーには「message」が追加される。
# @details この「message」キーが存在するか否かで判定し、無いitemを結果格納用辞書変数(target_member)に追加する。
# @details その後、検知した生徒に対して下記処理を行う。
# @details ・ban対象者用メッセージを所定チャンネルに表示する
# @details ・banする
# @details ・ban対象者のユーザIDをnotionのDBから検索して、対象のメールアドレスに受講料請求メールを送信する
# @note member_info_dict出力元の関数は上記「get_messages_info」だが、この時afterは8/16にすること
##
async def progress_ban(guild, member_info_dict_through_week_ago):

    # ban対象者処理開始メッセージ(プロンプト上に出力)
    print("progress_ban process start...")

    # ban対象者出力対象チャンネルを指定する
    channel = discord.utils.get(
        guild.channels, name="進捗報告（日報）")  # できればnameではなくidで指定したい
    # channel = discord.utils.get(guild.channels, name="bot_train")  # できればnameではなくidで指定したい  # Debug用

    # ban対象者(2週間以内に進捗報告が確認できなかった生徒)の情報を抽出
    target_member = {}

    # ban対象者選別基準日付(8/16)
    exec_threshould_date = datetime.datetime(2023, 8, 16, 0, 0, 0)

    # sterterコースの生徒のみバン処理対象
    starter_flg = True

    # 過去のメッセージ情報確認し、2週間の間進捗報告が無い人を抽出
    for id, member in member_info_dict_through_week_ago.items():
        if not (member["is_standard"] or member["is_premium"]):
            if not (member["is_bot"] or member["is_moderator"] or member["is_admin"] or member["is_portofolio"]):
                if not "message" in member.keys():
                    # target_member[member["name"]] = id
                    # Disocrod参画時の日付が上記「警告対象者選別基準日付」以降のみ
                    if member["joined_at"] > exec_threshould_date:
                        target_member[member["name"]] = id

                        # ban対象者が一人でもいたら
                        if len(target_member) > 0:

                            # 出力用メッセージ生成
                            # (下記ループ文で対象者をメンションで指定する)
                            ban_message = "## 【進捗報告が確認できない方へ】\n"

                            for member_name, id in target_member.items():
                                ban_message += "<@" + str(id) + ">さん\n"
                                # ban_message += member_name + "さん\n"

                            ban_message += "\n"
                            ban_message += "ここ2週間の進捗が確認できません。\n" +\
                                "事前にお伝えしておりました通り、\n" +\
                                "当コミュニティより除名させていただくとともに\n" +\
                                "受講料132,000円(税込)ご請求させていただきます。\n\n" +\
                                "詳細につきまして、ご入会の際にご提示いただきましたメールアドレス宛に\n" +\
                                "届いておりますメールをご確認ください。\n\n" +\
                                "以上、よろしくお願いいたします。"

                            print(ban_message)

                            # チャンネルにメッセージを出力
                            await channel.send(ban_message)

                            # ban対象者に受講料請求メール送信
                            # send_mail(target_member)

                            # ban処理  # TODO notionDBに対してbanフラグがあればONにする処理必要？
                            for id in target_member.values():
                                member = guild.get_member(id)
                                await member.ban(reason="1週間の進捗報告が確認できなかったため")

                            # バン機能お試し
                            # member = guild.get_member(1141974279886475275)
                            # await member.ban(reason="バンお試し(テストアカウント)")
                        else:
                            print("進捗報告における、ban対象者は存在しませんでした。")

                    ##
                    # @fnuc send_mail
                    # @brief メール送信用関数
                    # @param target_member {(ユーザID): (ニックネーム)}の集合体
                    ##

                    def send_mail(target_member):
                        import smtplib  # SMTPライブラリ
                        from email.mime.text import MIMEText  # メール送信用モジュール
                        from notion_client import Client  # notionAPI

                        # notionオブジェクト生成
                        notion = Client(auth=guild_id_dict["NOTION_TOKEN"])

                        # SMTPオブジェクト生成
                        smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
                        smtpobj.starttls()
                        smtpobj.login('ra0039ip@gmail.com',
                                      'repuxcyfahmxqrea')  # SMTP使用処理

                        # メッセージ設定
                        message = MIMEText('Test Mail From Python.')  # 文面
                        message['Subject'] = 'Test Title'  # メール文面
                        # WorkReady運営用メールアドレス？
                        message['From'] = 'ra0039ip@gmail.com'

                        # メール送信処理
                        for member_name, id in target_member.items():

                            idx = member_name.index("_")  # 「_」の番地取得
                            # databaseid取得
                            database_id = database_id_list[member_name[:(
                                idx+1)]]

                            # notionDBから上記情報に紐づくカラムを取得
                            result = notion.databases.query(
                                **{
                                    "database_id": database_id,
                                    "filter": {
                                        "property": "id",
                                        "title": {
                                            "contains": id,
                                        }
                                    },
                                }).get("results")

                            # メールアドレス取得
                            # TODO notionで新規DBの結果を取得で来てから
                            mail = result[0]['property']
                            message['To'] = mail

                            # メール送信
                            smtpobj.send_message(message)

                        # SMTPオブジェクト破棄
                        smtpobj.close()

##
# @func list_vanity_student
# @brief 過去一度も進捗報告を実施したことがない人たちを列挙
# @param guild Discord上のWorkReadyについての情報
# @param member_info_dict 進捗報告(日報)における、過去のメッセージ情報
# @details member_info_dict(辞書型)には過去全期間のメッセージ情報が含まれる。
# @details 具体的には、過去メッセージを発信した(進捗報告を行った)人のキーには「message」が追加される。
# @details この「message」キーが存在するか否かで判定し、無いitemを結果格納用辞書変数(target_member)に追加する。
# @note member_info_dict出力元の関数は上記「get_messages_info」だが、この時afterはNoneにすること
##
# async def list_vanity_student(guild, member_info_dict, member_info_dict_through_week_ago):


async def list_vanity_student(guild, member_info_dict):

    # 結果出力チャネル指定
    # channel = discord.utils.get(guild.channels, name="進捗報告（日報）")  # できればnameではなくidで指定したい
    channel = discord.utils.get(
        guild.channels, name="bot_train")  # できればnameではなくidで指定したい

    # 進捗報告が一度もない生徒の情報を抽出
    target_member = {}

    # 過去のメッセージ情報確認し、一度も無い人を抽出
    for id, member in member_info_dict.items():
        if not (member["is_bot"] or member["is_moderator"] or member["is_admin"] or member["is_portofolio"]):
            if not "message" in member.keys():
                # if not id in member_info_dict_through_week_ago.keys():
                #     target_member[member["name"]] = id
                target_member[member["name"]] = id

    # 結果メッセージ生成
    vanity_student_list = ""
    for member_name, id in target_member.items():
        # vanity_student_list += "<@" + str(id) + ">さん\n"
        vanity_student_list += member_name + "さん\n"

    vanity_student_list += "\n"
    vanity_student_list += "入会後一度も進捗報告が無い人"

    # 結果メッセージをチャット上に出力
    await channel.send(vanity_student_list)


def main():
    print("test")


if __name__ == "__main__":
    main()
