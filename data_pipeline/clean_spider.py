import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
from urllib.parse import urljoin
from datetime import datetime

# 💡 扩大战果：不再只盯着首页，加入各大联赛频道的入口
TARGET_URLS = [
    "https://www.dongqiudi.com/",  # 首页推荐
    "https://www.dongqiudi.com/articles/channel/3",  # 英超
    "https://www.dongqiudi.com/articles/channel/5",  # 西甲
    "https://www.dongqiudi.com/articles/channel/6",  # 欧冠
    "https://www.dongqiudi.com/articles/channel/4"  # 意甲
]

BASE_URL = "https://www.dongqiudi.com"
OUTPUT_FILE = "clean_football_news.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.dongqiudi.com/"
}


def load_existing_data():
    """读取本地已有的数据，用于去重"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📂 发现本地历史档案：已存在 {len(data)} 条新闻。")
                return data
        except Exception as e:
            print(f"⚠️ 读取历史数据失败，将作为全新爬取。原因: {e}")
    return []


def fetch_links_from_html(existing_urls):
    """从多个频道抓取链接，并剔除已经爬过的"""
    print("🚀 启动多频道雷达：开始大范围扫荡链接...")
    news_links = []

    # 建立一个 Set 集合，把历史 URL 放进去。查找速度 O(1)，极其高效！
    seen_urls = set(existing_urls)

    for target_url in TARGET_URLS:
        print(f"  > 正在扫描频道: {target_url}")
        try:
            res = requests.get(target_url, headers=HEADERS, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')

            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                title = a_tag.get_text(strip=True)

                if ('/articles/' in href or '/news/' in href) and len(title) > 8:
                    url = urljoin(BASE_URL, href)

                    # 💡 核心去重逻辑：只有当这个 URL 不在历史库里，才加进新任务名单
                    if url not in seen_urls:
                        seen_urls.add(url)
                        news_links.append({
                            "title": title,
                            "url": url,
                            "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
            time.sleep(1)  # 频道之间稍微停顿一下
        except Exception as e:
            print(f"  ❌ 扫描频道 {target_url} 失败: {e}")

    print(f"✅ 频道扫描完毕，共发现 {len(news_links)} 条【全新】的新闻链接待清洗！")
    return news_links


def extract_clean_content(url):
    """清洗正文"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        body = soup.find('div', class_='con') or soup.find('div', class_='detail') or soup.find('article')
        if not body: return ""

        for tag in body(['script', 'style', 'iframe', 'div', 'a']):
            if tag.name in ['script', 'style', 'iframe']:
                tag.decompose()

        paragraphs = body.find_all('p')
        clean_text = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 0])

        if not clean_text:
            clean_text = body.get_text(separator=' ', strip=True)
        return clean_text

    except Exception:
        return ""


def main():
    print("====== 启动增量式足球情报爬虫 ======")

    # 1. 加载历史数据，提取历史 URL 列表
    existing_data = load_existing_data()
    existing_urls = [item['url'] for item in existing_data]

    # 2. 带着历史名单去扫荡新链接
    new_links = fetch_links_from_html(existing_urls)

    if not new_links:
        print("🎉 当前全网没有产生新资讯，无需更新！")
        return

    clean_new_dataset = []

    # 3. 深入清洗新链接
    for idx, item in enumerate(new_links):
        print(f"[{idx + 1}/{len(new_links)}] 正在清洗新情报: {item['title'][:20]}...")

        content = extract_clean_content(item['url'])

        if content and len(content) > 80:
            item['content'] = content
            clean_new_dataset.append(item)

        time.sleep(random.uniform(1.0, 2.5))

    # 4. 新旧合并，覆写存档
    final_dataset = existing_data + clean_new_dataset

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 大功告成！本次新增了 {len(clean_new_dataset)} 条情报。目前总库中共有 {len(final_dataset)} 条高质量新闻！")
    print("💡 提示：数据量已扩大，请重新运行 update_data.py 把它们同步进 MySQL 和 Whoosh！")


if __name__ == "__main__":
    main()