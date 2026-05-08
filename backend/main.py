import time
from typing import Optional, List

from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from config import DATABASE_URL, CORS_ORIGINS
from search_engine import search_news, compare_search_news, log_query
from database import get_db, engine as db_engine
from llm_service import generate_search_summary, generate_player_bio

app = FastAPI(title="BallInsight API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Entity fallback dict ────────────────────────────────────────
ENTITY_EN_FALLBACK = {
    # ── 球员 Players ──────────────────────────────────────────────
    "梅西": "Lionel Messi", "老板": "Lionel Messi", "煤老板": "Lionel Messi", "梅老八": "Lionel Messi", "梅球王": "Lionel Messi", "小跳蚤": "Lionel Messi",
    "C罗": "Cristiano Ronaldo", "总裁": "Cristiano Ronaldo", "罗哥": "Cristiano Ronaldo", "小小罗": "Cristiano Ronaldo", "CR7": "Cristiano Ronaldo",
    "内马尔": "Neymar Jr", "马儿": "Neymar Jr", "内少": "Neymar Jr",
    "姆巴佩": "Kylian Mbappé", "神龟": "Kylian Mbappé", "总监": "Kylian Mbappé", "姆总": "Kylian Mbappé", "忍者神龟": "Kylian Mbappé",
    "哈兰德": "Erling Haaland", "魔人布欧": "Erling Haaland", "吃人": "Erling Haaland", "哈宝": "Erling Haaland", "魔人": "Erling Haaland",
    "莱万": "Robert Lewandowski", "莱万多夫斯基": "Robert Lewandowski", "世一锋": "Robert Lewandowski", "豆腐": "Robert Lewandowski",
    "德布劳内": "Kevin De Bruyne", "丁丁": "Kevin De Bruyne", "做饼师傅": "Kevin De Bruyne",
    "贝林厄姆": "Jude Bellingham", "贝林": "Jude Bellingham", "贝皇": "Jude Bellingham",
    "维尼修斯": "Vinícius Jr.", "小熊": "Vinícius Jr.", "熊皇": "Vinícius Jr.",
    "萨拉赫": "Mohamed Salah", "法老": "Mohamed Salah",
    "凯恩": "Harry Kane", "哈里凯恩": "Harry Kane",
    "孙兴慜": "Heung Min Son", "孙哥": "Heung Min Son",
    "亚马尔": "Lamine Yamal",
    "佩德里": "Pedri",
    "加维": "Gavi",
    "福登": "Phil Foden", "太子": "Phil Foden",
    "萨卡": "Bukayo Saka",
    "厄德高": "Martin Ødegaard",
    "罗德里": "Rodri",
    "穆西亚拉": "Jamal Musiala", "斑比": "Jamal Musiala",
    "维尔茨": "Florian Wirtz",
    "范迪克": "Virgil van Dijk",
    "阿利松": "Alisson",
    "库尔图瓦": "Thibaut Courtois", "裤袜": "Thibaut Courtois",
    "诺伊尔": "Manuel Neuer", "小新": "Manuel Neuer",
    "格列兹曼": "Antoine Griezmann", "格子": "Antoine Griezmann",
    "劳塔罗": "Lautaro Martínez", "塔罗": "Lautaro Martínez",
    "阿尔瓦雷斯": "Julián Álvarez", "小蜘蛛": "Julián Álvarez",
    "莱奥": "Rafael Leão",
    "奥斯梅恩": "Victor Osimhen",
    "克瓦拉茨赫利亚": "Khvicha Kvaratskhelia",
    "巴尔韦德": "Federico Valverde",
    "赖斯": "Declan Rice",
    "阿诺德": "Trent Alexander-Arnold",
    "吕迪格": "Antonio Rüdiger",
    "阿劳霍": "Ronald Araujo",
    "巴斯托尼": "Alessandro Bastoni",
    "麦卡利斯特": "Alexis Mac Allister",
    "恩佐": "Enzo Fernández",
    "苏亚雷斯": "Luis Suárez", "苏神": "Luis Suárez", "咬人苏": "Luis Suárez", "苏牙": "Luis Suárez",
    "莫德里奇": "Luka Modrić", "魔笛": "Luka Modrić",
    "克罗斯": "Toni Kroos", "托尼老师": "Toni Kroos", "阿宽": "Toni Kroos",
    "本泽马": "Karim Benzema", "锅锋": "Karim Benzema", "背锅侠": "Karim Benzema",
    "拉莫斯": "Sergio Ramos", "水爷": "Sergio Ramos",
    "马奎尔": "Harry Maguire", "航母": "Harry Maguire", "马大头": "Harry Maguire",
    "安东尼": "Antony", "圆规": "Antony",
    "斯特林": "Raheem Sterling", "快乐男孩": "Raheem Sterling",
    "阿扎尔": "Eden Hazard", "汉堡王": "Eden Hazard",
    "布冯": "Gianluigi Buffon", "小将": "Gianluigi Buffon",
    "伊布": "Zlatan Ibrahimović", "上帝": "Zlatan Ibrahimović", "奉先": "Zlatan Ibrahimović",
    "罗本": "Arjen Robben",
    "里贝里": "Franck Ribéry",
    "皮尔洛": "Andrea Pirlo",
    "卡卡": "Kaká",
    "贝克汉姆": "David Beckham", "小贝": "David Beckham",
    "齐达内": "Zinedine Zidane", "齐祖": "Zinedine Zidane",
    "巴洛特利": "Mario Balotelli", "巴神": "Mario Balotelli",
    "博格巴": "Paul Pogba", "波霸": "Paul Pogba",
    "迪马利亚": "Ángel Di María", "天使": "Ángel Di María",
    "菲尔米诺": "Roberto Firmino", "费米": "Roberto Firmino",
    "范佩西": "Robin van Persie",
    "德罗巴": "Didier Drogba", "魔兽": "Didier Drogba",
    "托雷斯": "Fernando Torres",
    "哈维": "Xavi Hernández",
    "伊涅斯塔": "Andrés Iniesta", "小白": "Andrés Iniesta",
    "布斯克茨": "Sergio Busquets", "布教授": "Sergio Busquets",
    "皮克": "Gerard Piqué",
    "普约尔": "Carles Puyol",
    "马斯切拉诺": "Javier Mascherano",
    "迪巴拉": "Paulo Dybala", "小魔仙": "Paulo Dybala",
    "坎特": "N'Golo Kanté",
    "若日尼奥": "Jorginho",
    "蒂亚戈席尔瓦": "Thiago Silva",
    "内斯塔": "Alessandro Nesta",
    "马尔蒂尼": "Paolo Maldini",
    "卡纳瓦罗": "Fabio Cannavaro",
    "罗纳尔迪尼奥": "Ronaldinho", "小罗": "Ronaldinho",
    "罗纳尔多": "Ronaldo Nazário", "大罗": "Ronaldo Nazário", "外星人": "Ronaldo Nazário",
    # 门将
    "多纳鲁马": "Gianluigi Donnarumma", "钱多多": "Gianluigi Donnarumma",
    "奥布拉克": "Jan Oblak",
    "特尔施特根": "Marc-André ter Stegen", "特狮": "Marc-André ter Stegen",
    "埃德森": "Ederson",
    "马丁内斯": "Emiliano Martínez", "大马丁": "Emiliano Martínez",
    "德赫亚": "David de Gea",
    # ── 教练 Coaches ─────────────────────────────────────────────
    "瓜迪奥拉": "Pep Guardiola", "瓜帅": "Pep Guardiola",
    "克洛普": "Jürgen Klopp", "渣叔": "Jürgen Klopp",
    "穆里尼奥": "José Mourinho", "魔力鸟": "José Mourinho", "鸟叔": "José Mourinho",
    "安切洛蒂": "Carlo Ancelotti", "安胖": "Carlo Ancelotti",
    "滕哈赫": "Erik ten Hag", "滕嗨": "Erik ten Hag",
    "阿尔特塔": "Mikel Arteta", "塔帅": "Mikel Arteta",
    "阿隆索": "Xabi Alonso",
    # ── 球队 Teams ────────────────────────────────────────────────
    "曼联": "Manchester United", "红魔": "Manchester United",
    "曼城": "Manchester City", "蓝月亮": "Manchester City",
    "阿森纳": "Arsenal", "兵工厂": "Arsenal", "枪手": "Arsenal",
    "车子": "Chelsea", "切尔西": "Chelsea", "蓝军": "Chelsea",
    "利物浦": "Liverpool", "红军": "Liverpool",
    "热刺": "Tottenham Hotspur", "托特纳姆热刺": "Tottenham Hotspur",
    "维拉": "Aston Villa", "阿斯顿维拉": "Aston Villa",
    "纽卡": "Newcastle United", "纽卡斯尔": "Newcastle United",
    "皇马": "Real Madrid", "皇家马德里": "Real Madrid", "银河战舰": "Real Madrid",
    "巴萨": "FC Barcelona", "巴塞罗那": "FC Barcelona", "红蓝军团": "FC Barcelona",
    "马竞": "Atlético de Madrid", "马德里竞技": "Atlético de Madrid", "床单军团": "Atlético de Madrid",
    "尤文": "Juventus", "尤文图斯": "Juventus", "老妇人": "Juventus",
    "米兰": "Milan", "AC米兰": "Milan", "红黑军团": "Milan",
    "国米": "Inter", "国际米兰": "Inter", "蓝黑军团": "Inter",
    "那不勒斯": "Napoli", "拿波里": "Napoli",
    "拜仁": "FC Bayern München", "拜仁慕尼黑": "FC Bayern München",
    "多特": "Borussia Dortmund", "多特蒙德": "Borussia Dortmund", "大黄蜂": "Borussia Dortmund",
    "勒沃库森": "Bayer 04 Leverkusen", "药厂": "Bayer 04 Leverkusen",
    "巴黎": "Paris SG", "大巴黎": "Paris SG", "巴黎圣日耳曼": "Paris SG",
    "迈阿密国际": "Inter Miami CF",
    "利雅得胜利": "Al Nassr",
    "利雅得新月": "Al Hilal",
    "马赛": "Olympique de Marseille",
    "摩纳哥": "AS Monaco",
    "罗马": "AS Roma", "红狼": "AS Roma",
    "拉齐奥": "Lazio", "蓝鹰": "Lazio",
    "塞维利亚": "Sevilla",
    "瓦伦西亚": "Valencia", "蝙蝠军团": "Valencia",
    "比利亚雷亚尔": "Villarreal", "黄潜": "Villarreal",
    "皇家社会": "Real Sociedad",
    "毕尔巴鄂竞技": "Athletic Club",
    "本菲卡": "Benfica",
    "波尔图": "FC Porto",
    "葡萄牙体育": "Sporting CP",
    "阿贾克斯": "Ajax",
    "埃因霍温": "PSV Eindhoven",
    "费耶诺德": "Feyenoord",
    "凯尔特人": "Celtic",
    "格拉斯哥流浪者": "Rangers",
    "加拉塔萨雷": "Galatasaray",
    "费内巴切": "Fenerbahçe",
    "埃弗顿": "Everton",
    "西汉姆联": "West Ham United", "铁锤帮": "West Ham United",
    "莱斯特城": "Leicester City", "蓝狐": "Leicester City",
    "狼队": "Wolverhampton Wanderers",
    "水晶宫": "Crystal Palace",
    "布莱顿": "Brighton & Hove Albion", "海鸥": "Brighton & Hove Albion",
    "伯恩茅斯": "AFC Bournemouth",
    "富勒姆": "Fulham",
    "布伦特福德": "Brentford",
    "诺丁汉森林": "Nottingham Forest",
    "伯恩利": "Burnley",
    "南安普顿": "Southampton", "圣徒": "Southampton",
    "利兹联": "Leeds United",
    # ── 国家队 National Teams ─────────────────────────────────────
    "阿根廷": "Argentina", "潘帕斯雄鹰": "Argentina",
    "巴西": "Brazil", "桑巴军团": "Brazil",
    "法国": "France", "高卢雄鸡": "France",
    "英格兰": "England", "三狮军团": "England",
    "西班牙": "Spain", "斗牛士军团": "Spain",
    "德国": "Germany", "日耳曼战车": "Germany",
    "意大利": "Italy", "蓝衣军团": "Italy",
    "荷兰": "Netherlands", "橙衣军团": "Netherlands",
    "葡萄牙": "Portugal",
    "比利时": "Belgium",
    "克罗地亚": "Croatia", "格子军团": "Croatia",
    "日本": "Japan", "蓝武士": "Japan",
    "韩国": "South Korea", "太极虎": "South Korea",
    # ── 联赛/赛事 ─────────────────────────────────────────────────
    "英超": "Premier League", "英格兰足球超级联赛": "Premier League",
    "西甲": "La Liga", "西班牙足球甲级联赛": "La Liga",
    "意甲": "Serie A", "意大利足球甲级联赛": "Serie A",
    "德甲": "Bundesliga", "德国足球甲级联赛": "Bundesliga",
    "法甲": "Ligue 1", "法国足球甲级联赛": "Ligue 1",
    "欧冠": "UEFA Champions League", "欧洲冠军联赛": "UEFA Champions League",
    "欧联杯": "UEFA Europa League",
    "世界杯": "FIFA World Cup",
    "欧洲杯": "UEFA European Championship",
    "美洲杯": "Copa América",
}


def _resolve_search_query(q: str, db: Session) -> str:
    """Look up query in sys_synonym table only (for search endpoints)."""
    if not q.strip():
        return q
    row = db.execute(text("SELECT standard FROM sys_synonym WHERE keyword = :kw"), {"kw": q}).fetchone()
    return row[0] if row else q


def _resolve_entity_name(name: str, db: Session) -> str:
    """Look up entity name in synonym table, then fallback dict (for entity endpoint)."""
    if not name.strip():
        return name
    row = db.execute(text("SELECT standard FROM sys_synonym WHERE keyword = :kw"), {"kw": name}).fetchone()
    if row:
        return row[0]
    return ENTITY_EN_FALLBACK.get(name, name)


# ── Search ──────────────────────────────────────────────────────

@app.get("/api/search")
def api_search(
    q: str = Query(""),
    sentiment: str = Query("all"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    t0 = time.time()
    actual_keyword = _resolve_search_query(q, db)
    results = search_news(keyword=actual_keyword, sentiment_filter=sentiment, limit=50)
    total = len(results)
    paged = results[offset:offset + limit]
    elapsed = round((time.time() - t0) * 1000, 1)
    log_query(q.strip() or "(全库)", total, elapsed)
    return {
        "status": "success",
        "query": {"original": q, "mapped": actual_keyword},
        "results": paged,
        "total": total,
        "offset": offset,
        "limit": limit,
        "query_time_ms": elapsed,
    }


@app.get("/api/search/compare")
def api_search_compare(
    q: str = Query(""),
    sentiment: str = Query("all"),
    mmr: bool = Query(False),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    t0 = time.time()
    actual_keyword = _resolve_search_query(q, db)
    metric_keyword = f"{q} {actual_keyword}" if q.strip() and actual_keyword != q else actual_keyword
    comparison = compare_search_news(
        keyword=actual_keyword,
        sentiment_filter=sentiment,
        limit=50,
        metric_keyword=metric_keyword,
    )
    ours_results = comparison["ours"]
    if mmr and len(ours_results) > 1:
        from search_engine import mmr_rerank
        ours_results = mmr_rerank(ours_results, top_k=50, lambda_param=0.7)

    elapsed = round((time.time() - t0) * 1000, 1)
    log_query(q.strip() or "(全库)", len(ours_results), elapsed)
    return {
        "status": "success",
        "query": {"original": q, "mapped": actual_keyword, "mmr_enabled": mmr},
        "results": ours_results[offset:offset + limit],
        "baseline_results": comparison["baseline"][offset:offset + limit],
        "tfidf_results": comparison["tfidf"][offset:offset + limit],
        "metrics": comparison["metrics"],
        "total": len(ours_results),
        "offset": offset,
        "limit": limit,
        "query_time_ms": elapsed,
    }


# ── Entity ──────────────────────────────────────────────────────

@app.get("/api/entity/{entity_name}")
def api_get_entity(entity_name: str, db: Session = Depends(get_db)):
    search_name = _resolve_entity_name(entity_name, db)

    # 1) try player table
    player = db.execute(
        text("SELECT p.*, t.team_name FROM sys_player p "
             "LEFT JOIN sys_team t ON p.team_id = t.id "
             "WHERE p.name LIKE :name LIMIT 1"),
        {"name": f"%{search_name}%"},
    ).mappings().fetchone()

    if player:
        p = dict(player)
        team_name = p.get("team_name", "未知球队")
        nation = p.get("nation", "未知国籍")
        nodes = [
            {"id": p["name"], "name": p["name"], "category": 0, "symbolSize": 45},
            {"id": team_name, "name": team_name, "category": 1, "symbolSize": 30},
            {"id": nation, "name": nation, "category": 2, "symbolSize": 25},
        ]
        links = [
            {"source": p["name"], "target": team_name},
            {"source": p["name"], "target": nation},
        ]
        if p.get("team_id"):
            teammates = db.execute(
                text("SELECT name FROM sys_player WHERE team_id = :tid AND id != :pid ORDER BY ovr DESC LIMIT 3"),
                {"tid": p["team_id"], "pid": p["id"]},
            ).fetchall()
            for tm in teammates:
                nodes.append({"id": tm[0], "name": tm[0], "category": 3, "symbolSize": 20})
                links.append({"source": tm[0], "target": team_name})
        p["graph_data"] = {"nodes": nodes, "links": links}
        return {"status": "success", "type": "player", "data": p}

    # 2) try team table
    team = db.execute(
        text("SELECT * FROM sys_team WHERE team_name LIKE :name LIMIT 1"),
        {"name": f"%{search_name}%"},
    ).mappings().fetchone()

    if team:
        t = dict(team)
        league = t.get("league", "未知联赛")
        nodes = [
            {"id": t["team_name"], "name": t["team_name"], "category": 0, "symbolSize": 45},
            {"id": league, "name": league, "category": 1, "symbolSize": 30},
        ]
        links = [{"source": t["team_name"], "target": league}]
        players = db.execute(
            text("SELECT name FROM sys_player WHERE team_id = :tid ORDER BY ovr DESC LIMIT 4"),
            {"tid": t["id"]},
        ).fetchall()
        for pl in players:
            nodes.append({"id": pl[0], "name": pl[0], "category": 3, "symbolSize": 25})
            links.append({"source": pl[0], "target": t["team_name"]})
        t["graph_data"] = {"nodes": nodes, "links": links}
        return {"status": "success", "type": "team", "data": t}

    return {"status": "error", "msg": "未找到相关实体档案"}


# ── AI endpoints ────────────────────────────────────────────────

class SummaryRequest(BaseModel):
    keyword: str
    results: list


@app.post("/api/ai/summary")
def api_ai_summary(req: SummaryRequest):
    return {"ai_summary": generate_search_summary(req.keyword, req.results)}


class BioRequest(BaseModel):
    player_data: dict


@app.post("/api/ai/bio")
def api_ai_bio(req: BioRequest):
    return {"ai_bio": generate_player_bio(req.player_data)}


# ── Spell check / query suggestion ───────────────────────────────

_SPELL_TERMS: Optional[List[str]] = None


def _get_spell_terms(db: Session) -> list[str]:
    global _SPELL_TERMS
    if _SPELL_TERMS is not None:
        return _SPELL_TERMS
    terms: set[str] = set()
    # Player names
    for row in db.execute(text("SELECT name FROM sys_player")).fetchall():
        terms.add(row[0])
    # Team names
    for row in db.execute(text("SELECT team_name FROM sys_team")).fetchall():
        terms.add(row[0])
    # Synonyms
    for row in db.execute(text("SELECT keyword, standard FROM sys_synonym")).fetchall():
        terms.add(row[0])
        terms.add(row[1])
    # Fallback dictionary
    for k, v in ENTITY_EN_FALLBACK.items():
        terms.add(k)
        terms.add(v)
    # Common football terms
    terms.update({"欧冠", "英超", "西甲", "意甲", "德甲", "法甲", "世界杯", "欧洲杯",
                   "帽子戏法", "倒钩", "绝杀", "转会", "红牌", "黄牌", "点球", "任意球",
                   "越位", "乌龙球", "金球奖", "金靴奖", "助攻", "进球", "战报", "首发"})
    _SPELL_TERMS = sorted(terms, key=len, reverse=True)
    return _SPELL_TERMS


def _levenshtein(a: str, b: str) -> int:
    """Edit distance between two strings."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1),
            )
    return dp[m][n]


@app.get("/api/spell/check")
def api_spell_check(q: str = Query(""), db: Session = Depends(get_db)):
    """Return spelling suggestions for queries that return few or no results."""
    if not q.strip():
        return {"status": "success", "suggestions": []}

    terms = _get_spell_terms(db)
    suggestions: list[dict] = []

    for term in terms:
        # Fast length pre-filter: skip if lengths differ too much
        if abs(len(q) - len(term)) > 3 or abs(len(q) - len(term)) > max(len(q), len(term)) // 2:
            continue
        dist = _levenshtein(q, term)
        max_len = max(len(q), len(term))
        if max_len > 0 and dist <= min(3, max_len // 2):
            similarity = 1 - dist / max_len
            suggestions.append({"term": term, "similarity": round(similarity, 3)})

    suggestions.sort(key=lambda x: (-x["similarity"], len(x["term"])))
    return {
        "status": "success",
        "query": q,
        "suggestions": suggestions[:5],
    }


# ── Analytics ───────────────────────────────────────────────────

@app.get("/api/analytics")
def api_analytics():
    from search_engine import get_query_stats
    return {"status": "success", "stats": get_query_stats()}


# ── Players list ────────────────────────────────────────────────

@app.get("/api/players/all")
def get_all_players(limit: int = 100):
    try:
        with db_engine.connect() as conn:
            rows = conn.execute(
                text("SELECT p.*, t.team_name FROM sys_player p "
                     "JOIN sys_team t ON p.team_id = t.id "
                     "ORDER BY p.ovr DESC LIMIT :limit"),
                {"limit": limit},
            )
            players = [dict(row._mapping) for row in rows]
        return {"status": "success", "data": players}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
