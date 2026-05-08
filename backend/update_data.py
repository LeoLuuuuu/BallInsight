import json
import os
import shutil

from snownlp import SnowNLP
from sqlalchemy import create_engine, text
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from jieba.analyse import ChineseAnalyzer

from config import DATABASE_URL, INDEX_DIR

JSON_FILE_PATH = "../data_pipeline/clean_football_news.json"


def update_pipeline():
    print("====== 启动后端数据更新管道 ======")

    # 1. 加载 JSON
    try:
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
            news_data = json.load(f)
        print(f"读取 JSON 成功，共 {len(news_data)} 条新闻。")
    except Exception as e:
        print(f"读取 JSON 失败: {e}")
        return

    # 2. 同步 MySQL
    print("\n同步 MySQL 数据库...")
    engine = create_engine(DATABASE_URL)
    try:
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE sys_news"))
            for idx, item in enumerate(news_data, start=1):
                conn.execute(
                    text("INSERT INTO sys_news (id, title, publish_time, content) "
                         "VALUES (:id, :title, :publish_time, :content)"),
                    {
                        "id": idx,
                        "title": item["title"],
                        "publish_time": item["publish_time"],
                        "content": item["content"][:5000],
                    },
                )
        print("sys_news 表已更新。")
    except Exception as e:
        print(f"数据库写入失败: {e}")
        return

    # 3. 重建 Whoosh 索引（含情感打分）
    print("\n重建 Whoosh 倒排索引...")
    analyzer = ChineseAnalyzer()
    schema = Schema(
        news_id=ID(stored=True, unique=True),
        title=TEXT(stored=True, analyzer=analyzer),
        content=TEXT(stored=True, analyzer=analyzer),
        publish_time=ID(stored=True),
        sentiment_score=NUMERIC(stored=True),
    )

    if os.path.exists(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)
    os.mkdir(INDEX_DIR)

    ix = create_in(INDEX_DIR, schema)
    writer = ix.writer()
    count = 0

    try:
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT id, title, content, publish_time FROM sys_news"))
            for row in rows:
                content_text = row[2]
                try:
                    score = round(SnowNLP(content_text[:500]).sentiments * 100)
                except Exception:
                    score = 50

                writer.add_document(
                    news_id=str(row[0]),
                    title=row[1],
                    content=content_text,
                    publish_time=str(row[3]),
                    sentiment_score=score,
                )
                count += 1
                if count % 50 == 0:
                    print(f"  ...已完成 {count} 篇")

        writer.commit()
        print(f"索引重建完毕，共 {count} 篇文档。")
    except Exception as e:
        print(f"构建索引失败: {e}")

    print("\n全链路更新完成。")


if __name__ == "__main__":
    update_pipeline()
