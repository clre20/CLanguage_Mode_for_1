import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urlparse, urljoin, parse_qs
import os

def bing_general_scrape(query, max_results):
    """
    使用 Bing 通用搜索抓取网页链接，包括论文、文章、书籍等。
    """
    urls = []
    T = 0
    headers = {
        # 使用一个更真实的User-Agent，模拟浏览器请求
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    # Bing 通用搜索的基础 URL
    base_bing_url = "https://www.bing.com/search"

    # 定义一些您希望排除的域名，例如搜索引擎内部链接、社交媒体、视频网站等
    # 您可以根据需要修改此列表，添加或移除域名
    excluded_domains = [
        "bing.com",         # Bing 自己的域名
        "microsoft.com",    # 微软相关域名
        "google.com",       # Google 域名 (以防 Bing 结果中出现)
        "facebook.com", "twitter.com", "instagram.com", "linkedin.com", "reddit.com", "pinterest.com", # 社交媒体
        "amazon.com", "taobao.com", "jd.com", # 电商网站
        "youtube.com"       # 视频网站
    ]

    # 为了更好的过滤效果，可以添加一些常见的学术/文章平台域名，如果它们不希望被抓取
    # 例如：["arxiv.org", "sciencedirect.com", "researchgate.net", "academia.edu", "jstor.org"]
    # 如果您想抓取这些网站，就不要把它们加入 excluded_domains

    for start_index in range(0, max_results, 10): # Bing 搜索结果通常每页显示 10 条
        T += 1
        print(f"第{T}次收尋 (Bing)")
        
        # 构建 Bing 通用搜索的 URL 参数
        params = {
            "q": query,         # 查询关键字
            "first": start_index # 结果的起始索引，用于分页
        }
        
        # 构建完整的请求 URL
        # requests.Request().prepare().url 是一种可靠的构建带参数 URL 的方式
        response_url_obj = requests.Request('GET', base_bing_url, headers=headers, params=params).prepare()
        final_url = response_url_obj.url
        
        print(f"query:{query} | start:{start_index}")
        print(f"请求URL: {final_url}")

        try:
            # 发送 HTTP GET 请求，并设置超时，避免长时间等待
            response = requests.get(final_url, headers=headers, timeout=15)
            response.raise_for_status() # 如果 HTTP 状态码不是 200 (成功)，则抛出异常
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            print("等待更长时间后重试当前页...")
            time.sleep(random.uniform(10, 30)) # 请求失败时等待更长时间再重试当前页
            continue # 跳过当前循环的剩余部分，进入下一次循环
        
        # 使用 BeautifulSoup 解析页面内容
        soup = BeautifulSoup(response.text, "html.parser")
        
        found_links_on_page = 0
        
        # --- 针对 Bing 通用搜索结果的 HTML 结构进行解析 ---
        # Bing 的主要搜索结果通常位于 <li class="b_algo"> 元素中
        # 在每个 <li class="b_algo"> 内部，新闻/文章的标题链接通常是 <h2/h3> 标签下的 <a> 标签
        
        # 查找所有 class 为 "b_algo" 的列表项，这些通常是主要搜索结果
        result_items = soup.find_all("li", class_="b_algo")

        for item in result_items:
            # 在每个结果项中，尝试找到标题链接 (通常在 h2 或 h3 标签下)
            a_tag = None
            if item.find("h2"):
                a_tag = item.find("h2").find("a")
            elif item.find("h3"): # 有些结果可能是 h3
                a_tag = item.find("h3").find("a")
            
            if a_tag:
                href = a_tag.get("href")
                
                if href:
                    # Bing 的链接通常是绝对路径，但为了健壮性，使用 urljoin 处理可能的相对路径
                    full_url = urljoin(base_bing_url, href)

                    # 过滤掉不需要的域名
                    is_excluded_domain = False
                    parsed_full_url_domain = urlparse(full_url).netloc # 获取链接的域名部分
                    for domain in excluded_domains:
                        # 检查链接的域名是否包含在排除列表中
                        if domain in parsed_full_url_domain:
                            is_excluded_domain = True
                            break
                    
                    if full_url.startswith("http") and not is_excluded_domain:
                        # 只有当链接以 http/https 开头且不在排除域名列表中时才添加
                        urls.append(full_url)
                        print(f"提取到通用搜索URL: {full_url}")
                        found_links_on_page += 1
                    else:
                        print(f"过滤掉链接 (内部/排除域名): {full_url}")
                else:
                    print(f"警告: 找到无href属性的<a>标签在结果项中: {a_tag.prettify()}")
            else:
                print(f"警告: 未能在结果项中找到标题链接: {item.text[:100]}...") # 打印部分文本以便调试


        if found_links_on_page == 0:
            print("警告: 未能在当前页面找到任何外部通用链接。请检查 Bing 的 HTML 结构是否已改变。")
        
        print(f"当前已找到 {len(urls)} 条唯一URL。")
        print("等待...")
        # 每次请求之间随机等待一段时间，模拟人类行为，降低被检测为爬虫的风险
        time.sleep(random.uniform(5, 15)) 

    return list(set(urls))  # 返回去重后的链接列表

# --- 主题設定（可修改）和执行部分 ---
# 确保 'data' 目录存在，如果不存在则创建
os.makedirs("data", exist_ok=True)

# 定义您想要搜索的查询词
# 尝试使用更具体的查询词来获得论文、文章、书籍等结果
query = "歷史 文章" # 例如："數學 論文", "歷史 文章", "物理 學術期刊", "AI 書籍"
max_results = 30  # 您希望抓取的总结果数量上限 (实际抓取页数取决于此值和每页结果数)

print("開始!")
# 调用 Bing 通用搜索函数来抓取数据
urls = bing_general_scrape(query, max_results)

# 儲存抓取到的链接到 JSON 文件
with open("data/urls.json", "w", encoding="utf-8") as f:
    json.dump(urls, f, indent=2, ensure_ascii=False)

print(f"成功儲存 {len(urls)} 筆資料到 data/urls.json")