import datetime
import zoneinfo
import platform

from settings.settings_dict import settings_dict


def get_progress_in_comment(content):
    if "\n" in content:
        content = content.split('\n')[-1]
    # else:
    #     content = content

    # 進捗コマンドから進捗抽出
    progress = int(content.split(" ")[1])

    return progress


def get_unit_datetime():
    """
    if platform.platform().split('-')[0] == 'Linux':
        now_tz = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        temp_dt = now_tz.strftime('%Y-%m-%d %H:%M:%S.%f')
        now = datetime.datetime.strptime(temp_dt, '%Y-%m-%d %H:%M:%S.%f')
    else:
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    """
    now = datetime.datetime.now(zoneinfo.ZoneInfo('Asia/Tokyo'))

    return now


def get_command(message):
    content = message.content
    if len(content.split('\n')) > 0:
        content = content.split('\n')[-1]
    return content


def return_mail_content(sending_type, name):
    now = datetime.date.today().strftime("%Y-%m-%d")
    term = settings_dict["SENDING"][sending_type]["TERM"]
    mail_dict = get_mail_content(sending_type, name)
    title = mail_dict["TITLE"]
    content = mail_dict["CONTENT"]
    return f"{now}\n{name}さんに{term}進捗がない方用のメールを送信しました。\n\n【タイトル】\n{title}\n\n【文面】\n{content}\n"


def return_dm_content(sending_type, name):
    now = datetime.date.today().strftime("%Y-%m-%d")
    term = settings_dict["SENDING"][sending_type]["TERM"]
    content = get_dm_content(sending_type, name)
    return f"{now}\n{name}さんに{term}進捗がない方用のDMを送信しました。\n\n【DM文面】\n{content}\n"


# def get_dm_content(sending_type, id):
def get_dm_content(sending_type, name):
    content_ = ''
    content_ = settings_dict["SENDING"][sending_type]["DM"]
    content = name + "さん\n\n" + content_
    return content


# def get_mail_content(sending_type, name, date):
def get_mail_content(sending_type, name):
    content = settings_dict["SENDING"][sending_type]["MAIL"].copy()
    # content = settings_dict["SENDING"][sending_type]["MAIL"]
    content["CONTENT"] = name + "様\n\n" + content["CONTENT"]
    # content["CONTENT"] = content["CONTENT"].replace("{}", date)
    return content


def return_mail_past_content(sending_type, name):
    print("input(return_mail_content): ", sending_type, name)
    now = datetime.date.today().strftime("%Y-%m-%d")
    term = settings_dict["SENDING"][sending_type]["TERM"]
    mail_dict = get_mail_content(sending_type, name)
    title = mail_dict["TITLE"]
    content = mail_dict["CONTENT"]
    return f"{now}\n{name}さんに入校してから{term}経過したことを報告するメールを送信しました。\n\n【タイトル】\n{title}\n\n【文面】\n{content}\n"


def return_dm_past_content(sending_type, name):
    print("input(return_mail_content): ", sending_type, name)
    now = datetime.date.today().strftime("%Y-%m-%d")
    term = settings_dict["SENDING"][sending_type]["TERM"]
    content = get_dm_content(sending_type, name)
    return f"{now}\n{name}さんに入校してから{term}経過したことを報告するDMを送信しました。\n\n【DM文面】\n{content}\n"
