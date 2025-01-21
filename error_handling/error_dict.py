"""
@file error_dict.py
@date 2023/07/31(月)
@author 藤原光基
@brief エラー種別ごとの文面
@details 進捗登録用コマンド、もしくは生徒の名前にエラーが検知された場合の文面についてまとめた辞書型変数
@note 本辞書型変数の見方は下記の通り。
@note 【大分類】
@note ・"annaounce": エラー発生時、Discordのチャット上に表示させる文面
@note ・"message": エラー発生時、ログに記載する内容
@note 
@note 【中分類】
@note ・"command": コマンド自体にエラーを検知した場合の文面
@note ・"user": コマンドを送信した生徒の名前にエラーを検知した場合の文面
@note 
@note 【小分類】
@note ・"command"-"/curr": コマンドの前半が「/curr 」でない場合の文面
@note ・"command"-"digit": コマンドの後半が数字でない場合の文面
@note ・"command"-"excess": コマンドの後半の数字が最大値(327)を超過した場合の文面
@note ・"user"-"digit": 生徒の名前の後にnotion登録用DBのIDが記載されていない場合の文面
@note ・"user"-"_":生徒名に「_」が付与されていない場合の文面
@note ・"user"-"nodigit":生徒名に「_」+「(DB登録用ID)」が付与されていない場合の文面
@note ・"user"-"dbidkey":生徒名にDBに登録されないIDが付与されている場合の文面
@note ・"user"-"userprofile": 生徒の名前が「サーバープロフィール」ではなく「ユーザープロフィール」に設定されている場合の文面
@note ・"both": 生徒名、コマンド名双方にエラーが検知された場合の文面
@note ・"Unknown": 上記すべてのエラーに該当しない場合の文面
@bar 編集日時 編集者 編集内容
@bar 2023/07/31(月) 藤原光基 新規作成
@bar 2023/09/19(火) 藤原光基 「相談会予約」用エラーメッセージ追加
"""

error_dict = {
    "annaounce": {
        "command": {
            "/curr": "想定されていないフォーマットのコマンドを検知しました。\n"\
                     "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                     "・コマンドの最初は「/curr」で始めてください。\n"\
                     "・「/curr」と数字の間にスペースを入れてください。\n\n"\
                     "(例) /curr 001",

            "digit": "想定されていないフォーマットのコマンドを検知しました。\n"\
                     "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                     "・3桁0埋めの数字で入力してください。\n\n"\
                     "(例) /curr 001",

            "excess": "想定されていないフォーマットのコマンドを検知しました。\n"\
                      "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                      "・コマンドに設定する数字は「335」以下にしてください。\n\n"\
                      "・カリキュラム番号がわからない場合、Wikiの「カリキュラム対応表」をご確認ください。\n\n"\
                      "(例) /curr 335",

        },
        "user": {
            "digit": "想定されていないフォーマットの名前を検知しました。\n"\
                     "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                     "・5桁0埋めの数字で設定してください。\n\n"\
                     "(例) テスト太郎_00001\n\n"\
                     "下記リンクを参考に「サーバープロフィール」タブからサーバーニックネームを変更してください。\n"\
                     "https://setup-lab.net/discord-nickname-change/",

            "_": "想定されていないフォーマットの名前を検知しました。\n"\
                 "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                 "・氏名と数字の間は「_(半角アンダースコア)」で設定してください。\n\n"\
                 "(例) テスト太郎_00001\n\n"\
                 "下記リンクを参考に「サーバープロフィール」タブからサーバーニックネームを変更してください。\n"\
                 "https://setup-lab.net/discord-nickname-change/",

            "nodigit": "想定されていないフォーマットの名前を検知しました。\n"\
                       "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                       "・氏名の後にご自身のDBに対応する5桁0埋めの数値を設定してください。\n\n"\
                       "(例) テスト太郎_00001\n\n"\
                       "下記リンクを参考に「サーバープロフィール」タブからサーバーニックネームを変更してください。\n"\
                       "https://setup-lab.net/discord-nickname-change/",

            "dbidkey": "想定されていないフォーマットの名前を検知しました。\n"\
                       "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                       "・氏名の後にご自身のDBに対応する5桁0埋めの数値を設定してください。\n\n"\
                       "(例) テスト太郎_00001\n\n"\
                       "番号がご不明の番号の場合、担当のエージェントにご確認ください。",

            "userprofile": "discord上に表示させる名前が「ユーザープロフィール」に設定されています。\n"\
                           "「サーバープロフィール」に設定を変更してください。\n"\
                           "なお、「ユーザーネーム」に同等の名前を設定することはお控えください。\n\n"\
                           "ユーザ名の設定方法は下記URLからご確認ください。\n"\
                           "https://setup-lab.net/discord-nickname-change/\n"\

        },
        "both": "コマンド、および名前双方に想定されていないフォーマットを検知しました。\n"\
                "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                "(例)\n"\
                "・コマンド: /curr 001\n"\
                "・名前: テスト太郎_00001\n\n"\
                "下記リンクを参考に「サーバープロフィール」タブからサーバーニックネームを変更してください。\n"\
                "https://setup-lab.net/discord-nickname-change/",

        "unknown": "不明なエラーを検知しました。\n"\
                   "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                   "(例)\n"\
                   "・コマンド: /curr 001\n"\
                   "・名前: テスト太郎_00001\n\n"\
                   "エラーが解消されない場合、「問い合わせ」チャットにてご連絡ください。",

    },
    "message": {
        "command": {
            "/curr": "[/curr ] could not found.",
            "digit": "Integer Missing.",
            "excess": "Too Bigger index has detected.",
        },
        "user": {
            "digit": "Integer Missing.",
            "_": "Underscore has not detected.",
            "nodigit": "Name has no digit.",
            "dbidkey": "Non-existent db key has detected.",
            "userprofile": "Display name is set 'User Profile'.",
        },
        "both": "command and name detect error.",
        "unknown": "Unknown error has detected.",
    }
}

error_dict_reservation_cycle = {
    "annaounce": {
        "command": {
            "/curr": "想定されていないフォーマットのコマンドを検知しました。\n"\
                     "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                     "・コマンドの最初は「/curr」で始めてください。\n"\
                     "・「/curr」と数字の間にスペースを入れてください。\n\n"\
                     "(例) /curr 001",

            "digit": "想定されていないフォーマットのコマンドを検知しました。\n"\
                     "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                     "・3桁0埋めの数字で入力してください。\n\n"\
                     "(例) /curr 001",

            "excess": "想定されていないフォーマットのコマンドを検知しました。\n"\
                      "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                      "・コマンドに設定する数字は「335」以下にしてください。\n\n"\
                      "・カリキュラム番号がわからない場合、Wikiの「カリキュラム対応表」をご確認ください。\n\n"\
                      "(例) /curr 335",

        },
        "user": {},
    },
    "message": {
        "command": {
            "/curr": "[/curr ] could not found.",
            "digit": "Integer Missing.",
            "excess": "Too Bigger index has detected.",
        },
        "user": {},
        "both": "command and name detect error.",
        "unknown": "Unknown error has detected.",
    }
}