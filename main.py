##
# @file main.py
# @date 2023/07/31(月)
# @author 藤原光基
# @brief 各bot実行用bot
# @details 以下の機能をまとめて実行する。
# @details ・進捗登録用bot(collect_progress)
# @details ・進捗に応じたロール変更用bot(change_roll)
# @details ・ロール自動変更bot(change_standard)
# @details
# @note 本プロジェクトのフォルダ構成は下記の通り
# @note
# @note Project (root)
# @note ┣ err_handling (エラー関連機能保存フォルダ)
# @note ┃ ┣ error_dict.py (エラー種別ごとの文面)
# @note ┃ ┗ error_message.py (エラー出力処理)
# @note ┃
# @note ┣ notion_api_logs (ログ保存フォルダ)
# @note ┃
# @note ┣ settings (ID,設定値関連保存フォルダ)
# @note ┃ ┣ database_id_list.py (進捗登録先ID集)
# @note ┃ ┣ guild_id_dict.py (WorkReady提携先エージェント様DBテーブルID)
# @note ┃ ┣ reservation_cycle.txt (アイテマスurl送付先アドレス参照用インデックス)
# @note ┃ ┗ settings_dict.py (Discord設定関連)
# @note ┃
# @note ┣ src (各機能bot保存フォルダ)
# @note ┃ ┣ change_roll.py (進捗に応じたロール変更bot)
# @note ┃ ┣ change_standard.py (ロール自動変更bot)
# @note ┃ ┣ collect_progress.py (進捗登録bot)
# @note ┃ ┣ delete_logs.py (ログ自動削除bot)
# @note ┃ ┣ get_aitemasu_url.py (相談会予約受付bot)
# @note ┃ ┣ get_progress_announce.py (進捗ランキング、DM送信bot)
# @note ┃ ┣ logger.py (ロガーモジュール)
# @note ┃ ┣ mail.py (メール送信モジュール)
# @note ┃ ┗ notion.py (Notionモジュール)
# @note ┃
# @note ┣ main.py (全処理実行用bot)
# @note ┗ keep_alive.py (bot定期実行)
# @note
# @note Debugの際は下記を変更してください。
# @note ・main.py(124行目~125行目)[変動有]
# @note  @tasks.loop(seconds=10)
# @note ↔@tasks.loop(hours=24)
# @note
# @note ・change_standard.py(23行目~38行目)[変動有]
# @note  if (datetime.now(timezone.utc) - member.joined_at) > timedelta(minutes=10):
# @note      for had_role in member.roles:
# @note          print("role: ", had_role)
# @note  ↔ if (datetime.now(timezone.utc) - member.joined_at) > timedelta(days=124):  # 4 months
# @note    ...
# @note        await member.remove_roles(remove_role)
# @warning 本処理をクラスにすべきか要検討
# @bar 編集日時 編集者 編集内容
# @bar 2023/07/31(月) 藤原光基 新規作成
# @bar 2023/08/20(日) 藤原光基 Replitへデプロイ
# @bar 2023/10/02(月) 藤原光基 logger.py, mail.py, notion.py, get_aitemasu_url.py追加
# @bar 2024/04/16(月) 藤原光基 on_member_join追加
##

import os
import datetime
import platform
# from pytz import timezone
import pytz

import discord
from discord.ext import tasks, commands

import keep_alive

from src.assign_instructor_roll import assign_instructor_roll
from src.collect_progress import collect_progress
from src.change_roll import change_roll
from src.change_standard import change_standard
from src.delete_logs import delete_logs
from src.get_progress_announce import get_messages_info, progress_ranking, progress
from src.get_aitemasu_url import get_aitemasu_url
from src.check_beginner import check_beginner
from src.change_enrollment_status import change_enrollment_status
from src.logger import Logger
from settings.settings_dict import settings_dict
from src.manage_ticket import accept_consultation_services, confirm_ticket, recieve_consultation_report
from settings.role_id_dict import role_id_dict

# logger = logging.getLogger()

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
client = discord.Client(intents=discord.Intents.all())


