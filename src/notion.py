"""
@file notion.py
@date 2023/09/15(月)
@author 藤原光基
@brief 進捗登録bot
@details 進捗コマンドに応じてnotion上の進捗管理DBに進捗率を登録する。
@bar 編集日時 編集者 編集内容
@bar 2023/07/31(月) 藤原光基 新規作成
"""

import datetime

from settings.settings_dict import settings_dict
from notion_client import Client


class Notion:

    def __init__(self):
        self._notion = Client(auth=settings_dict["TOKEN"]["NOTION"])

    def select(self, database_id, filter_dict):
        key = list(filter_dict.keys())[0]
        value = filter_dict[key]

        """
        results = self._notion.databases.query(
            **{
                "database_id": database_id,
                "filter": {
                    "property": key,
                    "title": {
                        "contains": value,
                    },
                },
            }).get("results")
        """
        filter = self._get_select_filter_equal(filter_dict)
        results = self._notion.databases.query(
            **{
                "database_id": database_id,
                "filter": filter,
            }).get("results")
        return results

    def update(self, page_id, filter_dicts_list):
        properties = self._add_property(filter_dicts_list)
        print("properties: ", properties)
        self._notion.pages.update(
            **{
                "page_id": page_id,
                "properties": properties
            }
        )

    def create(self, database_id, filter_dicts_list):
        properties = self._add_property(filter_dicts_list)
        self._notion.pages.create(
            **{
                "parent": {"database_id": database_id},
                "properties": properties
            }
        )

    def _add_property(self, filter_dicts_list):
        result = {}
        for key, value in filter_dicts_list[0].items():
            if key == 'カリキュラムNo':
                result[key] = {
                    'rich_text': [{
                        'text': {
                            'content': value
                        }
                    }]
                }
            elif key == 'ユーザーID':
                result[key] = {
                    'rich_text': [{
                        'text': {
                            'content': value
                        }
                    }]
                }
            elif key == '講師番号':
                result[key] = {
                    'rich_text': [{
                        'text': {
                            'content': value
                        }
                    }]
                }
            elif key == '名前':
                result[key] = {
                    'title': [{
                        'text': {
                            'content': value
                        }
                    }]
                }
            elif key == '代理店番号':
                result[key] = {
                    'rich_text': [{
                        'text': {
                            'content': value
                        }
                    }]
                }
            elif key == 'カリキュラム名':
                result[key] = {
                    'rich_text': [{
                        'text': {
                            'content': value
                        }
                    }]
                }
            elif key == 'カリキュラム進捗(%)':
                result[key] = {
                    'rich_text': [{
                        'text': {
                            'content': value
                        }
                    }]
                }
            elif key == '在籍状況':
                result[key] = {
                    'select': {"name": value}
                }
            elif key == '請求書送付状況':
                result[key] = {
                    'select': {"name": value}
                }
            elif key == 'プラン名':
                result[key] = {
                    'rich_text': [{
                        'text': {
                            'content': value
                        }
                    }]
                }
            elif key == '進捗更新日時':
                result[key] = {
                    "date": {
                        "start": value
                    }
                }
            elif key == '請求状況':
                result[key] = {
                    'select': {"name": value}
                }
            elif key == '30分無料相談チケット':
                result[key] = {
                    "number": value
                }
            elif key == '30分有料相談チケット':
                result[key] = {
                    "number": value
                }
            elif key == '60分有料相談チケット':
                result[key] = {
                    "number": value
                }
            elif key == '作成日時':
                result[key] = {
                    "created_time": value
                }
            elif key == '受講コース':
                result[key] = {
                    'rich_text': [{
                        'text': {
                            'content': value
                        }
                    }]
                }

        return result

    def _get_select_filter_equal(self, filter_dict):
        key = list(filter_dict.keys())[0]
        value = filter_dict[key]

        if    ((key == 'カリキュラムNo')
           or  (key == 'ユーザーID')
           or  (key == '講師番号')
           or  (key == '名前')
           or  (key == '代理店番号')
           or  (key == 'カリキュラム名')
           or  (key == 'カリキュラム進捗(%)')
           or  (key == 'プラン名')
           or  (key == '受講コース')):
            filter = {
                "property": key,
                "title": {
                    "contains": value,
                },
            }
        elif    ((key == '在籍状況')
             or  (key == '請求書送付状況')
             or  (key == '請求状況')):
            filter = {
                "property": key,
                "select": {
                    "equals": value,
                },
            }
        elif    ((key == '30分無料相談チケット')
              or (key == '30分有料相談チケット')
              or (key == '60分有料相談チケット')):
            filter = {
                "property": key,
                "number": {
                    "equals": value,
                },
            }
        elif key == '作成日時':
            created_time_filter = {
                "created_time": {}
            }
            if value["start_date"] != "": created_time_filter["created_time"]["on_or_after"] = value["start_date"]
            if value["end_date"] != "": created_time_filter["created_time"]["on_or_before"] = value["end_date"]
            filter = {
                "property": key,
                "filter": created_time_filter
            }
        elif key == '進捗更新日時':
            date_filter = {
                "date": {}
            }
            if value["start_date"] != "": date_filter["date"]["on_or_after"] = value["start_date"]
            if value["end_date"] != "": date_filter["date"]["on_or_before"] = value["end_date"]
            filter = {
                "property": key,
                "filter": date_filter
            }
        else:
            filter = None

        return filter