import streamlit as st

import db

st.set_page_config(page_title="PO 데일리 트레이닝", page_icon=":material/edit_note:")

with st.sidebar:
    user = st.session_state.get("user")
    if user:
        st.caption(f"{user['nickname']}님")
        if st.button("로그아웃"):
            st.session_state.clear()
            st.rerun()
    else:
        with st.form("login"):
            st.markdown("##### PO 데일리 트레이닝")
            nickname = st.text_input("닉네임", max_chars=20)
            pin = st.text_input("PIN 4자리", type="password", max_chars=4)
            if st.form_submit_button("시작하기", type="primary"):
                nickname = nickname.strip()
                if not (1 <= len(nickname) <= 20 and pin.isdigit() and len(pin) == 4):
                    st.error("닉네임과 숫자 4자리 PIN을 입력해 주세요.")
                elif (user := db.login(nickname, pin)) is None:
                    st.error("PIN이 맞지 않아요. 처음 정한 4자리를 다시 입력해 주세요.")
                else:
                    st.session_state.user = user
                    st.rerun()
        st.caption("처음 쓰는 닉네임이면 바로 가입돼요. PIN을 잊으면 기록을 불러올 수 없어요.")

st.markdown("**PO-Daily-Training**")

st.navigation([
    st.Page("views/home.py", title="오늘의 브리핑", icon=":material/newspaper:", default=True),
    st.Page("views/case.py", title="케이스 답변", icon=":material/edit_note:"),
    st.Page("views/archive.py", title="내 아카이브", icon=":material/inventory_2:"),
    st.Page("views/admin.py", title="운영진 검수", icon=":material/fact_check:"),
]).run()
