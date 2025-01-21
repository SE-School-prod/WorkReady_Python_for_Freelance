"""
@file assign_instructor_roll.py
@date 2024/04/13(木)
@author 藤原光基
@brief 新規ユーザ確認bot
@brief Discordへの受講生参加時、講師用ロールを割り振る。
@bar 編集日時 編集者 編集内容
@bar 2023/10/23(月) 藤原光基 新規作成
"""

import discord

from .notion import Notion
from settings.database_id_list import instructor_id_list


async def assign_instructor_roll(member):

    notion = Notion()

    min_student_num = 100000

    for key, val in instructor_id_list.items():
        print(key, val)
        if key != "講師DB":
            results = notion.select(
                database_id=val["id"], filter_dict={'在籍状況': '受講中'})
            print("results length({}): {}".format(val, len(results)))
            if len(results) <= min_student_num:
                min_student_num = len(results)
                instructor_id_key = key

    print(f"instructor id: {instructor_id_key}")

    role_name_instructor = "講師" + instructor_id_key + \
        "_" + instructor_id_list[instructor_id_key]["name"]
    print("role_name_instructor: ", role_name_instructor)

    role_instructor = discord.utils.get(member.guild.roles, name=role_name_instructor)
    # role_instructor = discord.utils.get(member.guild.roles, name='test')
    print("role(test) add.")
    await member.add_roles(role_instructor)

    role_begginer = discord.utils.get(member.guild.roles, name='Beginner')
    await member.add_roles(role_begginer)
    print("role(begginer) add.")
