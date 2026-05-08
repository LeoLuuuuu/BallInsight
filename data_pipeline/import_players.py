import requests
from bs4 import BeautifulSoup
from snownlp import SnowNLP
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import time
import random

# ==========================================
# 1. 数据库与采集核心配置
# ==========================================
# ⚠️ 注意：请将 123456 替换为你真实的数据库密码
DB_URI = "mysql+pymysql://root:@localhost:3306/ballinsight?charset=utf8mb4"
engine = create_engine(DB_URI, echo=False)

TARGET_COUNT = 1000  # 目标采集数量
TIME_LIMIT_DAYS = 90  # 时间围栏：只抓取近 90 天的新闻
MAX_PAGES_PER_TAB = 300  # 防止单个频道无限下钻的极限页数

# 垂直语料过滤器核心词库
CORE_KEYWORDS = [
    "梅西", "C罗", "姆巴佩", "哈兰德", "贝林厄姆", "维尼修斯", "德布劳内", "亚马尔",
    "曼城", "皇马", "巴萨", "拜仁", "阿森纳", "利物浦", "曼联", "切尔西", "尤文", "米兰", "国米"
]


def is_relevant(title, content):
    """【拦截器】判断新闻是否包含核心球星或豪门"""
    combined_text = str(title) + str(content)
    for keyword in CORE_KEYWORDS:
        if keyword in combined_text:
            return True
    return False


# ==========================================
# 2. 定向采集引擎 (主逻辑)
# ==========================================
def fetch_focused_news():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.dongqiudi.com/'
    }

    # 懂球帝频道列表: 1:头条, 3:英超, 4:西甲, 5:意甲, 6:德甲
    tabs = [1, 3, 4, 5, 6]
    total_saved = 0
    cutoff_date = datetime.now() - timedelta(days=TIME_LIMIT_DAYS)

    print("=" * 60)
    print(f"🚀 启动 BallInsight 严谨版定向采集引擎")
    print(f"🎯 目标：{TARGET_COUNT} 条 | 时间跨度：近 {TIME_LIMIT_DAYS} 天")
    print(f"🛡️ 开启精确去重与防死循环机制...")
    print("=" * 60)

    for tab in tabs:
        # 获取第一页的初始 URL
        api_url = f"https://www.dongqiudi.com/api/app/tabs/web/{tab}.json"

        for page in range(1, MAX_PAGES_PER_TAB + 1):
            if total_saved >= TARGET_COUNT:
                print("\n🎉 恭喜！已达到目标抓取数量，大规模语料采集圆满结束！")
                return

            try:
                print(f"\n📡 [频道 {tab}] 正在请求第 {page} 页数据...")
                response = requests.get(api_url, headers=headers, timeout=10)

                if response.status_code != 200:
                    print(f"⚠️ 请求异常，状态码: {response.status_code}。暂停 5 秒后重试...")
                    time.sleep(5)
                    continue

                data = response.json()
                articles = data.get('articles', [])

                if not articles:
                    print(f"ℹ️ 频道 {tab} 数据已触底。")
                    break

                # ---- 核心提取与清洗 ----
                news_list, should_stop_tab = process_and_filter_articles(articles, headers, cutoff_date)

                if news_list:
                    # 传入数据库进行批量插入，并获取绝对真实的增量
                    actual_inserted = save_to_mysql(news_list)
                    total_saved += actual_inserted
                    print(f"📊 当前数据库真实进度: {total_saved} / {TARGET_COUNT}")

                    # 【防死循环 / 无缝断点】如果本页抓取了相关新闻，但数据库实际新增为 0，说明遇到已爬取过的老数据
                    if actual_inserted == 0 and len(news_list) > 0:
                        print(f"⚠️ 发现本页数据已全部存在于数据库中，为避免重复劳动，自动切换下一频道...")
                        break

                # ---- 时间越界判定 ----
                if should_stop_tab:
                    print(f"⏰ 频道 {tab} 已触及 {TIME_LIMIT_DAYS} 天前的时间边界，停止该频道抓取。")
                    break

                # ---- 获取真实的下一页游标 ----
                next_url = data.get('next')
                if not next_url:
                    print(f"ℹ️ 频道 {tab} 没有下一页游标了。")
                    break
                api_url = next_url

                # 礼貌休眠，防封 IP
                time.sleep(random.uniform(2.0, 3.5))

            except requests.exceptions.RequestException as e:
                print(f"❌ 网络请求异常: {e}，休息一会...")
                time.sleep(5)
            except Exception as e:
                print(f"❌ 发生未知错误: {e}")
                time.sleep(5)


