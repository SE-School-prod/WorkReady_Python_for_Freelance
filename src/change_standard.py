"""
@file change_standard.py
@date 2023/07/31(月)
@author 藤原光基
@brief ロール自動変更bot
@details 1日に1回生徒の習熟期間を検知し、
@details 4ヵ月経過した生徒のロールを「Starter(無料)」→「Standard(有料)」に自動変更する。
@note TODO 退会→再入会した際の対策
@bar 編集日時 編集者 編集内容
@bar 2023/07/31(月) 藤原光基 新規作成
"""
import discord
# from datetime import datetime, timedelta, timezone
import datetime
import platform
import pytz

# from .logger import Logger


async def change_standard(guild, logger):
    # async def change_standard(guild):
    role_update_flag = False
    """
    logger_ = Logger()
    logger = logger_.get()
    """

    logger.info("START change_standard")
    print(guild.members)
    for member in guild.members:
        role_update_flag = False
        try:
            for had_role in member.roles:
                if had_role.name == '卒業生':
                    role_update_flag = True

            if not role_update_flag:

                now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))

                if (now - member.joined_at) > datetime.timedelta(days=124):  # 4 months
                    for had_role in member.roles:
                        if 'Starter' == had_role.name:
                            add_role = discord.utils.get(
                                guild.roles, name="Standard")
                            remove_role = discord.utils.get(
                                guild.roles, name="Starter")
                            # add the role
                            await member.add_roles(add_role)

                            # remove the role
                            await member.remove_roles(remove_role)

                            logger.info("{}'s roll changed from {} to {}.[past_time(now - member.joined_at): {}]".format(
                                member.name, 'Starter', 'Standard', now - member.joined_at))

        except Exception as e:
            logger.error(e)

    logger.info("END change_standard")
