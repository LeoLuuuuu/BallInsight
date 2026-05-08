from __future__ import annotations

import time
from functools import lru_cache

import requests

from config import ZHIPU_API_KEY, ZHIPU_API_URL, ZHIPU_MODEL, AI_REQUEST_TIMEOUT

HEADERS = {
    "Authorization": f"Bearer {ZHIPU_API_KEY}",
    "Content-Type": "application/json",
}

RETRY_DELAYS = [1, 2, 4]  # seconds, exponential back-off


def _call_zhipu(prompt: str, max_tokens: int = 200) -> str:
    """Call Zhipu API with retry on transient failures."""
    payload = {
        "model": ZHIPU_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }
    last_err = ""
    for attempt, delay in enumerate(RETRY_DELAYS):
        try:
            resp = requests.post(ZHIPU_API_URL, json=payload, headers=HEADERS, timeout=AI_REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.Timeout:
            last_err = "timeout"
        except requests.exceptions.HTTPError as e:
            last_err = f"HTTP {e.response.status_code if e.response else '?'}"
        except Exception as e:
            last_err = str(e)
        if attempt < len(RETRY_DELAYS) - 1:
            time.sleep(delay)
    return "[AI 服务暂时不可用，请稍后重试]"


def generate_search_summary(keyword: str, search_results: list) -> str:
    """Generate a concise news roundup from search results."""
    if not search_results:
        return "暂无相关资讯。"
    if not ZHIPU_API_KEY:
        return "[AI 摘要未配置 API Key]"

    context = "\n".join(
        f"- {res['title']}: {res['snippet']}" for res in search_results[:3]
    )
    prompt = (
        f"你是足球解说员。用户搜索了「{keyword}」，以下是相关新闻：\n"
        f"{context}\n\n"
        f"请用50-80字概括这些新闻的核心看点，直接输出正文，不要前缀。"
    )

    result = _call_zhipu(prompt, max_tokens=120)
    return result


def generate_player_bio(player_data: dict) -> str:
    """Generate a scout report for a player or club profile for a team."""
    if not ZHIPU_API_KEY:
        return "[AI 档案未配置 API Key]"

    entity_name = player_data.get("name") or player_data.get("team_name") or "Unknown"

    if "ovr" in player_data:
        prompt = (
            f"请根据以下数据为球员撰写一段150字左右的球探报告：\n"
            f"姓名：{entity_name}\n"
            f"球队：{player_data.get('team_name', '?')}\n"
            f"国籍：{player_data.get('nation', '?')}\n"
            f"位置：{player_data.get('position', '?')}\n"
            f"综合评分：{player_data.get('ovr', '?')}\n"
            f"速度{player_data.get('pac','?')} 射门{player_data.get('sho','?')} "
            f"传球{player_data.get('pas','?')} 盘带{player_data.get('dri','?')} "
            f"防守{player_data.get('def_attr','?')} 身体{player_data.get('phy','?')}\n"
            f"要求：语气专业，直接输出正文。"
        )
    else:
        prompt = (
            f"请根据以下数据为足球俱乐部撰写一段150字左右的深度分析：\n"
            f"队名：{entity_name}\n"
            f"联赛：{player_data.get('league', '?')}\n"
            f"主场：{player_data.get('stadium', '?')}\n"
            f"要求：结合历史底蕴或近期表现，语气专业，直接输出正文。"
        )

    return _call_zhipu(prompt, max_tokens=300)

