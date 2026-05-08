import requests
from bs4 import BeautifulSoup
from snownlp import SnowNLP
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, text
import time
import random

# ================= 1. 数据库配置 =================
DB_URI = "mysql+pymysql://root:@localhost:3306/ballinsight?charset=utf8mb4"
engine = create_engine(DB_URI)


# ================= 2. 进阶采集引擎 (支持翻页与重试) =================
def fetch_dongqiudi_news(target_count=3000):
    """
    通过懂球帝 API 获取历史新闻。
    懂球帝的翻页通常依赖 'after' 参数（时间戳）或者 'page' 参数。
    这里为了稳定，我们采用多次请求并结合日期范围来抓取。
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.dongqiudi.com/'
    }

    # 我们采用抓取多个不同频道（tabs）和不断往下翻页的策略
    # tab 1: 头条, tab 2: 深度, tab 3: 英超, tab 4: 西甲, tab 5: 意甲
    tabs = [1, 2, 3, 4, 5]

    total_saved = 0
    consecutive_failures = 0

    print(f"🚀 开始 BallInsight 大规模数据采集任务，目标：{target_count} 条...")

    for tab in tabs:
        # 针对每个频道，我们尝试抓取前 20 页（每页通常 20-30 条）
        for page in range(1, 21):

            if total_saved >= target_count:
                print("\n✅ 达到目标抓取数量，任务圆满结束！")
                return

            api_url = f"https://www.dongqiudi.com/api/app/tabs/web/{tab}.json?page={page}"

            try:
                print(f"\n📡 正在抓取 频道 {tab} - 第 {page} 页...")
                response = requests.get(api_url, headers=headers, timeout=10)

                # 检查请求是否成功
                if response.status_code != 200:
                    print(f"⚠️ 频道 {tab} 第 {page} 页请求失败，状态码: {response.status_code}。暂停...")
                    time.sleep(5)
                    continue

                data = response.json()
                articles = data.get('articles', [])

                if not articles:
                    print(f"⚠️ 频道 {tab} 已无更多数据。")
                    break  # 跳出当前频道的翻页循环

                news_list = process_articles(articles, headers)

                if news_list:
                    save_to_mysql(news_list)
                    total_saved += len(news_list)
                    consecutive_failures = 0
                    print(f"📊 当前进度: {total_saved} / {target_count}")

                # 随机休眠 2-4 秒，极其重要，防止被封 IP
                sleep_time = random.uniform(2, 4)
                time.sleep(sleep_time)

            except Exception as e:
                consecutive_failures += 1
                print(f"❌ 抓取异常: {e}")
                if consecutive_failures > 5:
                    print("🛑 连续失败次数过多，可能被限制访问，建议更换网络或休息一会。退出程序。")
                    return
                time.sleep(5)


def process_articles(articles, headers):
    """处理 API 返回的文章列表，提取正文和情感分"""
    news_list = []
    for article in articles:
        if article.get('is_video') or not article.get('share_title'):
            continue

        title = article.get('share_title')
        detail_url = article.get('share')
        publish_time = article.get('published_at')

        # 检查是否已经存在于数据库 (简单去重，避免重复请求详情页)
        # 实际生产中可以查库比对，这里依靠 MySQL 的 IGNORE 和唯一 ID 兜底
        news_id = hashlib.md5(detail_url.encode('utf-8')).hexdigest()

        content = fetch_detail_content(detail_url, headers)
        if not content or len(content) < 50:
            continue

        try:
            s = SnowNLP(content)
            sentiment_score = round(s.sentiments, 4)
        except Exception:
            sentiment_score = 0.5

        news_data = {
            "id": news_id,
            "title": title,
            "content": content,
            "publish_time": publish_time,
            "source": "懂球帝",
            "sentiment_score": sentiment_score
        }
        news_list.append(news_data)

    return news_list


def fetch_detail_content(url, headers):
    """抓取正文 (与之前相同)"""
    try:
        # 详情页随机休眠 0.5-1 秒
        time.sleep(random.uniform(0.5, 1))
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = "\n".join([p.text.strip() for p in paragraphs if len(p.text.strip()) > 5])
        return content
    except:
        return ""


# ================= 3. 数据入库 (支持批量插入去重) =================
def save_to_mysql(news_list):
    if not news_list:
        return

    insert_query = text("""
                        INSERT
                        IGNORE INTO sys_news 
        (id, title, content, publish_time, source, sentiment_score) 
        VALUES (:id, :title, :content, :publish_time, :source, :sentiment_score)
                        """)

    try:
        with engine.begin() as conn:
            # 批量执行
            conn.execute(insert_query, news_list)
        print(f"✅ 成功将 {len(news_list)} 条新数据写入数据库！")
    except Exception as e:
        print(f"❌ 批量入库失败: {e}")


# ================= 4. 执行入口 =================
if __name__ == "__main__":
    # 设置目标抓取数量为 1500 条 (可根据需要调整)
    fetch_dongqiudi_news(target_count=1500)