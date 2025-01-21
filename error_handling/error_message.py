"""
@file error_message.py
@date 2023/07/31(月)
@author 藤原光基
@brief エラー検知機能
@details 進捗登録用コマンド、もしくは生徒の名前にエラーが検知された場合、
@details エラーの旨をチャットに表示し、検知時刻やその際の生徒名とともにログに記載する。
@note エラーの文面については同フォルダ内「error_dict.py」を参照
@bar 編集日時 編集者 編集内容
@bar 2023/07/31(月) 藤原光基 新規作成
"""
from .error_dict import error_dict
from settings.database_id_list import database_id_list
from settings.settings_dict import settings_dict

class ErrorMessage:

    def __init__(self, logger):
        self._logger = logger
        self._error_dict = error_dict
        self._database_id = database_id_list

        self._error_message = None
        self._error_annaounce = None

    def get_message(self, message):

        try:

            # get message info
            command = message.content  # command statement
            get_messemger_name = message.author.display_name  # displaied user name in chat

            # check error
            err_message_command, err_announce_command = self._check_command(command)
            err_message_username, err_annaounce_username = self._check_user(message)
          
            # no error
            if not (bool(err_message_command) | bool(err_message_username)):

                if "\n" in command:
                    command = command.split('\n')[-1]

                user_name = get_messemger_name.split("_")[
                    0]  # explicit full name from displaied user name
                database_id = database_id_list[get_messemger_name.split(
                    "_")[1]]  # explicit database id from displaied user name
                curr_number = command[6:].zfill(
                    3)  # explicit curriculum number from command statement

                return user_name, database_id, curr_number

            # any error
            else:

                # command and name error
                if bool(err_message_command) & bool(err_message_username):
                    self._error_message = error_dict["message"]["both"]
                    # self._error_annaounce = error_dict["annaounce"]["both"]
                    self._error_annaounce = error_dict["annaounce"]["both"]
                    self._error_annaounce = self._add_messager_info_to_announce_for_command(message, self._error_annaounce)

                # command error
                elif bool(err_message_command):
                    self._error_message = err_message_command
                    # self._error_annaounce = err_announce_command
                    self._error_annaounce = err_announce_command
                    self._error_annaounce = self._add_messager_info_to_announce_for_command(message, self._error_annaounce)

                # name error
                elif bool(err_message_username):
                    self._error_message = err_message_username
                    # self._error_annaounce = err_annaounce_username
                    self._error_annaounce = err_annaounce_username
                    self._error_annaounce = self._add_messager_info_to_announce_for_username(message, self._error_annaounce)

                raise ValueError(self._error_message)

        except Exception as e:

            # get error log
            print("exception e(___DEBUG___): ", e)
            err_line = 'command: {}, error message: {}, username: {}'.format(
                command, e, get_messemger_name)
            self._logger.error(err_line)

            # unknown error
            if self._error_annaounce is None:
                self._error_annaounce = error_dict["annaounce"]["unknown"]

            return get_messemger_name, "", ""

    def get_error_message(self):
        return self._error_message

    def get_error_announce(self):
        return self._error_annaounce

    # TODO
    def _check_command(self, command):
        err_message = None
        err_annaounce = None

        if "\n" in command:
            command = command.split('\n')[-1]

        if command[:6] != '/curr ':
            err_message = self._error_dict["message"]["command"]["/curr"]
            err_annaounce = self._error_dict["annaounce"]["command"]["/curr"]
        elif not command[6:].isdigit():
            err_message = self._error_dict["message"]["command"]["digit"]
            err_annaounce = self._error_dict["annaounce"]["command"]["digit"]
        elif int(command[6:]) > settings_dict["CURRICULUM_NUMBER_RANGE"]["PORTOFOLIO"]["MAX"]:
            err_message = self._error_dict["message"]["command"]["excess"]
            err_annaounce = self._error_dict["annaounce"]["command"]["excess"]
        return err_message, err_annaounce


    # TODO
    def _check_user(self, message):
        err_message = None
        err_annaounce = None

        messemger_name = message.author.display_name

        if message.author.name == messemger_name:
            err_message = self._error_dict["message"]["user"]["userprofile"]
            err_annaounce = self._error_dict["annaounce"]["user"]["userprofile"]
        elif (not messemger_name[-1].isdigit()) | (messemger_name[-1] == "_"):
            err_message = self._error_dict["message"]["user"]["nodigit"]
            err_annaounce = self._error_dict["annaounce"]["user"]["nodigit"]
        elif not messemger_name[-5:].isdigit():
            err_message = self._error_dict["message"]["user"]["digit"]
            err_annaounce = self._error_dict["annaounce"]["user"]["digit"]
        elif messemger_name[-6] != '_':
            err_message = self._error_dict["message"]["user"]["_"]
            err_annaounce = self._error_dict["annaounce"]["user"]["_"]
        elif not messemger_name[-5:] in database_id_list.keys():
            err_message = self._error_dict["message"]["user"]["dbidkey"]
            err_annaounce = self._error_dict["annaounce"]["user"]["dbidkey"]
        return err_message, err_annaounce

    def _add_messager_info_to_announce_for_username(self, message, err_announce_before):
        messager_id = message.author.id
        messager_name = message.author.name

        err_announce_after = "<@" + str(messager_id) + ">さん\n\n"+\
                             err_announce_before + "\n\n"\
                             "なお、運営側で検知しているお名前は下記のとおりです。\n"+\
                             "  " + messager_name
        return err_announce_after

    def _add_messager_info_to_announce_for_command(self, message, err_announce_before):
        messager_id = message.author.id
        messager_name = message.author.name

        err_announce_after = "<@" + str(messager_id) + ">さん\n\n"+\
                             err_announce_before + "\n\n"\
                             # "なお、運営側で検知しているお名前は下記のとおりです。\n"+\
                             # "  " + messager_name
        return err_announce_after

