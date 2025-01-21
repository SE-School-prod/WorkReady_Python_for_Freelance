"""
@file guild_id_dict.py
@date 2023/07/31(月)
@author 藤原光基
@brief DiscordのID関連
@details 処理に必要な各種ID,トークン情報をまとめた辞書型変数。
@note 「NOTION_TOKEN」、「DISCORD_TOKEN」について、変更時は逐次用変更。
@bar 編集日時 編集者 編集内容
@bar 2023/07/31(月) 藤原光基 新規作成
"""

guild_id_dict = {
    "GUILD_ID": 1093886520324259920,  # DiscordのWorkReadyチャットグループID
    "BOT_ID": 1098104259926573076,  # 「Discortion」BOTのメッセージID
    "NOTION_TOKEN": 'secret_013tQKTmEmdOOWcBgcPBTKNN3wAOzgQhTSkN2t63M2U',  # Notionのトークン
    "DISCORD_TOKEN": 'MTA5ODEwNDI1OTkyNjU3MzA3Ng.GPjc_Y.AHckYHMDZgzubR-Z7Pt--quU3Y_LxjFqoBfV4g',  # Discordのトークン
    "CHANNEL_ID_DAILY_REPORT": "1098841750077968435",  # daily report
    "CHANNEL_ID_BOT_BOT": "1119239857751986227",  # bot_bot
    "CHANNEL_ID_BOT_TRAIN": "1098157558885273621",  # bot_train
    "LOG_SAVE_DIR": "notion_api_logs"  # ログ保存先
}