import os
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser

# 指向你刚刚建好的索引文件夹
INDEX_DIR = "news_index"


def test_search(keyword):
    print(f"🔍 正在系统大脑中检索关键词: 【{keyword}】...")

    # 1. 确保索引文件夹存在
    if not os.path.exists(INDEX_DIR):
        print("❌ 找不到 news_index 文件夹，请确认路径是否正确！")
        return

    # 2. 打开倒排索引库
    ix = open_dir(INDEX_DIR)

    # 3. 创建查询解析器 (同时在 title 和 content 两个字段里搜)
    # MultifieldParser 允许我们一次性搜多个字段
    qp = MultifieldParser(["title", "content"], schema=ix.schema)
    q = qp.parse(keyword)

    # 4. 执行搜索 (使用 with 语句确保搜索完毕后安全关闭资源)
    with ix.searcher() as searcher:
        # 搜索并返回前 5 条最相关的结果
        results = searcher.search(q, limit=5)

        if len(results) == 0:
            print(f"😭 未找到与“{keyword}”相关的新闻。")
            return

        print(f"✅ 共找到 {len(results)} 条极度相关的结果 (按 BM25 相关度得分排序):\n")
        print("=" * 60)

        for i, hit in enumerate(results):
            # 获取基本信息
            title = hit.get('title', '无标题')
            pub_time = hit.get('publish_time', '未知时间')
            score = hit.get('sentiment_score', '未知情感')

            print(f"[{i + 1}] 🏆 {title}")
            print(f"    ⏱️ 发布时间: {pub_time} | 🎭 情感极性(0-100): {score}")

            # 🔥 杀手锏：自动提取包含关键词的上下文摘要，并加上 HTML 高亮标签！
            snippet = hit.highlights("content")
            # 如果 Whoosh 没提取出摘要，就截取正文前 50 个字
            if not snippet:
                snippet = hit.get('content', '')[:50] + "..."

            print(f"    📝 智能摘要: {snippet}")
            print("-" * 60)


if __name__ == "__main__":
    # 💡 在这里输入你想测试的球星、球队或随便一个你在数据库里看到过的词！
    # 比如：梅西、曼联、绝杀、冠军
    test_search("梅西")