class ErrorMessageReserveConsultation(ErrorMessage):

    def __init__(self, logger):
        super().__init__(logger)

    def get_message(self, message):

        try:
            # get message info
            command = message.content  # command statement
            get_messemger_name = message.author.display_name  # displaied user name in chat

            # check error
            err_message_command, err_announce_command = self._check_command(command)
            err_message_username, err_annaounce_username = self._check_user(message)

            # no error
            if not (bool(err_message_command) | bool(err_message_username)):

                # message = ""
                # message += "ご相談内容を受理いたしました。\n"
                # message += "下記URLからご希望の相談会への予約をお願いいたします。\n\n"

                # return message
                # return ""
                pass

            # any error
            else:

                # command and name error
                if bool(err_message_command) & bool(err_message_username):
                    self._error_message = error_dict["message"]["both"]
                    self._error_annaounce = error_dict["annaounce"]["both"]

                # command error
                elif bool(err_message_command):
                    self._error_message = err_message_command
                    self._error_annaounce = err_announce_command

                # name error
                elif bool(err_message_username):
                    self._error_message = err_message_username
                    self._error_annaounce = err_annaounce_username

                raise ValueError(self._error_message)

        except Exception as e:

            # get error log
            print("exception e(___DEBUG___): ", e)
            err_line = 'command: {}, error message: {}, username: {}'.format(
                command, e, get_messemger_name)
            self._logger.error(err_line)

            # unknown error
            if self._error_annaounce is None:
                self._error_annaounce = error_dict["annaounce"]["unknown"]

            # return get_messemger_name

    def _check_content_contain(self, content, key_word):
        return key_word in content

    def _check_command(self, command):
        print("_check_command executed.")
        err_message = None
        err_annaounce = None

        message_key_word_list = ['【カリキュラム番号】', '【質問内容】', '【何をどう調べたか】', '【Gitクローン用URL】', 'https://']
        error_key_word_list = list(filter(lambda key_word: not key_word in command, message_key_word_list))
        print("error_key_word_list: ", error_key_word_list)

        if len(error_key_word_list) > 0:
            err_annaounce = "ご相談内容につきまして下記項目が検知されませんでした。\n"\
                            "***\n\n"

            for error_key_word in error_key_word_list:
                if error_key_word == 'https://':
                    err_annaounce += '・' + '(Gitクローン用URL)\n'
                else:
                    err_annaounce += '・' + error_key_word + "\n"

            err_annaounce += "***\n\n"+\
                             "お手数ですが、\n"+\
                             "下記項目(文字列完全一致)を追加の上\n"+\
                             "再度相談内容をご展開いただきますようお願いいたします。"
            err_message = 'missing content has detected.'            

        return err_message, err_annaounce

    def _check_user(self, user):
        print("_check_user executed.")
        err_message = None
        err_annaounce = None

        return err_message, err_annaounce
