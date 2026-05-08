import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
from datetime import datetime

# ================= ⚙️ 核心配置区 =================
START_ID = 5803000
END_ID = 5803999
OUTPUT_FILE = "clean_football_news.json"
SAVE_INTERVAL = 50  # 每抓取50条自动保存一次，防止程序崩溃数据丢失

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.dongqiudi.com/"
}


# =================================================

def load_existing_data():
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []


def extract_article(url):
    """进入详情页，同时提取标题、时间和正文"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)

        # 遇到 404 (页面不存在) 直接返回空，不报错
        if res.status_code != 200:
            return None

        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # 1. 抓取标题 (直接找 h1 标签)
        title_tag = soup.find('h1')
        if not title_tag:
            return None
        title = title_tag.get_text(strip=True)

        # 2. 抓取时间 (如果找不到就用当前时间)
        pub_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_tag = soup.find('span', class_='time')
        if time_tag:
            pub_time = time_tag.get_text(strip=True)

        # 3. 抓取并清洗正文
        body = soup.find('div', class_='con') or soup.find('div', class_='detail') or soup.find('article')
        if not body:
            return None

        for tag in body(['script', 'style', 'iframe', 'div', 'a']):
            if tag.name in ['script', 'style', 'iframe']:
                tag.decompose()

        paragraphs = body.find_all('p')
        clean_text = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 0])

        if not clean_text:
            clean_text = body.get_text(separator=' ', strip=True)

        # 组装返回
        if len(clean_text) > 80:  # 只保留高质量长文
            return {
                "title": title,
                "url": url,
                "publish_time": pub_time,
                "content": clean_text
            }
        return None

    except Exception as e:
        # 屏蔽超时等网络错误，保持程序继续运行
        return None


def main():
    print(f"====== 🚀 启动重装坦克爬虫：目标 ID {START_ID} -> {END_ID} ======")

    dataset = load_existing_data()
    existing_urls = {item['url'] for item in dataset}
    print(f"📂 本地已有 {len(dataset)} 条记录。")

    success_count = 0
    total_tasks = END_ID - START_ID + 1

    for i, current_id in enumerate(range(START_ID, END_ID + 1)):
        url = f"https://www.dongqiudi.com/articles/{current_id}.html"

        if url in existing_urls:
            print(f"[{i + 1}/{total_tasks}] ⏩ 跳过已存在: {url}")
            continue

        print(f"[{i + 1}/{total_tasks}] 📡 正在破解尝试: {url}", end="")

        article_data = extract_article(url)

        if article_data:
            dataset.append(article_data)
            existing_urls.add(url)
            success_count += 1
            print(f"  -> ✅ 成功捕获: {article_data['title'][:15]}...")
        else:
            print("  -> ❌ 页面失效或无高价值正文")

        # 💾 定期存档机制 (每 50 条保存一次)
        if success_count > 0 and success_count % SAVE_INTERVAL == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, ensure_ascii=False, indent=2)
            print(f"  [系统提示] 💾 已自动触发存档，当前总库容量: {len(dataset)}")

        # ⚠️ 反爬休眠 (极其重要！不要删掉！)
        time.sleep(random.uniform(0.5, 1.5))

    # 最终保存
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 扫荡行动结束！本次新增 {success_count} 条纯净战报，弹药库总计 {len(dataset)} 条！")
    print("💡 提示：快去运行 update_data.py 更新你的数据库和倒排索引吧！")


if __name__ == "__main__":
    main()