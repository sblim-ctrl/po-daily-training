import json
from datetime import date

import pytest

import llm
import sources


def test_case_type_follows_weekday_rotation():
    assert llm.case_type_for(date(2026, 10, 19)) == "문제 정의"  # 월
    assert llm.case_type_for(date(2026, 10, 22)) == "개선안"     # 목
    assert llm.case_type_for(date(2026, 10, 23)) == "역기획"     # 금
    assert llm.case_type_for(date(2026, 10, 24)) == "문제 정의"  # 토
    assert llm.case_type_for(date(2026, 10, 25)) == "지표 설계"  # 일


def test_case_type_differs_per_slot():
    thu = date(2026, 10, 22)
    assert [llm.case_type_for(thu, s) for s in (1, 2, 3)] == ["개선안", "역기획", "문제 정의"]
    fri = date(2026, 10, 23)
    assert [llm.case_type_for(fri, s) for s in (1, 2, 3)] == ["역기획", "문제 정의", "지표 설계"]


def test_clean_strips_tags_and_entities():
    assert sources.clean("<b>카카오</b> &quot;신기능&quot; 출시") == '카카오 "신기능" 출시'


def _case(**over):
    base = {"pick": 1, "headline": "h", "summary": "s", "question": "q", "rubric": ["a", "b"]}
    return json.dumps({**base, **over})


def test_parse_case_returns_bulleted_rubric():
    r = llm.parse_case(_case(), 3)
    assert r["pick"] == 1 and r["rubric"] == "- a\n- b"


@pytest.mark.parametrize("text", [
    "not json",
    json.dumps({"pick": 0, "headline": "h"}),   # 키 누락
    _case(pick=3),                               # 범위 밖
    _case(pick=-1),
    _case(pick="1"),                             # 정수 아님
])
def test_parse_case_rejects_invalid(text):
    with pytest.raises(ValueError):
        llm.parse_case(text, 3)
