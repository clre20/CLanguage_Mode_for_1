import requests
from bs4 import BeautifulSoup
import os
import json

# 讀取 urls.json 檔案
with open("data/urls.json", "r", encoding="utf-8") as f:
    urls = json.load(f)

# 建立資料夾
os.makedirs("data", exist_ok=True)

# 爬取每個網址並存成 txt
for i, url in enumerate(urls):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 抓取 <p> 標籤中的文字
        paragraphs = soup.find_all('p')
        text = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

        # 儲存成 txt 檔案
        with open(f"data/article_{i+1}.txt", "w", encoding="utf-8") as f:
            f.write(text)

        print(f"已儲存: article_{i+1}.txt")

    except Exception as e:
        print(f"錯誤於 {url}: {e}")

print("爬蟲完成，資料已儲存到 data 資料夾。")