"""
@file keep_alive.py
@date 2023/07/01(土)
@author 新家魁人
@brief bot定期実行処理
@details 現状の構成では既存のbotが1カ月程度で処理が中断される。
@details それを解消する機能。
@bar 編集日時 編集者 編集内容
@bar 2023/07/01(土) 新家魁人 新規作成
@bar 2023/07/31(月) 藤原光基 コメント追加
"""
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()