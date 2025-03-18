"""
@file database_id_list.py
@date 2023/07/31(月)
@author 藤原光基
@brief 進捗登録先ID集
@details 進捗登録先のIDについてまとめた辞書型変数。
@note ID参照方法・・・
@note 1.notionの一般代理店様ページに飛ぶ
@note 2.「...」から「Copy link to View」をクリックする
@note 3.コピーしたリンクから下記を抽出する
@note   https://www.notion.so/[database_id](ここ！！))?v=[view_id]&...
@note
@note 参考URL
@note https://stackoverflow.com/questions/73045760/how-do-i-find-the-database-id-of-an-inline-notion-database
@bar 編集日時 編集者 編集内容
@bar 2023/07/31(月) 藤原光基 新規作成
@bar 2023/08/20(日) 藤原光基 00006(D-GATE様)追加
@bar 2023/09/08(金) 藤原光基 00007(UooD株式会社様)追加
@bar 2023/09/19(火) 藤原光基 00008(合同会社Trust me様)追加
@bar 2023/09/18(月) 藤原光基 00008(Trust me様)追加
@bar 2023/09/21(木) 藤原光基 00009(CHEER ONE様)追加
@bar 2023/09/25(月) 藤原光基 99999(Test DB)追加
@bar 2023/10/20(金) 藤原光基 00010(北岡謙信様)追加
@bar 2023/10/20(金) 藤原光基 00011(株式会社リンクシア様)追加
@bar 2023/10/20(金) 藤原光基 00012(株式会社エスフリー様)追加
@bar 2023/11/14(火) 藤原光基 00013(株式会社ピロリズム様)追加
@bar 2023/11/14(火) 藤原光基 00014(株式会社Leaps様)追加
@bar 2023/11/16(木) 藤原光基 00015(佐土原奨様)追加
@bar 2023/11/27(月) 藤原光基 00016(後藤将矢様)追加
@bar 2023/12/21(木) 藤原光基 00017(ウィディア株式会社様)追加
@bar 2024/01/20(土) 藤原光基 00018(株式会社PMAgent様)追加
@bar 2024/01/20(土) 藤原光基 00019(株式会社オーバージェット様)追加
@bar 2024/01/20(土) 藤原光基 00020(アスユメLabo.様)追加
@bar 2024/02/08(木) 藤原光基 00021(植松 仁様)追加
@bar 2024/02/08(木) 藤原光基 00022((株)LSC様)追加
@bar 2024/03/04(月) 藤原光基 instructor_id_list追加
@bar 2024/03/15(金) 藤原光基 講師00003(和田さん)追加
@bar 2024/04/05(金) 藤原光基 講師00004(内山さん)追加
"""

