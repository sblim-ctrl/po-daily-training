import streamlit as st

import db
import llm
import ui

RATING_LABELS = {"helpful": "도움됐어요", "meh": "아쉬워요"}  # views/case.py와 같은 문구

user = st.session_state.get("user")
if not user:
    st.info("사이드바에 닉네임과 PIN을 입력하면 바로 시작할 수 있어요.")
    st.stop()

st.title("내 아카이브")

rows = db.my_answers(user["id"])
if not rows:
    st.info("아직 쌓인 답변이 없어요. 오늘의 브리핑에서 케이스를 고르면 여기에 모여요.")
    st.stop()

t = st.segmented_control("유형", ["전체", *llm.CASE_TYPES], default="전체") or "전체"  # 선택 해제하면 None
only_helpful = st.toggle("도움된 피드백만 보기")
filtered = [
    r for r in rows
    if (t == "전체" or r["cases"]["case_type"] == t)
    and (not only_helpful or r["rating"] == "helpful")
]
st.caption(f"{len(filtered)}개")
if only_helpful and not filtered:
    st.info("아직 도움됐어요로 평가한 피드백이 없어요. 케이스 화면에서 피드백을 평가하면 여기서 모아 볼 수 있어요.")

for r in filtered:
    c = r["cases"]
    with st.expander(f"{c['date']} · {c['case_type']} · {c['headline']}"):
        st.markdown(f"##### {c['question']}")
        st.markdown("#### 내 답변")
        st.write(r["body"])
        st.markdown("#### AI 피드백")
        if r["feedback"]:
            ui.feedback_cards(r["feedback"], r["id"])
            if r["rating"]:
                st.caption(f"내 평가: {RATING_LABELS[r['rating']]}")
        else:
            st.caption("아직 피드백이 없어요. [이 케이스 열기]에서 다시 받을 수 있어요.")
        if st.button("이 케이스 열기", key=f"open_{r['id']}"):
            st.session_state.case_id = c["id"]
            st.switch_page("views/case.py")
