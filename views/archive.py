import streamlit as st

import db
import llm

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
filtered = [r for r in rows if t == "전체" or r["cases"]["case_type"] == t]
st.caption(f"{len(filtered)}개")

for r in filtered:
    c = r["cases"]
    with st.expander(f"{c['date']} · {c['case_type']} · {c['headline']}"):
        st.markdown(f"##### {c['question']}")
        st.markdown("#### 내 답변")
        st.write(r["body"])
        st.markdown("#### AI 피드백")
        if r["feedback"]:
            st.markdown(r["feedback"])
        else:
            st.caption("아직 피드백이 없어요. [이 케이스 열기]에서 다시 받을 수 있어요.")
        if st.button("이 케이스 열기", key=f"open_{r['id']}"):
            st.session_state.case_id = c["id"]
            st.switch_page("views/case.py")
