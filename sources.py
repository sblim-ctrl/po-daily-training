"""뉴스 후보 수집: Hacker News, 네이버 뉴스, Open DART."""
import html
import re
from datetime import timedelta

import requests
import streamlit as st

import db

TIMEOUT = 10
MAX_CANDIDATES = 20
HN = "https://hacker-news.firebaseio.com/v0"


def clean(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def _get(url, **kw):
    r = requests.get(url, timeout=TIMEOUT, **kw)
    r.raise_for_status()
    return r.json()


def fetch_hn():
    out = []
    for item_id in _get(f"{HN}/topstories.json")[:15]:
        item = _get(f"{HN}/item/{item_id}.json") or {}
        if item.get("type") == "story" and item.get("url"):
            out.append({
                "title": item["title"],
                "desc": f"HN {item.get('score', 0)}점, 댓글 {item.get('descendants', 0)}개",
                "url": item["url"],
            })
    return out[:MAX_CANDIDATES]


def fetch_naver():
    data = _get(
        # 검색 API는 개발자센터에서 NAVER API HUB(NCP)로 이관됐다
        "https://naverapihub.apigw.ntruss.com/search/v1/news",
        headers={
            "X-NCP-APIGW-API-KEY-ID": st.secrets["NAVER_CLIENT_ID"],
            "X-NCP-APIGW-API-KEY": st.secrets["NAVER_CLIENT_SECRET"],
        },
        params={"query": "신규 기능 업데이트", "display": 20, "sort": "date"},
    )
    return [
        {"title": clean(i["title"]), "desc": clean(i["description"]), "url": i.get("originallink") or i["link"]}
        for i in data["items"]
    ][:MAX_CANDIDATES]


def fetch_dart():
    today = db.today_kst()
    data = _get(
        "https://opendart.fss.or.kr/api/list.json",
        params={
            "crtfc_key": st.secrets["DART_API_KEY"],
            "bgn_de": (today - timedelta(days=7)).strftime("%Y%m%d"),
            "end_de": today.strftime("%Y%m%d"),
            "pblntf_ty": "B",
            "page_count": 100,
        },
    )
    if data.get("status") != "000":  # "013"은 조회된 데이터 없음
        raise RuntimeError(f"DART {data.get('status')}: {data.get('message')}")
    return [
        {
            "title": f"[{d['corp_name']}] {d['report_nm']}",
            "desc": f"{d['flr_nm']} 제출, 접수일 {d['rcept_dt']}",
            "url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={d['rcept_no']}",
        }
        for d in data["list"]
    ][:MAX_CANDIDATES]


SLOTS = [
    (1, "AI·tech 서비스 출시", fetch_hn),
    (2, "국내외 서비스 기능 업데이트", fetch_naver),
    (3, "그로스·비즈니스 의사결정", fetch_dart),
]
