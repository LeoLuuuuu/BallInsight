import os
import sys
from sqlalchemy import create_engine, text
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, DATETIME, NUMERIC
from jieba.analyse import ChineseAnalyzer
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from config import DATABASE_URL, INDEX_DIR

engine = create_engine(DATABASE_URL, echo=False)


# ==========================================
# 2. 定义 Whoosh 的 Schema (索引结构)
# ==========================================
def create_whoosh_schema():
    analyzer = ChineseAnalyzer()
    schema = Schema(
        news_id=ID(unique=True, stored=True),
        title=TEXT(stored=True, analyzer=analyzer),
        content=TEXT(stored=True, analyzer=analyzer),
        publish_time=DATETIME(stored=True, sortable=True),
        # 💡 核心修复 1：改为 int 类型，彻底避开浮点数排序的底层 Bug
        sentiment_score=NUMERIC(int, stored=True, sortable=True),
        source=ID(stored=True)
    )
    return schema


# ==========================================
# 3. 从 MySQL 提取数据并构建索引
# ==========================================
def build_index():
    print("🚀 开始构建 BallInsight 全文检索倒排索引...")

    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)

    if not exists_in(INDEX_DIR):
        schema = create_whoosh_schema()
        ix = create_in(INDEX_DIR, schema)
        print("📁 创建了全新的索引目录。")
    else:
        ix = open_dir(INDEX_DIR)
        print("📁 找到了已存在的索引目录。")

    writer = ix.writer()
    print("📡 正在从数据库抽取新闻数据...")
    fetch_query = text("SELECT id, title, content, publish_time, source, sentiment_score FROM sys_news")

    try:
        with engine.connect() as conn:
            result = conn.execute(fetch_query)
            rows = result.fetchall()

            total_docs = len(rows)
            print(f"📦 共查找到 {total_docs} 条新闻，准备分词并建立索引...")

            count = 0
            for row in rows:
                news_id, title, content, publish_time, source, sentiment_score = row

                # --- 时间处理 ---
                if isinstance(publish_time, str):
                    try:
                        publish_time_obj = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        publish_time_obj = datetime.now()
                else:
                    publish_time_obj = publish_time

                title = str(title) if title else ""
                content = str(content) if content else ""

                # 💡 核心修复 2：将浮点数转换为 0-100 的百分制整数
                if sentiment_score is not None:
                    # 比如 0.8543 -> 85.43 -> 85
                    score_int = int(float(sentiment_score) * 100)
                else:
                    score_int = 50  # 默认中立给 50 分

                # 写入倒排索引
                writer.update_document(
                    news_id=str(news_id),
                    title=title,
                    content=content,
                    publish_time=publish_time_obj,
                    sentiment_score=score_int,  # 传入转化后的整数
                    source=str(source) if source else "未知"
                )

                count += 1
                if count % 200 == 0:
                    print(f"⏳ 已处理 {count} / {total_docs} 条...")

        print("💾 正在将倒排索引写入磁盘并进行优化 (这可能需要几秒钟)...")
        writer.commit()
        print("✅ 倒排索引构建成功！系统的核心大脑已装填完毕！")

    except Exception as e:
        print(f"❌ 构建索引时发生错误: {e}")
        writer.cancel()


if __name__ == "__main__":
    build_index()