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
    def send_ban_mail(self, username_with_db_id, id):
        username_dbid_pair = username_with_db_id.split("_")
        username = username_dbid_pair[0]
        database_id = database_id_list[username_dbid_pair[1]]

        subject = '【重要なお知らせ】退会措置とIT技術学習費用のお支払いについて'
        text = username + '様\n\n'\
            'お世話になっております。\n'\
            'Work Ready運営でございます。\n\n'\
            '大変申し訳ございませんが、この度、当スクールの利用規約に違反が判明しました。これに基づき、強制退会措置を取らせていただくこととなりました。また、IT技術学習費用についての請求もさせていただきます。\n\n'\
            '以下のリンクより、請求金額の確認と一括でのお支払いをお願い申し上げます。なお、お支払い期限は本メール受信月の月末となっております。\n'\
            '**https://buy.stripe.com/14kcPg8qlcgo0Rq9AF**\n\n'\
            '何卒、ご理解とご協力のほどよろしくお願い申し上げます。'

        message = MIMEText(text)
        message['Subject'] = subject
        # message['From'] = self._source_address
        message['From'] = email.utils.formataddr(
            ('Work Ready運営', self._source_address))
        message['To'] = self._get_mail_address_from_id(database_id, id)

        self._smtp_obj.send_message(message)
    """

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
