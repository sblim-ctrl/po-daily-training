"""운영진 검수 (R1, R2). 사용자 로그인 없이 ADMIN_PASSWORD로만 보호한다."""
import hmac

import streamlit as st

import db
import llm

st.title("운영진 검수")

pw = st.text_input("운영진 비밀번호", type="password")
if not pw:
    st.stop()
if not hmac.compare_digest(pw, st.secrets["ADMIN_PASSWORD"]):
    st.error("비밀번호가 맞지 않아요. 다시 입력해 주세요.")
    st.stop()

today = db.today_kst()
st.caption(str(today))
st.badge(llm.case_type_for(today), color="blue")

if st.button("오늘 케이스 만들기", type="primary", help="오늘 초안을 새로 만들어요. 이미 발행한 케이스는 그대로 남아요."):
    with st.spinner("뉴스를 모으고 케이스를 만들고 있어요. 1~2분 걸려요."):
        drafts, errors = llm.generate_daily(today)
        # 이미 발행한 슬롯에 초안이 또 생기면 홈에 같은 슬롯 카드가 두 장 보인다
        published = {c["slot"] for c in db.cases_by_date(today, "published")}
        db.replace_drafts(today, [d for d in drafts if d["slot"] not in published])
    st.session_state.gen_errors = errors

for slot, msg in st.session_state.get("gen_errors", []):
    st.error(f"{slot}번 슬롯을 만들지 못했어요 ({msg}). 다시 시도하려면 [오늘 케이스 만들기]를 눌러 주세요.")

cases = db.cases_by_date(today)
if not cases:
    st.info("아직 만든 케이스가 없어요. [오늘 케이스 만들기]를 누르면 슬롯 3개가 채워져요.")

for c in cases:
    is_published = c["status"] == "published"
    with st.form(f"case_{c['id']}"):
        st.caption(f"슬롯 {c['slot']}")
        if is_published:
            st.badge("발행됨", color="green")
        else:
            st.badge("초안", color="gray")
        fields = {
            "headline": st.text_input("헤드라인", c["headline"] or ""),
            "summary": st.text_area("요약", c["summary"] or ""),
            "question": st.text_area("질문", c["question"] or ""),
            "rubric": st.text_area("루브릭", c["rubric"] or ""),
        }
        st.markdown(f"[원문 보기]({c['source_url']})")
        left, right = st.columns(2)
        save = left.form_submit_button("저장하기")
        publish = right.form_submit_button("발행하기", disabled=is_published)
    if save or publish:
        db.update_case(c["id"], fields)
        if publish:
            db.publish_case(c["id"])
        st.toast("발행했어요" if publish else "저장했어요")
        st.rerun()
