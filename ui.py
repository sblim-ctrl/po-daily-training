"""화면 공용 조각. CSS는 AI 피드백 카드의 key 클래스에만 건다."""
import streamlit as st

import llm

# 소제목 → (카드 key 이름, 배지 색). 배경색은 아래 CSS에서 key 이름으로 정한다
SECTION_STYLE = {"강점": ("strength", "green"), "빈틈": ("gap", "orange"), "개선 제안": ("tip", "blue")}

# toss.md: radius-xl 16px 카드, 그림자·2px 보더·left-rail 없음. green-50·orange-50은 toss.md에 없어 TDS 공개 팔레트 값을 쓴다
FEEDBACK_CSS = """<style>
[class*="st-key-fb-"] { border-radius: 16px; padding: 16px 20px; gap: 8px; }
[class*="st-key-fb-strength"] { background: #F0FAF6; }
[class*="st-key-fb-gap"] { background: #FFF3E0; }
[class*="st-key-fb-tip"] { background: #E8F3FF; }
[class*="st-key-fb-plain"] { background: #F9FAFB; border: 1px solid #E5E8EB; }
[class*="st-key-fb-"] p, [class*="st-key-fb-"] li { color: #191F28; }
</style>"""


def feedback_cards(text, key):
    """피드백을 소제목별 색 카드로 그린다. key는 화면 안에서 카드끼리 겹치지 않게 하는 값(답변 id)."""
    st.html(FEEDBACK_CSS)
    for title, body in llm.split_feedback(text):
        name, color = SECTION_STYLE.get(title, ("plain", None))
        with st.container(key=f"fb-{name}-{key}"):
            if title:
                st.badge(title, color=color)
            st.markdown(body)
