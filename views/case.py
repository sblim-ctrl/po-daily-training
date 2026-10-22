import logging

import streamlit as st

import db
import llm

MIN_LEN = 50
RATING_LABELS = {"helpful": "도움됐어요", "meh": "아쉬워요"}


def _generate_feedback(case, answer):
    try:
        with st.spinner("피드백을 만들고 있어요. 최대 1분 걸려요."):
            text = llm.feedback(case["question"], case["rubric"], answer["body"])
        db.set_feedback(answer["id"], text)
    except Exception:
        logging.exception("feedback failed for answer %s", answer["id"])
        st.error("피드백을 만들지 못했어요. 답변은 저장됐으니 [피드백 다시 받기]를 눌러 주세요.")
        return
    st.rerun()


user = st.session_state.get("user")
if not user:
    st.info("사이드바에 닉네임과 PIN을 입력하면 바로 시작할 수 있어요.")
    st.stop()

case_id = st.session_state.get("case_id")
case = db.get_case(case_id) if case_id else None
if not case:
    st.info("오늘의 브리핑에서 케이스를 고르면 여기서 답변할 수 있어요.")
    st.page_link("views/home.py", label="오늘의 브리핑으로 가기")
    st.stop()

st.title("케이스 답변")
st.badge(case["case_type"], color="blue")
st.caption(case["date"])
st.markdown(f"##### {case['headline']}")
with st.expander("뉴스 요약 보기"):
    st.write(case["summary"])
    st.markdown(f"[원문 보기]({case['source_url']})")
st.markdown(f"#### {case['question']}")

answer = db.my_answer(user["id"], case_id)

if not answer:
    # 제출 후 피드백이 실패하면 입력창을 지우고 아래 "답변이 있을 때" 화면으로 넘어간다
    draft_area = st.empty()
    with draft_area.container():
        body = st.text_area(
            "내 답변", height=260, key=f"draft_{case_id}",
            placeholder="결론, 근거, 지표와 리스크 순서로 쓰면 5분 안에 정리할 수 있어요.",
        )
        st.caption(f"{len(body.strip())}자")
        submitted = st.button("답변 제출하기", type="primary")
    if submitted:
        text = body.strip()
        if not text:
            st.error("답변을 입력해 주세요.")
        elif len(text) < MIN_LEN and st.session_state.get("short_ok") != case_id:
            st.session_state.short_ok = case_id
            st.warning(
                f"답변이 {MIN_LEN}자보다 짧아요. 근거를 한두 문장 더하면 피드백이 정확해져요. "
                "이대로 내려면 [답변 제출하기]를 한 번 더 눌러 주세요."
            )
        else:
            draft_area.empty()
            answer = db.save_answer(user["id"], case_id, text)
            db.log_event(user["id"], "answer_submit", case_id)
            _generate_feedback(case, answer)

if answer:
    st.markdown("#### 내 답변")
    st.write(answer["body"])
    if not answer["feedback"]:
        st.info("아직 피드백이 없어요. 답변은 저장돼 있어요.")
        if st.button("피드백 다시 받기", type="primary"):
            _generate_feedback(case, answer)
    else:
        st.markdown("#### AI 피드백")
        st.markdown(answer["feedback"])
        if answer["rating"]:
            st.caption(f"내 평가: {RATING_LABELS[answer['rating']]}")
        else:
            st.caption("이 피드백이 도움이 됐나요?")
            left, right = st.columns(2)
            rating = None
            if left.button("도움됐어요", width="stretch"):
                rating = "helpful"
            if right.button("아쉬워요", width="stretch"):
                rating = "meh"
            if rating:
                db.set_rating(answer["id"], rating)
                db.log_event(user["id"], "feedback_rate", case_id)
                st.toast("의견을 남겼어요")
                st.rerun()

st.page_link("views/archive.py", label="내 아카이브 보기")
