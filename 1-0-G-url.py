import requests
from bs4 import BeautifulSoup
import json
import time

def google_news_scrape(query, max_results=100):
    urls = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for start in range(0, max_results, 10):
        url = f"https://www.google.com/search?q={query}&tbm=nws&start={start}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a"):
            href = a.get("href")
            if href and href.startswith("http") and "google.com" not in href:
                urls.append(href)
        time.sleep(20)
    return list(set(urls))  # 去重複

# 主題設定（可修改）
query = "AI technology"
max_results = 1000  # 可改成 500 或更多

# 抓資料
urls = google_news_scrape(query, max_results)

# 儲存為 JSON 檔
with open("data/urls.json", "w", encoding="utf-8") as f:
    json.dump(urls, f, indent=2, ensure_ascii=False)

print(f"成功儲存 {len(urls)} 筆資料到 urls.json")