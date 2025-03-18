import smtplib

from email.mime.text import MIMEText
import email.utils

from settings.database_id_list import database_id_list
from src.notion import Notion

from settings.settings_dict import settings_dict
from src import common


class Mail:

    def __init__(self):
        self._smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
        self._smtp_obj.starttls()
        # self._smtp_obj.login('ra0039ip@gmail.com', 'repuxcyfahmxqrea')
        self._smtp_obj.login('workreadyschool@gmail.com', 'euyhubgultpeynqz')

        self._source_address = 'workreadyschool@gmail.com'

    def __del__(self):
        self._smtp_obj.close()

    """
    @func send_assigin_mail_to_instructor
    @brief 講師割り当て時メール送信機能
    @param instructor_info[dict] 講師情報
    @param student_info[dict] 受講生情報
    @return なし
    """
    def send_assigin_mail_to_instructor(self, instructor_info, student_info):
        subject = '【お知らせ】受講生割り当てのお知らせ'
        content = instructor_info["name"] + "様\n\n"\
            'いつもお世話になっております。\n'\
            'WorkReady運営です。\n\n'\
            'この度' + instructor_info["name"] + "様が下記受講生のご担当となりましたことをご連絡いたします。\n\n"\
            "・受講生氏名: " + student_info["name"] +"\n"\
            "・担当代理店: " + student_info["agent_id"] + "\n"\
            "・コース: " + student_info["course"] + "\n"\
            "・卒業予定日: " + student_info["graduate_date"] + "\n\n"\
            "つきましては「面談日程調整」チャンネルにて上記受講生と初回面談の日程調整をお願いいたします。\n"\
            "以上、よろしくお願いいたします。\n\n"\
            "WorkReady運営"

        self.send_mail(subject, content, instructor_info["mail"])

    def send_mail_accept_consultation_services(self, instructor_info, student_info):
        subject = '【お知らせ】相談会予約のお知らせ'
        content = instructor_info["name"] + "様\n\n"\
            'いつもお世話になっております。\n'\
            'WorkReady運営です。\n\n'\
            'この度、ご担当頂いております' + student_info["name"] + "様より相談会をご依頼いただきましたことをご連絡いたします。\n\n"\
            "■受講生氏名\n" + student_info["name"] +"\n\n"\
            "■担当代理店\n" + student_info["agent_id"] + "\n\n"\
            "■相談会チケット種別\n" + student_info["ticket"] + "\n\n"\
            "■相談会内容:\n" + student_info["message"] + "\n\n"\
            "つきましては「チケット制相談チャンネル」チャンネルにて上記受講生と相談会の日程調整をお願いいたします。\n"\
            "以上、よろしくお願いいたします。\n\n"\
            "WorkReady運営"

        self.send_mail(subject, content, instructor_info["mail"])

    def send_mail(self, username_with_db_id, id, exe_mode):
        username_dbid_pair = username_with_db_id.split("_")
        print("username_dbid_pair: ", username_dbid_pair)
        username = username_dbid_pair[0]
        database_id = database_id_list[username_dbid_pair[1]]

        print("exe_mode: ", exe_mode)
        # print(settings_dict.settings_dict["SENDING"][exe_mode]["MAIL"]["TITLE"])
        subject = settings_dict["SENDING"][exe_mode]["MAIL"]["TITLE"]
        # text = settings_dict.get_mail_content(settings_dict.settings_dict["SENDING"][exe_mode]["MAIL"]["CONTENT"], username)
        content_without_username = settings_dict["SENDING"][exe_mode]["MAIL"]["CONTENT"]
        content = username + '様\n\n' + content_without_username

        message = MIMEText(content)
        message['Subject'] = subject
        # message['From'] = self._source_address
        message['From'] = email.utils.formataddr(
            ('Work Ready運営', self._source_address))
        message['To'] = self._get_mail_address_from_id(database_id, id)
        message['Bcc'] = 'workreadyschool@gmail.com'

        self._smtp_obj.send_message(message)

    def _get_mail_address_from_id(self, database_id, id):
        notion_obj = Notion()

        filter_dict = {'ユーザーID': id}
        result = notion_obj.select(
            database_id=database_id, filter_dict=filter_dict)

        address = result[0]['properties']['メールアドレス']['email']
        return address


def test_send_ban_mail(target_member):
    from src.notion import Notion

    notion_obj = Notion()
    mail_obj = Mail()

    # メール送信処理
    for member_name, id in target_member.items():

        # idx = member_name.index("_")  # 「_」の番地取得
        # idx = member_name.split("_")[1]
        database_id = database_id_list["test"]  # databaseid取得
        # database_id = "0235ca24d99a4fb49f0b1a30d54601f8"
        username_with_db_id = member_name + "_" + "test"

        # filter_dict = {'ユーザーID': id}
        # result = notion_obj.select(database_id=database_id, filter_dict=filter_dict)

        # print("result: ", result)
        # print("address: ", result[0]['properties']['メールアドレス']['email'])

        mail_obj.send_ban_mail(username_with_db_id, id)
        # print("address send: ", address)


def main():

    # link = https://www.notion.so/47f8fd2dee904aff93271f5cd7834a85?v=42c1ee7a78f146a2ab72e937b794d2af&pvs=4
    # database_id = "47f8fd2dee904aff93271f5cd7834a85"
    target_member = {
        # '新海魁人': "1093885923214753802",
        # '林田翼': "822444947994050601",
        '藤原光基': "683267456202047507",
        # '菊池幸大': "1139466804973027378",
        # '武藤みさき': "888385794627235870"


        # '新海魁人': 1093885923214753802,
        # '林田翼': 822444947994050601,
        # '藤原光基': 683267456202047507,
        # '菊池幸大': 1139466804973027378,
        # '武藤みさき': 888385794627235870
    }

    test_send_ban_mail(target_member)


if __name__ == "__main__":
    main()
