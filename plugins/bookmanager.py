# coding: utf-8

from slackbot.bot import respond_to
from slackbot.bot import default_reply
import requests
import sqlite3

# ---------- setting ----------
# googleBookAPIのエンドポイントとなるURL
googleBookAPI_endpoint = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'
# データベースファイル名
db_filename = 'book_manager.sqlite3'
# -----------------------------


# デフォルトの応答
@default_reply()
def default_func(message):
    msg = "＜？"
    message.reply(msg)


# Google Books APIへ問い合わせて、本のタイトルを返すメソッド
def get_book_information(isbn):
    url = googleBookAPI_endpoint + isbn
    response = requests.get(url)
    if response.status_code == 200:
        if response.json()["totalItems"] == 1:
            title = response.json()["items"][0]["volumeInfo"]["title"]
            return title
    return False


# DBに問い合わせてユーザIDをユーザ名に変換するメソッド
def userid_to_username(userid):
    # DBに問い合わせ
    db = sqlite3.connect(db_filename)
    c = db.cursor()
    c.execute('SELECT username FROM users WHERE userid = ?', (userid,))
    row = c.fetchone()
    db.close()

    # DBにあった場合はユーザ名を返却、なかった場合はユーザIDを返却
    if row is None:
        return userid
    else:
        return row[0]


# add コマンド
# => 本を購入した時に呼び出して、本棚への登録を行います。
@respond_to(r'^add\s+\S.*')
def add_command_func(message):
    # コマンドと引数に分割
    command, message_isbn = message.body['text'].split(None, 1)
    message_userid = message.body['user']

    # コマンド実行
    book_title = get_book_information(message_isbn)
    if book_title is False:
        # googleBookAPIへの問い合わせで本が見つからなかった場合、エラーメッセージを返す
        msg = 'すみません...その本は見つかりませんでした'
        message.reply(msg)
        return False
    else:
        # googleBookAPIへの問い合わせで本が見つかった場合、本棚に加えてメッセージを返す
        db = sqlite3.connect(db_filename)
        c = db.cursor()
        c.execute("INSERT INTO bookshelf VALUES (null, ?, ?, ?)", (message_userid, message_isbn, book_title))
        db.commit()
        db.close()

        msg = userid_to_username(message.body['user']) + 'さん、「' + book_title + '」を買ったんですね！本棚に加えておきました。'
    message.reply(msg)
    return True


# check コマンド
# => 指定したISBNの本が本棚に登録されているか（＝所有しているか）をチェックします。
@respond_to(r'^check\s+\S.*')
def check_command_func(message):
    # コマンドと引数に分割
    command, message_isbn = message.body['text'].split(None, 1)
    message_userid = message.body['user']

    # コマンド実行
    # コマンドを置く多々ユーザが本を持っているかどうかをDBで検索
    msg = ""
    db = sqlite3.connect(db_filename)
    c = db.cursor()
    c.execute("SELECT count(id) FROM bookshelf WHERE userid = ? AND isbn = ?", (message_userid, message_isbn,))
    num = c.fetchone()[0]

    if num >= 1:
        msg += "その本は既に" + userid_to_username(message_userid) + "さんの本棚に" + str(num) + "冊ありますよ！"
    else:
        msg += userid_to_username(message_userid) + "さんはその本はまだ持っていませんね。"

    # 他に本を持っているユーザをDBで検索
    c.execute("SELECT userid FROM bookshelf WHERE userid != ? AND isbn = ?", (message_userid, message_isbn,))
    userid_list = c.fetchall()

    if len(userid_list) >= 1:
        msg += "その本を持っている人は"
        for userid in userid_list:
            msg += "「" + userid_to_username(userid[0]) + "さん」"
        msg += "です。"
    else:
        msg += "他にその本を持っている人はいなさそうです。"
    message.reply(msg)

    db.close()
    return True


# show コマンド
# => 自分が所持している本のタイトルをリストで返信します。
@respond_to(r'^show')
def show_command_func(message):
    message_userid = message.body['user']

    # ここからコマンド実行
    # 所持している本のリストをデータベースへ問い合わせ
    db = sqlite3.connect(db_filename)
    c = db.cursor()
    c.execute("SELECT title FROM bookshelf WHERE userid = ?", (message_userid,))
    # テキストに整形してからslackで返信
    book_list = ""
    for row in c.fetchall():
        book_list = book_list + "、" + row[0]
    message.reply("あなたが持っている本は" + book_list + "です。")
    db.close()


# create database コマンド【管理者用】
# => データベースを作成する。最初に1回実行すること。
@respond_to(r'^create\s+database')
def create_database_func(message):
    db = sqlite3.connect(db_filename)
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS bookshelf("
              "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
              "userid TEXT NOT NULL, isbn INTEGER NOT NULL,"
              "title TEXT NULL);")
    c.execute("CREATE TABLE IF NOT EXISTS users("
              "userid TEXT NOT NULL PRIMARY KEY,"
              "username TEXT NOT NULL);")
    db.commit()
    db.close()

    message.reply("データベースを作成しました。")
