from __future__ import annotations

import json
import os
import re
import math
import hashlib
from datetime import datetime
from typing import Any

import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.query import Every

from config import INDEX_DIR


# ── Human relevance judgments ────────────────────────────────────

_JUDGMENTS_FILE = os.path.join(os.path.dirname(__file__), "relevance_judgments.json")
_HUMAN_JUDGMENTS: dict[str, dict[str, int]] = {}

def _load_judgments() -> dict[str, dict[str, int]]:
    if not os.path.exists(_JUDGMENTS_FILE):
        return {}
    with open(_JUDGMENTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("queries", {})


_HUMAN_JUDGMENTS = _load_judgments()


def _get_human_grade(keyword: str, news_id: str | None) -> int | None:
    """Return human relevance grade (0-2) or None if not labeled.

    Returns a special sentinel -1 when the query exists in human judgments
    but with an empty dict, meaning *all* documents are confirmed irrelevant.
    """
    if not news_id:
        return None
    if keyword in _HUMAN_JUDGMENTS:
        q_judgments = _HUMAN_JUDGMENTS[keyword]
        if isinstance(q_judgments, dict):
            if news_id in q_judgments:
                return q_judgments[news_id]
            if len(q_judgments) == 0:
                return -1  # query known, empty = all docs irrelevant
    return None


# ── Scoring factors ─────────────────────────────────────────────

def _parse_datetime(s: str | None) -> datetime | None:
    """Best-effort parse publish_time string."""
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def calculate_time_decay(publish_time_str: str | None) -> float:
    """Exponential decay: newer → close to 1, older → floor at 0.1."""
    pub = _parse_datetime(publish_time_str)
    if pub is None:
        return 0.5
    days = (datetime.now() - pub).days
    return max(math.exp(-0.05 * max(days, 0)), 0.1)


def calculate_sentiment_factor(score: Any, mode: str = "all") -> float:
    """Convert sentiment score (0-100) to a ranking weight.

    - positive mode: higher score → higher weight
    - negative mode: lower score → higher weight
    - all mode:      extreme scores → mild boost
    """
    try:
        s = float(score)
    except (TypeError, ValueError):
        s = 50.0
    s = max(0.0, min(100.0, s))

    if mode == "positive":
        return 0.6 + 0.8 * (s / 100.0)
    if mode == "negative":
        return 0.6 + 0.8 * ((100.0 - s) / 100.0)

    intensity = abs(s - 50.0) / 50.0
    return 1.0 + 0.2 * intensity


# ── Text helpers ────────────────────────────────────────────────

def _strip_html(text: str | None) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


def _tokenize(text: str) -> list[str]:
    """Chinese + English tokenisation, dedup'd in order."""
    parts = re.findall(r"[A-Za-z0-9]+|[一-鿿]+", text.lower())
    tokens: list[str] = []
    seen = set()
    for p in parts:
        if re.search(r"[一-鿿]", p):
            for t in jieba.lcut(p):
                t = t.strip().lower()
                if t and t not in seen:
                    tokens.append(t)
                    seen.add(t)
        else:
            p = p.strip().lower()
            if p and p not in seen:
                tokens.append(p)
                seen.add(p)
    return tokens


# ── Auto relevance (for evaluation metrics) ─────────────────────

def auto_relevance_grade(keyword: str, item: dict, sentiment_filter: str = "all") -> float:
    """Automatic relevance label (0-10) for computing P@K / NDCG@K.

    Weights text-matching more heavily than time/sentiment to reduce
    circularity with the ranking formula.
    """
    terms = _tokenize(keyword)
    if not terms:
        return 0.0

    title = _strip_html(item.get("title", "")).lower()
    content = _strip_html(item.get("full_content", "")[:1200]).lower()

    title_hits = sum(1 for t in terms if t in title)
    content_hits = sum(1 for t in terms if t in content)

    if title_hits == 0 and content_hits == 0:
        return 0.0

    # Text match: title hits are worth more than body hits
    score = min(title_hits, 3) * 2.5 + min(content_hits, 5) * 1.0

    # Mild freshness bonus (capped so it doesn't dominate text relevance)
    tf = float(item.get("time_factor", 0.5))
    score += tf * 1.0

    # Mild sentiment alignment bonus
    s = float(item.get("sentiment_score", 50))
    if sentiment_filter == "positive":
        score += max(0.0, (s - 50) / 50) * 1.0
    elif sentiment_filter == "negative":
        score += max(0.0, (50 - s) / 50) * 1.0
    else:
        score += abs(s - 50) / 50 * 0.5

    return round(min(score, 10.0), 2)


# ── IR metrics ──────────────────────────────────────────────────

def precision_at_k(ranked_items: list[dict], k: int = 10) -> float:
    top = ranked_items[:k]
    if not top:
        return 0.0
    return round(sum(1 for it in top if it.get("relevance_grade", 0) >= 2) / len(top), 4)


def _dcg(grades: list[float], k: int = 10) -> float:
    score = 0.0
    for i, g in enumerate(grades[:k]):
        score += (2 ** g - 1) / math.log2(i + 2)
    return score


def ndcg_at_k(ranked_items: list[dict], ideal_items: list[dict], k: int = 10) -> float:
    ranked_grades = [it.get("relevance_grade", 0) for it in ranked_items[:k]]
    ideal_grades = sorted(
        (it.get("relevance_grade", 0) for it in ideal_items), reverse=True
    )[:k]
    ideal = _dcg(ideal_grades, k)
    if ideal == 0:
        return 0.0
    return round(_dcg(ranked_grades, k) / ideal, 4)


# ── Candidate collection ────────────────────────────────────────

def collect_candidates(
    keyword: str,
    sentiment_filter: str = "all",
    candidate_limit: int = 50,
) -> list[dict]:
    if not os.path.exists(INDEX_DIR):
        raise FileNotFoundError(f"索引目录不存在: {INDEX_DIR}")

    ix = open_dir(INDEX_DIR)
    qp = MultifieldParser(["title", "content"], schema=ix.schema)

    q = Every() if not keyword.strip() else qp.parse(keyword)

    candidates: list[dict] = []
    with ix.searcher() as searcher:
        hits = searcher.search(q, limit=candidate_limit)
        for hit in hits:
            bm25 = float(hit.score)
            pub_time = hit.get("publish_time")
            sentiment = hit.get("sentiment_score", 50)

            tf = calculate_time_decay(pub_time)
            sf = calculate_sentiment_factor(sentiment, sentiment_filter)
            final = bm25 * tf * sf

            snippet = hit.highlights("content")
            if not snippet:
                snippet = (hit.get("content") or "")[:80] + "..."

            candidates.append({
                "news_id": hit.get("news_id"),
                "title": hit.get("title"),
                "publish_time": pub_time or "未知",
                "sentiment_score": sentiment,
                "snippet": snippet,
                "full_content": hit.get("content", ""),
                "bm25_score": round(bm25, 2),
                "time_factor": round(tf, 4),
                "sentiment_factor": round(sf, 4),
                "final_score": round(final, 2),
                "_bm25_raw": bm25,
                "_final_raw": final,
            })

    return candidates


def _public(items: list[dict], limit: int = 10) -> list[dict]:
    cleaned: list[dict] = []
    for it in items[:limit]:
        obj = dict(it)
        obj.pop("_bm25_raw", None)
        obj.pop("_final_raw", None)
        obj.pop("_tfidf_raw", None)
        obj.pop("_human_labeled", None)
        cleaned.append(obj)
    return cleaned


# ── TF-IDF Baseline ──────────────────────────────────────────────

_tfidf_index: dict | None = None  # {"vectorizer": TfidfVectorizer, "matrix": sparse, "doc_ids": list}


_TFIDF_CACHE_FILE = os.path.join(os.path.dirname(__file__), ".tfidf_cache.pkl")

def _build_tfidf_index() -> dict:
    global _tfidf_index
    if _tfidf_index is not None:
        return _tfidf_index

    # Try loading from disk cache
    if os.path.exists(_TFIDF_CACHE_FILE):
        try:
            import pickle
            with open(_TFIDF_CACHE_FILE, "rb") as f:
                _tfidf_index = pickle.load(f)
            return _tfidf_index
        except Exception:
            pass

    if not os.path.exists(INDEX_DIR):
        return {"vectorizer": TfidfVectorizer(), "matrix": None, "doc_ids": []}

    ix = open_dir(INDEX_DIR)
    doc_texts: list[str] = []
    doc_ids: list[str] = []
    with ix.searcher() as searcher:
        for hit in searcher.search(Every(), limit=None):
            title = hit.get("title") or ""
            content = hit.get("content") or ""
            doc_texts.append(f"{title} {content}")
            doc_ids.append(hit.get("news_id", ""))

    vectorizer = TfidfVectorizer(
        tokenizer=_tokenize_tfidf,
        max_df=0.85,
        min_df=1,
        ngram_range=(1, 2),
        max_features=8000,
    )
    matrix = vectorizer.fit_transform(doc_texts)
    _tfidf_index = {"vectorizer": vectorizer, "matrix": matrix, "doc_ids": doc_ids}

    # Persist to disk
    try:
        import pickle
        with open(_TFIDF_CACHE_FILE, "wb") as f:
            pickle.dump(_tfidf_index, f)
    except Exception:
        pass

    return _tfidf_index


def _tokenize_tfidf(text: str) -> list[str]:
    """Tokenizer adapter for TfidfVectorizer (must accept str, not bytes)."""
    return _tokenize(text)


def _tfidf_rank(keyword: str, candidate_ids: list[str]) -> dict[str, float]:
    """Compute TF-IDF cosine similarity scores. Returns {doc_id: score}."""
    idx = _build_tfidf_index()
    matrix = idx["matrix"]
    if matrix is None or matrix.shape[0] == 0:
        return {}

    vectorizer = idx["vectorizer"]
    doc_ids = idx["doc_ids"]
    query_vec = vectorizer.transform([keyword])
    scores = cosine_similarity(query_vec, matrix)[0]

    result: dict[str, float] = {}
    for i, did in enumerate(doc_ids):
        if did in candidate_ids and scores[i] > 0:
            result[did] = round(float(scores[i]), 4)
    return result


# ── MMR Diversity Re-ranking ────────────────────────────────────

def mmr_rerank(
    candidates: list[dict],
    top_k: int = 10,
    lambda_param: float = 0.7,
) -> list[dict]:
    """Maximal Marginal Relevance re-ranking for result diversity.

    Balances relevance (lambda) against content similarity (1 - lambda)
    to avoid showing duplicate/near-duplicate articles at the top.

    lambda=1.0 → pure relevance ranking; lambda=0.0 → pure diversity.
    """
    if not candidates or len(candidates) <= 1:
        return candidates

    # Use title + snippet as document representation
    docs = [
        _tokenize((c.get("title") or "") + " " + (c.get("snippet") or ""))
        for c in candidates
    ]

    def _jaccard_sim(doc_a: list[str], doc_b: list[str]) -> float:
        if not doc_a or not doc_b:
            return 0.0
        set_a, set_b = set(doc_a), set(doc_b)
        inter = len(set_a & set_b)
        union = len(set_a | set_b)
        return inter / union if union > 0 else 0.0

    remaining = list(range(len(candidates)))
    selected: list[int] = []

    # First pick: highest final_score
    first = max(remaining, key=lambda i: candidates[i].get("final_score", 0))
    selected.append(first)
    remaining.remove(first)

    for _ in range(min(top_k - 1, len(remaining))):
        best_idx = max(
            remaining,
            key=lambda i: lambda_param * candidates[i].get("final_score", 0)
            - (1 - lambda_param) * max(
                _jaccard_sim(docs[i], docs[j]) for j in selected
            ),
        )
        selected.append(best_idx)
        remaining.remove(best_idx)

    # Append remaining in original order
    selected.extend(remaining)
    return [candidates[i] for i in selected]


# ── Public API ──────────────────────────────────────────────────

def compare_search_news(
    keyword: str,
    sentiment_filter: str = "all",
    limit: int = 10,
    metric_keyword: str | None = None,
) -> dict:
    candidates = collect_candidates(keyword, sentiment_filter, candidate_limit=50)

    # Apply relevance grades — prefer human labels over auto-grading
    eval_kw = metric_keyword or keyword
    human_labeled = 0
    # Check if this query's human judgment set is explicitly empty
    # (= we know there are zero relevant docs, e.g. "C罗")
    query_empty_judgment = (
        eval_kw in _HUMAN_JUDGMENTS
        and isinstance(_HUMAN_JUDGMENTS[eval_kw], dict)
        and len(_HUMAN_JUDGMENTS[eval_kw]) == 0
    )
    for item in candidates:
        nid = item.get("news_id")
        human = _get_human_grade(eval_kw, nid)
        if human == -1 or (query_empty_judgment and human is None):
            # Confirmed irrelevant (either sentinel or query with empty judgment set)
            item["relevance_grade"] = 0.0
            item["_human_labeled"] = True
            human_labeled += 1
        elif human is not None and human >= 0:
            # Human grade 0-2 → remap to 0-10 scale for metric compatibility
            item["relevance_grade"] = human * 5.0
            item["_human_labeled"] = True
            human_labeled += 1
        else:
            item["relevance_grade"] = auto_relevance_grade(eval_kw, item, sentiment_filter)
            item["_human_labeled"] = False

    # BM25 baseline
    baseline_ranked = sorted(candidates, key=lambda x: x["_bm25_raw"], reverse=True)

    # Ours: BM25 × TimeDecay × Sentiment
    ours_ranked = sorted(candidates, key=lambda x: x["_final_raw"], reverse=True)

    # TF-IDF baseline
    candidate_ids = {c["news_id"] for c in candidates}
    tfidf_scores = _tfidf_rank(keyword, candidate_ids)
    for item in candidates:
        item["_tfidf_raw"] = tfidf_scores.get(item["news_id"], 0.0)
    tfidf_ranked = sorted(candidates, key=lambda x: x["_tfidf_raw"], reverse=True)

    return {
        "baseline": _public(baseline_ranked, limit),
        "ours": _public(ours_ranked, limit),
        "tfidf": _public(tfidf_ranked, limit),
        "metrics": {
            "baseline": {
                "p_at_10": precision_at_k(baseline_ranked, limit),
                "ndcg_at_10": ndcg_at_k(baseline_ranked, candidates, limit),
            },
            "ours": {
                "p_at_10": precision_at_k(ours_ranked, limit),
                "ndcg_at_10": ndcg_at_k(ours_ranked, candidates, limit),
            },
            "tfidf": {
                "p_at_10": precision_at_k(tfidf_ranked, limit),
                "ndcg_at_10": ndcg_at_k(tfidf_ranked, candidates, limit),
            },
            "human_labeled": human_labeled,
            "total_candidates": len(candidates),
            "grading": "human" if human_labeled > 0 else "auto",
        },
    }


def search_news(
    keyword: str,
    sentiment_filter: str = "all",
    limit: int = 10,
) -> list[dict]:
    return compare_search_news(keyword, sentiment_filter, limit)["ours"]


# ── Query logging ────────────────────────────────────────────────

_QUERY_LOG_FILE = os.path.join(os.path.dirname(__file__), ".query_log.json")
_query_log: list[dict] = []

def _load_query_log():
    global _query_log
    if os.path.exists(_QUERY_LOG_FILE):
        try:
            with open(_QUERY_LOG_FILE, "r", encoding="utf-8") as f:
                _query_log = json.load(f)
        except Exception:
            _query_log = []

def _save_query_log():
    try:
        with open(_QUERY_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(_query_log[-1000:], f, ensure_ascii=False)
    except Exception:
        pass

_load_query_log()


def log_query(keyword: str, results_count: int, query_time_ms: float):
    """Record a query for analytics (in-memory + persistent)."""
    _query_log.append({
        "keyword": keyword,
        "results_count": results_count,
        "query_time_ms": query_time_ms,
        "timestamp": datetime.now().isoformat(),
    })
    if len(_query_log) > 1000:
        _query_log[:] = _query_log[-1000:]
    _save_query_log()


def get_query_stats() -> dict:
    """Return summary statistics about logged queries."""
    if not _query_log:
        return {"total_queries": 0, "recent": []}

    from collections import Counter
    keywords = [q["keyword"] for q in _query_log if q["keyword"].strip()]
    keyword_counts = Counter(keywords)
    avg_time = sum(q["query_time_ms"] for q in _query_log) / len(_query_log)

    return {
        "total_queries": len(_query_log),
        "unique_queries": len(keyword_counts),
        "avg_time_ms": round(avg_time, 1),
        "top_queries": keyword_counts.most_common(10),
        "recent": _query_log[-10:][::-1],
    }