# ==========================================
# 3. 数据清洗与情感分析
# ==========================================
def process_and_filter_articles(articles, headers, cutoff_date):
    news_list = []
    should_stop_tab = False

    for article in articles:
        # 抛弃视频新闻和不规范数据
        if article.get('is_video') or not article.get('share_title'):
            continue

        title = article.get('share_title')
        detail_url = article.get('share')
        publish_time_str = article.get('published_at')

        # --- 时间校验 ---
        if publish_time_str:
            try:
                pub_time = datetime.strptime(publish_time_str, '%Y-%m-%d %H:%M:%S')
                if pub_time < cutoff_date:
                    should_stop_tab = True  # 发现时间越界，标记停止
                    continue
            except Exception:
                pass

                # --- 标题预检 (提升效率，如果标题没有核心词，才去查正文) ---
        if not is_relevant(title, ""):
            # 如果标题不相关，抓取正文后再检查一次
            content = fetch_detail_content(detail_url, headers)
            if not content or len(content) < 50 or not is_relevant("", content):
                continue
        else:
            # 如果标题已相关，直接抓取正文
            content = fetch_detail_content(detail_url, headers)
            if not content or len(content) < 50:
                continue

        # --- 唯一 ID 生成 ---
        news_id = hashlib.md5(detail_url.encode('utf-8')).hexdigest()

        # --- SnowNLP 情感极性分析 ---
        try:
            s = SnowNLP(content)
            sentiment_score = round(s.sentiments, 4)
        except Exception:
            sentiment_score = 0.5  # 容错：解析失败视为中立

        news_list.append({
            "id": news_id,
            "title": title,
            "content": content,
            "publish_time": publish_time_str,
            "source": "懂球帝",
            "sentiment_score": sentiment_score
        })

    return news_list, should_stop_tab


def fetch_detail_content(url, headers):
    """请求详情页提取纯文本正文"""
    try:
        # 正文抓取极易触发高频封禁，增加微小延迟
        time.sleep(random.uniform(0.5, 1.2))
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # 提取所有段落，并清洗过短的无意义段落
        paragraphs = soup.find_all('p')
        content = "\n".join([p.text.strip() for p in paragraphs if len(p.text.strip()) > 5])
        return content
    except Exception:
        return ""


# ==========================================
# 4. 严谨的数据持久化 (事务与真实验算)
# ==========================================
def save_to_mysql(news_list):
    if not news_list:
        return 0

    insert_query = text("""
                        INSERT
                        IGNORE INTO sys_news 
        (id, title, content, publish_time, source, sentiment_score) 
        VALUES (:id, :title, :content, :publish_time, :source, :sentiment_score)
                        """)

    try:
        # 使用 engine.begin() 开启自动事务提交/回滚
        with engine.begin() as conn:
            # 1. 插入前验算：查询当前表中总行数
            before_count = conn.execute(text("SELECT COUNT(*) FROM sys_news")).scalar()

            # 2. 执行批量写入（重复数据将被 MySQL 默默忽略）
            conn.execute(insert_query, news_list)

            # 3. 插入后验算：再次查询总行数
            after_count = conn.execute(text("SELECT COUNT(*) FROM sys_news")).scalar()

            # 4. 严谨计算真实增量
            inserted = after_count - before_count

        print(
            f"✅ 从本页解析出 {len(news_list)} 条相关新闻，实际存入 {inserted} 条新数据 (忽略重复 {len(news_list) - inserted} 条)")
        return inserted

    except Exception as e:
        print(f"❌ 批量入库发生严重错误: {e}")
        return 0


# ==========================================
# 5. 执行入口
# ==========================================
if __name__ == "__main__":
    fetch_focused_news()