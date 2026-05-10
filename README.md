# BallInsight - 足球智能检索系统

面向中文足球新闻的智能检索系统，覆盖信息检索（IR）全链路：数据采集 → 索引构建 → 查询理解 → 混合排序 → 检索评测 → 前端交互。

## 项目概览

BallInsight 以懂球帝足球新闻为语料，构建了一个完整的 IR 系统。核心特色是提出并实现了 **BM25 × TimeDecay × Sentiment** 混合排序模型，并通过 TF-IDF / BM25 / Ours 三模型对比实验验证其有效性。系统还集成了中文同义词扩展、拼写纠错、MMR 多样性重排、球员知识图谱、AI 摘要等扩展功能。

## 系统架构

```
数据采集层：懂球帝 API / HTML → 爬虫（requests + BeautifulSoup）→ MySQL
索引构建层：结巴分词 → Whoosh 倒排索引 + sklearn TF-IDF 向量化
查询理解层: 同义词扩展（300+映射）+Levenshtein拼写纠错
排序模型层: BM25 × 时间衰减 × 情感因子 → MMR多样性重排
检索评测层:  15 条人工标注 Query (0/1/2) → P@10 + NDCG@10
交互展示层:  React 前端 → 搜索结果 / 知识图谱 / AI 摘要 / A/B 对比
```

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.12 + FastAPI + uvicorn |
| **数据库** | MySQL 8.0 + SQLAlchemy ORM |
| **搜索引擎** | Whoosh + jieba ChineseAnalyzer |
| **向量模型** | sklearn TfidfVectorizer |
| **NLP** | jieba (分词) + SnowNLP (情感分析) |
| **AI** | 智谱 GLM-4-Flash |
| **前端** | React 19 + Vite 8 + Tailwind CSS 3 |
| **可视化** | ECharts 5 (雷达图/知识图谱/柱状图) |
| **爬虫** | requests + BeautifulSoup |

## 项目结构

```
BallInsight/
├── backend/               # FastAPI 后端
│ ├── main.py # API 入口（搜索/实体/AI/拼写纠错/分析）
│   ├── search_engine.py   # 检索引擎 (BM25/TF-IDF/MMR/评测指标)
│   ├── config.py          # 配置 (数据库/AI/CORS)
│   ├── database.py        # SQLAlchemy 数据库连接
│   ├── llm_service.py     # 智谱 AI 调用服务
│ └── index_dir/ # Whoosh 索引（可重建）
├── frontend/              # React 前端
│   └── src/
│       ├── App.jsx        # 应用入口
│       ├── LandingPage.jsx     # 首页
│       ├── SearchResults.jsx   # 搜索结果页
│       ├── SearchHeader.jsx    # 搜索栏 + 情感过滤器
│       ├── ABTestPanel.jsx     # 三模型 A/B 对比面板
│       ├── EntityPanel.jsx     # 球员/球队实体面板
│       ├── NewsCard.jsx        # 新闻卡片
│       ├── HoloSlice.jsx       # 全息时刻展示
│       ├── ArticleModal.jsx    # 全文阅读弹窗
│       └── api.js              # 后端 API 封装
├── data_pipeline/         # 数据管线
│   ├── spider.py          # API 爬虫
│ ├── clean_spider.py # HTML 爬虫（5个频道）
│   ├── id_spider.py       # ID 遍历爬虫
│   ├── build_index.py     # Whoosh 索引重建
│   ├── import_players.py  # 球员数据导入
│   ├── import_synonyms.py # 同义词导入
│   ├── search_test.py     # 搜索测试脚本
│   └── sql/schema.sql     # 数据库建表 SQL
├── data/                  # 静态数据
│   ├── male_players.csv           # EA FC 25 球员数据
│ └── football_synonyms.json # 中文足球同义词（75条）
└── docs/                  # 文档
    └── BallInsight演示稿.docx     # 课程答辩演示方案
```

## 核心功能

### 1. 混合排序模型

