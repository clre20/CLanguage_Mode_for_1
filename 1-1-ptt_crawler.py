# ptt_crawler.py
import requests
from bs4 import BeautifulSoup
import time
import random
import os

# 配置參數
BOARD_NAME = "Tainan" # 你想爬取的看板名稱，例如 "Gossiping", "Boy-Girl", "NBA"
MAX_PAGES = 5          # 爬取多少頁的文章 (一頁約 20 篇文章)
OUTPUT_DIR = "data" # 數據保存目錄
OUTPUT_FILENAME = os.path.join(OUTPUT_DIR, "ptt_dialogues.txt")

# PTT 相關 URL
PTT_BASE_URL = "https://www.ptt.cc"
PTT_OVER18_URL = "https://www.ptt.cc/ask/over18" # 滿 18 歲驗證
PTT_BOARD_URL = f"{PTT_BASE_URL}/bbs/{BOARD_NAME}/index.html"

# 設置請求頭，模擬瀏覽器行為
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Session 用於維持 Cookie (處理 over18 驗證)
session = requests.Session()

def over18_verification():
    print("嘗試通過 18 歲驗證...")
    try:
        # 第一次 GET 請求獲取驗證頁面，獲取可能的 CSRF token 或設置初始 cookie
        response = session.get(PTT_OVER18_URL, headers=HEADERS)
        
        # 檢查是否確實需要驗證 (如果直接跳過，可能已經有有效的 cookie)
        if "是否已滿十八歲？" not in response.text:
            print("無需 18 歲驗證，可能已有有效會話。")
            return True

        # 發送 POST 請求，帶上 'yes' 參數
        payload = {
            'yes': 'yes'
        }
        # 確保 POST 請求的 URL 是正確的，並且 session 會自動處理 cookie
        response = session.post(PTT_OVER18_URL, data=payload, headers=HEADERS)

        # 驗證是否成功跳轉到指定看板的首頁
        # PTT 驗證成功後會直接跳轉到看板首頁
        # 檢查響應的 URL 是否包含看板名稱，或者響應文本是否不再包含 "是否已滿十八歲？"
        if PTT_BOARD_URL in response.url or "是否已滿十八歲？" not in response.text:
            print("18 歲驗證成功！")
            return True
        else:
            print("18 歲驗證失敗。")
            print(f"當前響應 URL: {response.url}")
            # print(f"響應內容前 500 字: {response.text[:500]}") # 協助調試
            return False
    except requests.exceptions.RequestException as e:
        print(f"18 歲驗證請求錯誤: {e}")
        return False

def get_articles_on_page(url):
    articles = []
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status() # 對於 4xx/5xx 的響應拋出 HTTPError
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到所有文章的 div 標籤
        # class name 是 'r-ent'
        for div in soup.find_all('div', class_='r-ent'):
            title_tag = div.find('div', class_='title').find('a')
            if title_tag and 'href' in title_tag.attrs:
                title = title_tag.text.strip()
                article_url = PTT_BASE_URL + title_tag['href']
                articles.append({'title': title, 'url': article_url})
    except requests.exceptions.RequestException as e:
        print(f"獲取文章列表錯誤於 {url}: {e}")
    return articles