def main():
    logger_ = Logger()
    logger = logger_.get()

    if settings_dict["DEBUG_FLG"]:
        channel_id_daily_report = settings_dict["GUILD_ID"]["CHANNEL_ID_BOT_TRAIN"]
        channel_id_reserve = settings_dict["GUILD_ID"]["CHANNEL_ID_BOT_TRAIN"]
        logger.info('チャンネル: bot_train')
    else:
        channel_id_daily_report = settings_dict["GUILD_ID"][
            "CHANNEL_ID_DAILY_REPORT"]
        channel_id_reserve = settings_dict["GUILD_ID"]["CHANNEL_ID_BOT_RESERVE"]
        logger.info('チャンネル: 進捗報告(日報)')

    # 本bot起動時発射用bot
    # 下記2種類の処理を実行する
    # ・botが正常に起動した旨のメッセージをコンソール上に表示する
    # ・エラーハンドラを初期化する
    @bot.event
    async def on_ready():
        logger.info('logined')
        role_update.start()
        monthly_task.start()
        progress_check.start()

    @bot.event
    async def on_member_join(member):
        await assign_instructor_roll(member)

    # メッセージ変更時発射bot
    # メッセージ編集時でも進捗を登録するようにする
    # ただし編集メッセージも誤っていた場合、その内容をチャット上に出力する
    @bot.event
    async def on_message_edit(before, after):
        logger.info('START メッセージ編集: {}'.format(after))
        logger.info('編集前: {}'.format(before))
        logger.info('編集後: {}'.format(after))

        # if before.channel.id == channel_id_daily_report:
        if ((after.author.display_name[-3:] != "@運営")
                and (after.author.id != settings_dict["GUILD_ID"]["BOT"])):
            if (after.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_BOT_TRAIN"]) or\
                    after.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_DAILY_REPORT"]:

                if before.content != after.content:
                    logger.info('START コマンド変更: {}'.format(after))
                    guild = discord.utils.get(bot.guilds,
                                              id=settings_dict["GUILD_ID"]["GUILD"])
                    await collect_progress(after, logger, guild)
                    await change_roll(after, logger)
                    # await collect_progress(after, guild)
                    # await change_roll(after)
                    logger.info('END コマンド変更: {}'.format(after))

            elif before.channel.id == channel_id_reserve:

                if before.content != after.content:

                    await get_aitemasu_url(after, guild)
                # await get_aitemasu_url(after)

            # チケットの枚数確認チャンネル
            elif before.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_CONFIRM_TICKET_NUM"]:
                guild = discord.utils.get(
                    bot.guilds, id=settings_dict["GUILD_ID"]["GUILD"])
                logger.info('START コマンド入力: {}'.format(after))
                await confirm_ticket(after, logger, guild)
                logger.info('END コマンド入力: {}'.format(after))

        elif (after.author.display_name[-3:] == "@運営") or (after.author.id == settings_dict["GUILD_ID"]["BOT"]):
            if (before.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_BOT_TRAIN"]) or (before.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_ENOROLLMENT_STATUS"]):
                guild = discord.utils.get(
                    bot.guilds, id=settings_dict["GUILD_ID"]["GUILD"])
                logger.info('START コマンド入力: {}'.format(after))
                await change_enrollment_status(after, logger, guild)
                logger.info('END コマンド入力: {}'.format(after))
        
        # ロールが講師の場合
        if after.author.get_role(role_id_dict["講師"]) != None:
            if (after.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_BOT_TRAIN"]) or (after.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_CONSULTATION_REPORT"]):
                guild = discord.utils.get(
                    bot.guilds, id=settings_dict["GUILD_ID"]["GUILD"])
                logger.info('START コマンド入力: {}'.format(after))
                await recieve_consultation_report(after, logger, guild)
                logger.info('END コマンド入力: {}'.format(after))

        logger.info('END メッセージ編集: {}'.format(after))

    # メッセージ受信時発射bot
    # ・進捗登録処理
    # 　専用コマンドフォーマット(/curr ~~~)に応じてnotionに進捗を登録する
    # ・ロール変更処理
    #   専用コマンドフォーマットの数字に応じて「udemy」、「ポートフォリオ」のいずれかを付与する
    # 上記処理には既定の名前、およびコマンドフォーマット以外は対応するエラー内容を表示するようにする
    @bot.event
    async def on_message(message):
        logger.info('START メッセージ入力: {}'.format(message))
        logger.info('メッセージ中身: {}'.format(message.content))

        # if False:  # Debug用
        # if message.channel.id == channel_id_daily_report:
        # if message.channel.id == channel_id_daily_report:
        if ((message.author.display_name[-3:] != "@運営")
                and (message.author.id != settings_dict["GUILD_ID"]["BOT"])):

            if ((message.channel.id
                 == settings_dict["GUILD_ID"]["CHANNEL_ID_BOT_TRAIN"])
                or (message.channel.id
                    == settings_dict["GUILD_ID"]["CHANNEL_ID_DAILY_REPORT"])
                or (message.channel.id
                    == settings_dict["GUILD_ID"]["CHANNEL_ID_DOC_COMPLETE"])):

                guild = discord.utils.get(bot.guilds,
                                          id=settings_dict["GUILD_ID"]["GUILD"])
                logger.info('START コマンド入力: {}'.format(message))
                await collect_progress(message, logger, guild)
                await change_roll(message, logger)
                logger.info('END コマンド入力: {}'.format(message))

            elif message.channel.id == channel_id_reserve:
                await get_aitemasu_url(message, logger)

            elif message.channel.id == settings_dict["GUILD_ID"][
                    "CHANNEL_ID_INIT_SETTING"]:
                guild = discord.utils.get(bot.guilds, id=settings_dict["GUILD_ID"]["GUILD"])
                await check_beginner(message, logger, guild)

            #チケット制相談会の予約
            elif message.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_CONSULTATION_SERVICE"]:
                guild = discord.utils.get(
                    bot.guilds, id=settings_dict["GUILD_ID"]["GUILD"])
                logger.info('START コマンド入力: {}'.format(message))
                await accept_consultation_services(message, logger, guild)
                logger.info('END コマンド入力: {}'.format(message))

            # チケットの枚数確認チャンネル
            elif message.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_CONFIRM_TICKET_NUM"]:
                guild = discord.utils.get(
                    bot.guilds, id=settings_dict["GUILD_ID"]["GUILD"])
                logger.info('START コマンド入力: {}'.format(message))
                await confirm_ticket(message, logger, guild)
                logger.info('END コマンド入力: {}'.format(message))

        # 運営の場合かボットの場合
        elif (message.author.display_name[-3:] == "@運営") or (message.author.id == settings_dict["GUILD_ID"]["BOT"]):
            if (message.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_BOT_TRAIN"]) or (message.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_ENOROLLMENT_STATUS"]):
                guild = discord.utils.get(
                    bot.guilds, id=settings_dict["GUILD_ID"]["GUILD"])
                logger.info('START コマンド入力: {}'.format(message))
                await change_enrollment_status(message, logger, guild)
                logger.info('END コマンド入力: {}'.format(message))
        
        # ロールが講師の場合
        if message.author.get_role(role_id_dict["講師"]) != None:
            if (message.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_BOT_TRAIN"]) or (message.channel.id == settings_dict["GUILD_ID"]["CHANNEL_ID_CONSULTATION_REPORT"]):
                guild = discord.utils.get(
                    bot.guilds, id=settings_dict["GUILD_ID"]["GUILD"])
                logger.info('START コマンド入力: {}'.format(message))
                await recieve_consultation_report(message, logger, guild)
                logger.info('END コマンド入力: {}'.format(message))
            

        logger.info('END メッセージ入力: {}'.format(message))

    # 自動ロール移行bot
    # 1日置きに、4カ月以上在籍している生徒のロールを「Starter」→「Standard」に変更する
    # なお、「卒業生」ロールが付与されている生徒は除外する
    # @tasks.loop(seconds=10)  # Debug用
    @tasks.loop(hours=1)
    async def role_update():
        guild = bot.get_guild(settings_dict["GUILD_ID"]["GUILD"])
        await change_standard(guild, logger)
        # await change_standard(guild)

    # @tasks.loop(minutes=5)  # Debug用
    @tasks.loop(hours=24)
    async def monthly_task():
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

        if now.day == 1:
            await delete_logs(logger)
            # await delete_logs()

    @tasks.loop(minutes=10)
    async def progress_check():
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        # if True:
        if (now.hour == 0) and (0 <= now.minute < 10):
            logger.info("START 全体進捗取得")
            guild = bot.get_guild(settings_dict["GUILD_ID"]["GUILD"])
            now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

            today_init_time = datetime.datetime(now.year, now.month, now.day, 0,
                                                0, 0)
            today_last_time = datetime.datetime(now.year, now.month, now.day, 23,
                                                59, 59)

            week_day = now.weekday()  # 今週の日付(月曜日: 0 ~ 日曜日: 6)

            two_week_ago_init = today_init_time - datetime.timedelta(
                days=14)  # 1週間前の日曜日の日付
            one_week_ago_last = today_last_time - datetime.timedelta(
                days=1)  # 1週間前の月曜日の日付

            member_info_through_week_ago = await get_messages_info(
                guild, logger, after=two_week_ago_init,
                before=one_week_ago_last)  # 2週間前の月曜日～日曜日のメッセージ情報

            await progress(bot, member_info_through_week_ago, logger)
            # await progress(bot, member_info_through_week_ago)

            if week_day == 0:
                two_week_ago_last = today_last_time - datetime.timedelta(
                    days=8)  # 2週間前の月曜日の日付
                one_week_ago_init = today_init_time - datetime.timedelta(
                    days=7)  # 前日(日曜日)の日付

                member_info_last_week = await get_messages_info(guild,
                                                                logger,
                                                                after=one_week_ago_init,
                                                                before=one_week_ago_last
                                                                )  # 先週月曜日～日曜日のメッセージ情報
                member_info_two_week_ago = await get_messages_info(
                    guild, logger, after=two_week_ago_init,
                    before=two_week_ago_last)  # 2週間前の月曜日～日曜日のメッセージ情報
                await progress_ranking(guild, logger, member_info_last_week,
                                       member_info_two_week_ago)  # 先週→今週にかけての進捗率を出力

    logger.info("END 全体進捗取得")

    @role_update.before_loop
    async def before():
        await bot.wait_until_ready()

    @monthly_task.before_loop
    async def monthly_task_init():
        await delete_logs(logger)

    @progress_check.before_loop
    async def progress_check_init():
        await bot.wait_until_ready()


def tes_mail():
    from src import mail
    mail.main()


def test_id():
    import discord
    id = 991088543680057394

    # print(settings_dict["GUILD_ID"]["GUILD"])
    guild = bot.get_guild(settings_dict["GUILD_ID"]["GUILD"])
    # print(guild)
    channel = discord.utils.get(guild.channels, name="進捗報告（日報）")

    for member in channel.members:
        if member.id == id:
            print(member)


if __name__ == "__main__":
    main()
    # keep_alive.keep_alive()  # server
    # bot.run(settings_dict["TOKEN"]["DISCORD"])  # debug
    bot.run(os.environ["DISCORD_TOKEN"])  # server
