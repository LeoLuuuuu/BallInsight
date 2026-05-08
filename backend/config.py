import os

# ── Database ──
DB_HOST = os.getenv("BI_DB_HOST", "localhost")
DB_PORT = os.getenv("BI_DB_PORT", "3306")
DB_USER = os.getenv("BI_DB_USER", "root")
DB_PASS = os.getenv("BI_DB_PASS", "")
DB_NAME = os.getenv("BI_DB_NAME", "ballinsight")
DB_CHARSET = "utf8mb4"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}"

# ── AI / LLM ──
ZHIPU_API_KEY = os.getenv("BI_ZHIPU_API_KEY", "")
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
ZHIPU_MODEL = "glm-4-flash"
AI_CACHE_SIZE = 128
AI_REQUEST_TIMEOUT = 10

# ── CORS ──
CORS_ORIGINS = os.getenv("BI_CORS_ORIGINS", "http://localhost:5173").split(",")

# ── Search index ──
INDEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index_dir")

# ── Server ──
API_HOST = os.getenv("BI_API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("BI_API_PORT", "8000"))
