import streamlit as st

import db
import sources

PUBLISH_TIME = "08:00"
SLOT_LABELS = {slot: label for slot, label, _ in sources.SLOTS}

user = st.session_state.get("user")
if not user:
    st.info("사이드바에 닉네임과 PIN을 입력하면 바로 시작할 수 있어요.")
    st.stop()

st.title("오늘의 브리핑")

today = db.today_kst()
cases = db.cases_by_date(today, "published")
if not cases:
    last = db.latest_published_date()
    if not last:
        st.info(f"아직 올라온 브리핑이 없어요. 매일 {PUBLISH_TIME}에 다시 확인해 주세요.")
        st.stop()
    st.info(f"오늘 브리핑은 매일 {PUBLISH_TIME}에 올라와요. 그동안 가장 최근 브리핑을 보여 드릴게요.")
    cases = db.cases_by_date(last, "published")

# Streamlit은 클릭마다 스크립트를 다시 실행하므로 하루에 세션당 1회만 기록한다
if st.session_state.get("briefing_logged") != str(today):
    db.log_event(user["id"], "briefing_view")
    st.session_state.briefing_logged = str(today)

st.caption(cases[0]["date"])
st.badge(cases[0]["case_type"], color="blue")
st.caption("관심 가는 뉴스 하나를 골라 5분 케이스로 연습해요.")

for c in cases:
    with st.container(border=True):
        st.caption(SLOT_LABELS.get(c["slot"], ""))
        st.markdown(f"##### {c['headline']}")
        st.write(c["summary"])
        st.markdown(f"[원문 보기]({c['source_url']})")
        if st.button("이 케이스로 연습하기", key=f"pick_{c['id']}"):
            st.session_state.case_id = c["id"]
            db.log_event(user["id"], "case_select", c["id"])
            st.switch_page("views/case.py")