```
最终得分 = BM25 × e^(-0.05 × 天数差) × 情感因子
```

-**BM25：概率检索模型基础评分（k1=1.2, b=0.75）
- **时间衰减**：负指数衰减，半衰期约 14 天，确保新闻时效性
-**情感因子：SnowNLP极性分析，正向放大、负向抑制
-支持MMR（最大边际相关性）多样性重排（λ=0.7）

### 2. 三模型对比评测

- **基线1**：TF-IDF + 余弦相似度（向量空间模型）
- **基线2**：纯BM25（概率检索模型）
- **我们的方法**：BM25 × 时间衰减 × 情感（混合模型）
-15条人工标注Query，0/1/2三级相关性打分
- 评测指标：P@10、NDCG@10
-前端 A/B 测试面板：三栏结果对比 + 柱状图可视化

### 3. 查询理解

- **同义词扩展**：三层映射体系（JSON 75 条 + 数据库 137 条 + 硬编码 200+ 条），理解球迷黑话（如「车子」→「切尔西」、「总裁」→「Cristiano Ronaldo」）
- **拼写纠错**：Levenshtein 编辑距离 + 足球专用词典，返回 Top-5 候选

### 4. 实体知识图谱

- **球员面板**：头像、OVR 总评、位置、六维雷达图（速度/射门/传球/盘带/防守/身体）
- **知识图谱**：ECharts 力导向图，展示球员 → 球队 → 国家 → 队友关系
- 数据来源：EA FC 25 球员数据集（16,000+ 球员）

###5. 人工智能摘要与球探报告

- 调用智谱 GLM-4-Flash，生成 50-80 字新闻综述（解说员语气）
- 基于球员雷达数据生成约 150 字专业球探报告

### 6. 情感分析 & 过滤

- SnowNLP 自动计算新闻情感极性（0-1）
- 前端支持 ALL / HYPE（积极）/ WARN（消极）三种模式切换
- 情感分析作为分面搜索（Faceted Search）的元数据维度

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+

### 1. 数据库初始化

```bash
mysql -u root -p < data_pipeline/sql/schema.sql
```

### 2. 数据准备

```bash
# 导入球员数据
python data_pipeline/import_players.py

# 导入同义词
python data_pipeline/import_synonyms.py

# 爬取新闻数据 (可选，使用已有抽样数据即可)
python data_pipeline/clean_spider.py

# 构建 Whoosh 索引
python data_pipeline/build_index.py
```

### 3. 后端启动

```bash
CD 后端
pip install -r requirements.txt

# 设置环境变量
export BI_DB_USER=root
export BI_DB_PASS=your_password
export BI_ZHIPU_API_KEY=your_zhipu_api_key  # 可选，用于 AI 功能

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 前端启动

```bash
cd 前端
npm install
npm run dev
```

访问 `http://localhost:5173` 即可使用。

##API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/search` |GET|主搜索（支持q/情感/偏移量/限制）|
| `/api/search/compare` |GET|三模型对比搜索（支持mmr参数）|
| `/api/entity/{name}` | GET | 球员/球队实体查询 |
| `/api/ai/summary` | POST | AI 新闻综述生成 |
| `/api/ai/bio` | POST | AI 球探报告生成 |
| `/api/spell/check` | GET | 拼写纠错 |
| `/api/analytics` | GET | 查询统计分析 |
| `/api/players/all` | GET | 全部球员列表 |

## 评测数据集

15 条人工标注查询覆盖以下类型：

- 球员名查询（C罗、梅西、姆巴佩）
- 球队名查询（皇马、曼联）
- 昵称查询（总裁、魔人布欧）
- 事件查询（世界杯、欧冠决赛）
- 拼写错误查询（罗纳而多）
- 零相关查询（用于测试 sentinel 处理）

## 课程信息

- **课程**：信息服务与信息检索
- **版本**：BallInsight v2
- **优化总结**：详见 `docs/` 目录

##许可证

MIT
