"""
@file change_roll.py
@date 2023/07/31(月)
@author 藤原光基
@brief ロール自動変更bot
@details 進捗コマンドに応じて、ロールを「Udemy」、「ポートフォリオ」のいずれかに自動で更新する
@note 「Udemy」ロール、「ポートフォリオ」ロールが付与されていない状態で
@note カリキュラムNo最大値の進捗コマンドが入力された場合は
@note 「ポートフォリオ」ロールは付与されないため注意すること。
@note TODO コマンド修正時、ロール下げる機能追加
@bar 編集日時 編集者 編集内容
@bar 2023/07/31(月) 藤原光基 新規作成
"""
import discord

from settings.settings_dict import settings_dict
from src import common
# from .logger import Logger


# 進捗コマンドに応じたロール名取得
def check_cariculam(cariculam_number):

    # 「/curr 001 ~ 020」→　ロール名:「Progate」
    # (現状存在しないが、便宜上分岐パターンとして付与)
    if settings_dict["CURRICULUM_NUMBER_RANGE"]["PROGATE"]["MIN"] <= cariculam_number <= settings_dict["CURRICULUM_NUMBER_RANGE"]["PROGATE"]["MAX"]:
        res = 'Progate'

    # 「/curr 021 ~ 326」→ ロール名:「Udemy」
    elif settings_dict["CURRICULUM_NUMBER_RANGE"]["UDEMY"]["MIN"] <= cariculam_number <= settings_dict["CURRICULUM_NUMBER_RANGE"]["UDEMY"]["MAX"]:
        res = 'Udemy'

    # 「/curr 327」→ ロール名:「ポートフォリオ」
    elif settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MIN"] <= cariculam_number <= settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MAX"]:
        res = 'Portofolio'

    # 上記以外は「Unknown」を返す
    # (基本ここに該当するコマンドは既にエラーとなっているため、ここまで来ないはず)
    else:
        res = 'Unknown'

    return res


# 本botメイン処理
async def change_roll(message, logger):
    # async def change_roll(message):

    """
    logger_ = Logger()
    logger = logger_.get()
    """

    logger.info("START change_roll")
    logger.info("message: {}".format(message))

    try:
        # ロールオブジェクト初期化
        role_progate = discord.utils.get(message.guild.roles, name="Progate")
        role_udemy = discord.utils.get(message.guild.roles, name="Udemy")
        role_portofolio = discord.utils.get(
            message.guild.roles, name="ポートフォリオ")

        # 進捗コマンドから進捗抽出
        if "\n" in message.content:
            content = message.content.split('\n')[-1]
        else:
            content = message.content

        # 進捗コマンドから進捗抽出
        # cariculam_number = int(message.content.split(" ")[1])
        cariculam_number = int(content.split(" ")[1])

        role_via_number = check_cariculam(cariculam_number)
        member = message.author

        # ロール削除
        for had_role in member.roles:
            if had_role.name == "Progate":
                await member.remove_roles(role_progate)
                logger.info("role {} has removed.".format("Progate"))
                break
            elif had_role.name == "Udemy":
                await member.remove_roles(role_udemy)
                logger.info("role {} has removed.".format("Udemy"))
                break
            elif had_role.name == "ポートフォリオ":
                await member.remove_roles(role_portofolio)
                logger.info("role {} has removed.".format("Portofolio"))
                break

        # ロール付与
        if role_via_number == "Progate":
            await member.add_roles(role_progate)
            logger.info("role {} has add.".format("Progate"))
        elif role_via_number == "Udemy":
            await member.add_roles(role_udemy)
            logger.info("role {} has add.".format("Udemy"))
        elif role_via_number == "Portofolio":
            await member.add_roles(role_portofolio)
            logger.info("role {} has add.".format("Portofolio"))

    # エラー検知処理
    except Exception as e:
        logger.error(e)

    logger.info("END change_roll")
