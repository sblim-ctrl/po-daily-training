"""OpenAI로 케이스를 만들고 답변에 피드백한다. DB에는 쓰지 않는다."""
import json
import logging

import streamlit as st
from openai import OpenAI

from sources import SLOTS

MODEL = "gpt-5-mini"  # gpt-5 계열은 temperature를 지원하지 않아 넘기지 않는다

CASE_TYPES = ["문제 정의", "지표 설계", "우선순위", "개선안", "역기획"]
TYPE_HINTS = {
    "문제 정의": "이 기능은 어떤 사용자 문제를 풀려는 걸까?",
    "지표 설계": "이 기능의 성공 지표를 무엇으로 잡겠는가?",
    "우선순위": "후보 기능 3개 중 무엇을 먼저 하겠는가?",
    "개선안": "이 서비스의 가장 큰 불편 하나와 개선안은?",
    "역기획": "이 기능이 나온 배경과 의사결정을 추론한다면?",
}
CASE_KEYS = ("pick", "headline", "summary", "question", "rubric")

CASE_SYSTEM = "너는 PO/PM 취업 준비생을 위한 케이스 면접 출제자다. 반드시 JSON 객체 하나만 출력한다."
CASE_PROMPT = """[슬롯] {label}
[오늘의 케이스 유형] {case_type} (예시 질문: {hint})
[후보 뉴스]
{candidates}

지시:
1. 기능 출시, 정책 변경, 실험, 지표 변화처럼 '프로덕트 의사결정'이 담긴 뉴스 1개를 고른다. 순수 광고, 브랜드 캠페인, 방법론 아티클, 주가 기사는 제외한다.
2. headline: 한국어 40자 이내. 명사형으로 끝내고 '~다'로 끝내지 않는다.
3. summary: 후보에 적힌 사실만으로 해요체 2~3문장 (예: "~를 출시했어요."). 원문 문장을 그대로 옮기지 않고, 추측을 넣지 않는다.
4. question: '{case_type}' 유형의 케이스 질문 1개. 해요체로, 5분 안에 답할 수 있는 범위로 (예: "이 기능의 성공 지표를 무엇으로 잡겠어요?").
5. rubric: 좋은 답이 갖춰야 할 평가 기준 3~4개 (문자열 배열, 명사형).
6. 이모지, 느낌표, 과장 표현(혁신적, 최고의)을 쓰지 않는다.
출력 JSON 키: pick(고른 후보 번호, 정수), headline, summary, question, rubric"""

FEEDBACK_SYSTEM = (
    "너는 PO 케이스 면접 코치다. 루브릭 기준으로 구체적으로 피드백한다. 이모지·느낌표·과장 표현은 쓰지 않는다.\n"
    "모든 문장은 해요체 평서문(~해요, ~있어요, ~좋아요, ~예요)으로 끝낸다. 인용한 예시 문장도 마찬가지다.\n"
    "금지 어미: 격식체(~합니다, ~습니다, ~입니다), 단정형(~한다, ~이다), 명령형(~하세요, ~해 보세요, ~하십시오).\n"
    "제안은 명령하지 않고 '~하면 좋아요', '~를 넣으면 더 설득력 있어요'처럼 쓴다."
)
# 소제목을 굵은 글씨로 받는다: 케이스 화면의 "#### AI 피드백" 아래에 들어가서 제목 위계가 뒤집히지 않게
FEEDBACK_PROMPT = """[케이스 질문] {question}
[평가 루브릭]
{rubric}
[지원자 답변]
{answer}

아래 형식의 한국어 마크다운으로만 답한다. 각 항목은 루브릭 기준과 연결하고 해요체로 쓴다.
**강점**
- (2개)

**빈틈**
- (2개)

**개선 제안**
- (1~2개, 바로 고쳐 쓸 수 있는 문장 예시 포함)

문장 끝 규칙: 모든 문장과 예시 문장을 해요체 평서문으로 끝낸다.
좋은 예: "지표를 하나로 좁히면 좋아요." / 예시 문장: "탐색 시간을 20% 줄이는 걸 목표로 잡겠어요."
나쁜 예: "좁혀야 합니다.", "명시하세요.", "목표로 설정한다." """


@st.cache_resource
def _client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"], timeout=60)


def _chat(system, user, json_mode=False):
    kw = {"response_format": {"type": "json_object"}} if json_mode else {}
    r = _client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        **kw,
    )
    return r.choices[0].message.content


def case_type_for(d):
    return CASE_TYPES[d.weekday() % 5]


def parse_case(text, n):
    data = json.loads(text)  # JSONDecodeError는 ValueError의 하위 클래스
    if not isinstance(data, dict) or any(k not in data for k in CASE_KEYS):
        raise ValueError("응답에 필요한 키가 없음")
    pick = data["pick"]
    if type(pick) is not int or not 0 <= pick < n:  # bool도 int라서 type으로 비교
        raise ValueError(f"pick 범위 오류: {pick!r}")
    rubric = data["rubric"]
    if isinstance(rubric, list):
        rubric = "\n".join(f"- {r}" for r in rubric)
    return {**{k: data[k] for k in CASE_KEYS}, "rubric": rubric}


def generate_case(label, case_type, candidates):
    if not candidates:
        raise ValueError("후보 뉴스 없음")
    candidates = candidates[:20]
    numbered = "\n".join(f"{i}. {c['title']} | {c['desc']}" for i, c in enumerate(candidates))
    text = _chat(
        CASE_SYSTEM,
        CASE_PROMPT.format(label=label, case_type=case_type, hint=TYPE_HINTS[case_type], candidates=numbered),
        json_mode=True,
    )
    c = parse_case(text, len(candidates))
    # URL은 LLM이 쓴 값 대신 후보에서 가져온다 (환각 방지)
    return {
        "headline": c["headline"], "summary": c["summary"], "question": c["question"],
        "rubric": c["rubric"], "source_url": candidates[c["pick"]]["url"],
    }


def generate_daily(d):
    case_type = case_type_for(d)
    drafts, errors = [], []
    for slot, label, fetch in SLOTS:
        try:
            drafts.append({"slot": slot, "case_type": case_type, **generate_case(label, case_type, fetch())})
        except (ValueError, RuntimeError) as e:
            logging.warning("slot %s failed: %s", slot, e)
            errors.append((slot, str(e)))
        except Exception as e:
            # requests 예외 메시지의 URL에 DART crtfc_key가 들어 있어서 타입명만 노출한다
            logging.warning("slot %s failed: %s", slot, type(e).__name__)
            errors.append((slot, type(e).__name__))
    return drafts, errors


def feedback(question, rubric, answer):
    return _chat(FEEDBACK_SYSTEM, FEEDBACK_PROMPT.format(question=question, rubric=rubric, answer=answer))
