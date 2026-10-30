
import requests
from bs4 import BeautifulSoup
import time
import csv

# 武蔵野大学のトップページ
base_url = "https://www.musashino-u.ac.jp"
start_url = base_url + "/"

# URLを保存するリスト
url_list = [start_url]

# 重複したURLを防ぐためのset
url_set = {start_url}

# URLとタイトルを保存する辞書
page_data = {}

# 取得するページ数の上限（動作確認用）
MAX_PAGES = 10000

# URLを順番に取得する
while url_list and len(page_data) < MAX_PAGES:

    # リストの先頭からURLを取り出す
    url = url_list.pop(0)

    try:
        print("アクセス開始:", url, flush=True)

        # サーバーへの負荷を減らすため1秒待つ
        time.sleep(1.0)

        # Webページを取得する
        response = requests.get(url, timeout=(5, 15))
        response.raise_for_status()

        # HTMLを解析する
        soup = BeautifulSoup(response.content, "html.parser")

        # titleタグの文字列を取得する
        if soup.title:
            title = soup.title.get_text(strip=True)
        else:
            title = ""

        # 辞書にURLとタイトルを保存する
        page_data[url] = title

        print("取得成功:", url)
        print("タイトル:", title)
        print("--------------------")

        # ページ内のリンクをすべて取得する
        links = soup.find_all("a")

        for link in links:

            href = link.get("href")

            if not href:
                continue

            # 不要なリンクを除外する
            if href.startswith("//"):
                continue

            if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
                continue

            # 同じドメインのURLだけを取得する
            if href.startswith("/"):
                next_url = base_url + href

            elif href.startswith(base_url + "/") or href == base_url:
                next_url = href

            else:
                continue

            # URL末尾の#以降を削除する
            next_url = next_url.split("#")[0]
            
            # PDFファイルを除外する
            if next_url.lower().endswith(".pdf"):
                continue

            # まだ取得していないURLをリストに追加する
            if next_url and next_url not in url_set:
                url_set.add(next_url)
                url_list.append(next_url)

    except requests.RequestException as e:
        # エラーが発生したURLを飛ばして次へ進む
        print("アクセスエラー:", url)
        print("エラー内容:", e)
        print("次のURLへ進みます。")
        print("--------------------")
        continue


# 最後にCSVファイルへ保存する
with open("sitemap.csv", "w", newline="", encoding="utf-8-sig") as file:

    writer = csv.writer(file)

    # CSVの見出し
    writer.writerow(["URL", "タイトル"])

    # 辞書の内容を書き込む
    for url, title in page_data.items():
        writer.writerow([url, title])


# 最終結果を表示する
print("取得したページ数:", len(page_data))
print("CSVファイルを保存しました。")
