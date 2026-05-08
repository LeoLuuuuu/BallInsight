import json
import os
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base

# ================= 1. 数据库连接 =================
DB_URI = "mysql+pymysql://root:@localhost:3306/ballinsight?charset=utf8mb4"
engine = create_engine(DB_URI, echo=False)
Base = declarative_base()


# ================= 2. 定义同义词表结构 =================
class Synonym(Base):
    __tablename__ = 'sys_synonym'
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(50), unique=True, nullable=False, comment="球迷黑话/简称")
    standard = Column(String(100), nullable=False, comment="标准实体名(球员名/球队名)")


# 初始化表结构 (如果不存在则创建)
Base.metadata.create_all(engine)


# ================= 3. 读取 JSON 并入库 =================
def load_synonyms_to_db(json_file_path):
    if not os.path.exists(json_file_path):
        print(f"❌ 找不到文件: {json_file_path}")
        return

    # 读取 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        synonyms_data = json.load(f)

    if not synonyms_data:
        print("⚠️ JSON文件为空。")
        return

    # 准备批量插入的 SQL (使用 IGNORE 防止重复导入报错)
    insert_query = text("""
                        INSERT
                        IGNORE INTO sys_synonym (keyword, standard) 
        VALUES (:keyword, :standard)
                        """)

    try:
        with engine.begin() as conn:
            # 插入前查总数
            before_count = conn.execute(text("SELECT COUNT(*) FROM sys_synonym")).scalar()

            # 批量执行
            conn.execute(insert_query, synonyms_data)

            # 插入后查总数
            after_count = conn.execute(text("SELECT COUNT(*) FROM sys_synonym")).scalar()

            inserted = after_count - before_count

        print(f"🎉 成功读取 {len(synonyms_data)} 个黑话映射！")
        print(f"✅ 实际新增入库 {inserted} 个 (忽略了 {len(synonyms_data) - inserted} 个已存在的重复项)。")
        print("🧠 系统的语义引擎大脑已充值完毕！")

    except Exception as e:
        print(f"❌ 导入失败: {e}")


if __name__ == "__main__":
    # 注意调整相对路径，指向你存放 JSON 的地方
    # 假设该脚本在 data_pipeline 下，JSON 在 data 下
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'football_synonyms.json')

    # 将路径规范化
    json_path = os.path.normpath(json_path)

    print(f"正在读取字典文件: {json_path}")
    load_synonyms_to_db(json_path)