database_id_list = {
    "00000": "0ad4e40097ae4ed589e454bef7cc1109",  # iConnect様
    "00001": "2decda34fa914958a61bd5e23842b29b",  # PMエージェント様
    "00002": "ab61771e3931426eadcbf8e363d3d3d8",  # 板尾大輔様
    "00003": "3dedcc2dc7e949218aa81eed568692dc",  # 黒木彩名様
    "00004": "fa5c4f1947fe430096d52dd99be4230e",  # 株式会社リード様
    "00005": "f2cb4ada0b4c4bde818398f94eabbf0d",  # 丹内光太郎様
    "00006": "61a2a6136ad64c87a8f46efed5988ba9",  # D-GATE様
    "00007": "1f201e1363cc4be2a0fe2fffb323ab5b",  # UooD株式会社様
    "00008": "67b1cdbdbbae4d23bbe8b8d962629981",  # 合同会社Trust me様
    "00009": "aac18bb3dc6e435b9351c3ab70f48074",  # 株式会社CHEER ONE様
    "00010": "ccbf0a53c80543d096550dd7f649d04c",  # 北岡謙信様
    "00011": "53934568499842be8ed1648071cd81b9",  # 株式会社リンクシア様
    "00012": "d1c3d850e76d49b69ece74e146219529",  # 株式会社エスフリー様
    "00013": "770d141a57ff4dbaa03baf226ef2df45",  # 株式会社ピロリズム様
    "00014": "ac9f939f2fee4cd3bc12a3431e6ddca9",  # 株式会社Leaps様
    "00015": "8120cb36695a469a850ad737e4523ecf",  # 佐土原奨様
    "00016": "d297d98075e44a2ea0d7ecd061806928",  # 後藤将矢様
    "00017": "04e8aa53338d485fb3290b75797e568d",  # ウィディア株式会社様
    "00018": "9ef18f4c5268493f814f834dcd2cd83d",  # 株式会社PMAgent様
    "00019": "881b8d42c9fe4d6db8c473871a4a1644",  # 株式会社オーバージェット様
    "00020": "3638e9072b90418fab16658eb699f848",  # アスユメLabo.様
    "00021": "5fa3809dab02448c969f6ef54156ce5d",  # 植松　仁様
    "00022": "4f79e52c85364dafb86c0df61bd7312c",  # (株)LSC様
    "00023": "a9b7ba1b7c2f43c3a47e1efd92d6dc7e",  # 合同会社ExAd様
    "00024": "19b6de70ecf04fa383b639c90186ce0c",  # 佐藤祐平様
    "00025": "ef1826b407d748919ff51322151e8ca1",  # 株式会社鈴菊HD様
    "00026": "aae626f3df8f4f3cb4423772a025d987",  # Assh様
    "00027": "6ce33427a01c4132ad10ca6ec9afbdfc",  # 株式会社RESTA様
    "00028": "15f795f96fce81da8f81d0a7592b2a9a",  # 中村　勇真様
    "00029": "16f795f96fce81a7b3fff05e5dbcfacc",  # 秋山美里様
    "00030": "190795f96fce81e8b6d6ffcb02c86b32",  # 鈴木郁哉様 
    "99999": "bee6832fb35c4c2c8ac829b3338c5a96",  # テストDB(共有)
    # "test": "0235ca24d99a4fb49f0b1a30d54601f8", # テストDB(メール送信)
}


instructor_id_list = {
    "講師DB": {
        "name": "講師DB",
        "mail": None,
        "id": "366f97862ac54ffdb341fb08301015b9",
    },
    "00001": {
        "name": "福山成",
        "mail": "fukunaru11@gmail.com",
        "id": "826887e69e6040c2a8d491c0ad91c03a",
    },
    # "00002": {
    #     "name": "高橋毅",
    #     "mail": "tk_031@outlook.jp",
    #     "id": "108c5f59a7fb404e990ed3021d1ffc11",
    # },
    # "00003": {
    #     "name": "和田颯",
    #     "mail": "hayato2121wada@gmail.com",
    #     "id": "66c8648bf8b54e7283ca3e314cccb9c0",
    # },
    "00004": {
        "name": "内山智明",
        "mail": "acm.lock.apocalypse@gmail.com",
        "id": "fbba05a7166a4118a0ec8fd1eb4f8a62",
    },
    "00005": {
        "name": "藤原浩司",
        "mail": "koji.0805.fuji@gmail.com",
        "id": "54b914a95a264ec8a4e515cd603cf083",
    },
    "00006": {
        "name": "下田晃雅",
        "mail": "sky1618item@gmail.com",
        "id": "a3e44576699447b082bcb1e6083d1504",
    },
    # "00007": {
    #     "name": "山形敦己",
    #     "mail": "kirikiri.3535@gmail.com",
    #     "id": "d3496467e15f484cbcc1f1ebda325fed",
    # },
    "00008": {
        "name": "濱田優一",
        "mail": "ilovemrchildrensazan@gmail.com",
        "id": "ed55fc9001a345208383a96a1e1bc0be",
    },
}
