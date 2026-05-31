"""分享服务 —— 分析结果持久化与短链接生成。"""

import json
import secrets
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "shares.db"


def _ensure_db():
    """确保数据库文件和表存在。"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS shares (
            id             TEXT PRIMARY KEY,
            girl_name      TEXT,
            user_name      TEXT,
            overall_score  INTEGER,
            dimensions     TEXT,
            summary        TEXT,
            suggestion     TEXT,
            search_results TEXT,
            created_at     TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    return conn


def _generate_id() -> str:
    """生成 6 位短码。"""
    while True:
        raw = secrets.token_urlsafe(4)
        short = raw.replace("-", "").replace("_", "")[:6]
        if len(short) == 6:
            return short


def save(data: dict) -> str:
    """保存分享数据，返回短 ID。"""
    conn = _ensure_db()
    share_id = _generate_id()
    conn.execute(
        """INSERT INTO shares
           (id, girl_name, user_name, overall_score, dimensions, summary, suggestion, search_results)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            share_id,
            data.get("girl_name", ""),
            data.get("user_name", ""),
            data.get("overall_score", 0),
            json.dumps(data.get("dimensions", []), ensure_ascii=False),
            data.get("summary", ""),
            data.get("suggestion", ""),
            json.dumps(data.get("search_results", []), ensure_ascii=False),
        ),
    )
    conn.commit()
    conn.close()
    return share_id


def get(share_id: str) -> dict | None:
    """根据短 ID 获取分享数据，不存在返回 None。"""
    conn = _ensure_db()
    row = conn.execute(
        "SELECT * FROM shares WHERE id = ?", (share_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "id": row[0],
        "girl_name": row[1],
        "user_name": row[2],
        "overall_score": row[3],
        "dimensions": json.loads(row[4]),
        "summary": row[5],
        "suggestion": row[6],
        "search_results": json.loads(row[7]) if row[7] else [],
    }