def parse_article_content(article_url):
    content = ""
    comments = []
    try:
        response = session.get(article_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 抓取文章內容
        main_content = soup.find('div', id='main-content')
        if main_content:
            # 移除不需要的標籤，例如推文、簽名檔、自動產生的資訊等
            for tag in main_content.find_all(['div', 'span'], class_=['push', 'f2', 'f4']):
                tag.extract()
            
            # 清理並獲取文章主要文本
            # 獲取所有文本內容，然後進行清理
            raw_text = main_content.get_text(separator='\n').strip()
            
            # 進一步清理：移除多餘的空行，去除文章開頭和結尾的發文資訊等
            lines = raw_text.split('\n')
            cleaned_lines = []
            for line in lines:
                stripped_line = line.strip()
                if stripped_line: # 只保留非空行
                    cleaned_lines.append(stripped_line)
            
            # 找到文章的結束標誌，例如「--」或「※ 發信站」
            # 簡單的方法是找最後一行包含文章資訊的行
            filtered_content_lines = []
            skip_lines = False
            for line in cleaned_lines:
                if "※ 發信站: 批踢踢實業坊(ptt.cc)" in line:
                    skip_lines = True
                    break
                if "※ 文章網址" in line:
                    skip_lines = True
                    break
                if "作者" in line and "看板" in line: # 通常是文章開頭
                    continue
                filtered_content_lines.append(line)
            
            if not skip_lines: # 如果沒有找到明顯的結束標誌，則全部保留
                 content = "\n".join(cleaned_lines).strip()
            else:
                 content = "\n".join(filtered_content_lines).strip()


            # 抓取推文
            for push_tag in soup.find_all('div', class_='push'):
                span_tags = push_tag.find_all('span')
                if len(span_tags) >= 3:
                    tag = span_tags[0].text.strip() # 推、噓、->
                    user = span_tags[1].text.strip() # 使用者ID
                    comment = span_tags[2].text.strip() # 推文內容
                    comments.append({'tag': tag, 'user': user, 'comment': comment})

    except requests.exceptions.RequestException as e:
        print(f"解析文章內容錯誤於 {article_url}: {e}")
    except Exception as e:
        print(f"處理文章 {article_url} 時發生未知錯誤: {e}")

    return content, comments

def main():
    # 建立數據保存目錄
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 執行 18 歲驗證
    if not over18_verification():
        print("無法通過 18 歲驗證，退出程式。")
        return

    current_page_url = PTT_BOARD_URL
    dialogues_collected = 0

    print(f"開始爬取 PTT 看板：{BOARD_NAME}")

    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f_out:
        for i in range(MAX_PAGES):
            print(f"正在爬取第 {i+1} 頁: {current_page_url}")
            articles = get_articles_on_page(current_page_url)
            
            if not articles:
                print(f"第 {i+1} 頁未找到文章或訪問失敗，停止爬取。")
                break

            for article in articles:
                print(f"  處理文章: {article['title']} ({article['url']})")
                article_content, comments = parse_article_content(article['url'])

                if article_content:
                    # 將文章內容作為「使用者：」的輸入
                    # 考慮文章標題也作為上下文的一部分
                    formatted_article = f"<s>使用者：請問關於「{article['title']}」這篇文章，內容是：\n{article_content}</s>\n"
                    f_out.write(formatted_article)
                    dialogues_collected += 1
                
                # 將推文作為「AI：」的回覆
                for comment_data in comments:
                    # 過濾掉空白推文和無效使用者
                    if comment_data['comment'].strip() and comment_data['user'].strip():
                        # 格式化為對話形式
                        formatted_comment = f"AI：{comment_data['user']}：{comment_data['comment']}"
                        f_out.write(formatted_comment)
                        f_out.write("\n")
                        dialogues_collected += 1
                
                f_out.write("\n") # 文章之間留空行
            
            time.sleep(random.uniform(1, 3)) # 每處理一篇文章後隨機延遲

            # 獲取下一頁的 URL (PTT 的「上一頁」按鈕實際是「最新頁」往前的按鈕)
            # 所以我們要找的其實是當前頁的 index 減 1 的頁面
            # PTT 頁碼是遞減的，因此要找到前一頁的 URL
            response = session.get(current_page_url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            # 找到 <div class="btn-group btn-group-paging">
            # 裡面有三個 <a> 標籤，第一個是「最舊」，第二個是「上一頁」，第三個是「下一頁」，第四個是「最新」
            paging_div = soup.find('div', class_='btn-group-paging')
            if paging_div:
                next_page_button = paging_div.find_all('a')[1] # 這是“上一頁”的按鈕，實際是更舊的文章
                if 'href' in next_page_button.attrs:
                    current_page_url = PTT_BASE_URL + next_page_button['href']
                else:
                    print("No more pages found (no 'next page' link).")
                    break
            else:
                print("未找到分頁按鈕，停止爬取。")
                break
    
    print(f"爬蟲完成，共收集到 {dialogues_collected} 條對話/文章片段，保存到 {OUTPUT_FILENAME}")
    print("請執行 1-2-data.py, 1-3-create_train_jsonl.py, 2-1-Tokenizer-BPE.py, 2-2-Tokenization-dataset.py, 3-Defining-the-Model.py, 5.mode-work.py, 6.run.py 進行後續的語言模型訓練與應用。")

if __name__ == "__main__":
    main()