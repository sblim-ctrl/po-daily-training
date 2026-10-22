"""Supabase 접근 함수. 예외는 삼키지 않고 호출한 화면이 처리한다."""
import hashlib
import hmac
from datetime import date, datetime
from zoneinfo import ZoneInfo

import streamlit as st
from supabase import create_client


@st.cache_resource
def _client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def _first(rows):
    return rows[0] if rows else None


def today_kst() -> date:
    return datetime.now(ZoneInfo("Asia/Seoul")).date()


def _hash(nickname, pin):
    # shortcut: 4자리 PIN + sha256은 약함, P1 카카오 로그인을 붙일 때 교체
    return hashlib.sha256(f"{nickname}:{pin}".encode()).hexdigest()


def login(nickname: str, pin: str) -> dict | None:
    users = _client().table("users")
    row = _first(users.select("id, nickname, pin_hash").eq("nickname", nickname).limit(1).execute().data)
    if row is None:
        row = users.insert({"nickname": nickname, "pin_hash": _hash(nickname, pin)}).execute().data[0]
    elif not hmac.compare_digest(row["pin_hash"], _hash(nickname, pin)):
        return None
    return {"id": row["id"], "nickname": row["nickname"]}


def replace_drafts(d: date, drafts: list[dict]) -> None:
    cases = _client().table("cases")
    cases.delete().eq("date", d.isoformat()).eq("status", "draft").execute()
    if drafts:
        cases.insert([{**x, "date": d.isoformat(), "status": "draft"} for x in drafts]).execute()


def cases_by_date(d: date, status: str | None = None) -> list[dict]:
    q = _client().table("cases").select("*").eq("date", d.isoformat())
    if status:
        q = q.eq("status", status)
    return q.order("slot").execute().data


def latest_published_date() -> date | None:
    row = _first(
        _client().table("cases").select("date").eq("status", "published")
        .order("date", desc=True).limit(1).execute().data
    )
    return date.fromisoformat(row["date"]) if row else None


def get_case(case_id: int) -> dict | None:
    return _first(_client().table("cases").select("*").eq("id", case_id).limit(1).execute().data)


def update_case(case_id: int, fields: dict) -> None:
    _client().table("cases").update(fields).eq("id", case_id).execute()


def publish_case(case_id: int) -> None:
    _client().table("cases").update({"status": "published"}).eq("id", case_id).execute()


def save_answer(user_id: int, case_id: int, body: str) -> dict:
    return _client().table("answers").insert(
        {"user_id": user_id, "case_id": case_id, "body": body}
    ).execute().data[0]


def set_feedback(answer_id: int, text: str) -> None:
    _client().table("answers").update({"feedback": text}).eq("id", answer_id).execute()


def set_rating(answer_id: int, rating: str) -> None:
    _client().table("answers").update({"rating": rating}).eq("id", answer_id).execute()


def my_answer(user_id: int, case_id: int) -> dict | None:
    return _first(
        _client().table("answers").select("*").eq("user_id", user_id).eq("case_id", case_id)
        .order("created_at", desc=True).limit(1).execute().data
    )


def my_answers(user_id: int) -> list[dict]:
    return (
        _client().table("answers").select("*, cases(*)").eq("user_id", user_id)
        .order("created_at", desc=True).execute().data
    )


def log_event(user_id: int, name: str, case_id: int | None = None) -> None:
    _client().table("events").insert({"user_id": user_id, "name": name, "case_id": case_id}).execute()
