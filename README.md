# PO 데일리 트레이닝

PO/PM 취준생이 하루 세 번 짧게 들어와 프로덕트 사고력을 훈련하고, 그 기록이 자연스럽게 포트폴리오로 쌓이는 AI 케이스 트레이닝 서비스.

## P0 기능

- 오늘의 브리핑: tech 뉴스 헤드라인·요약 3개 (Hacker News, 네이버 뉴스, Open DART)
- 케이스 답변: 브리핑 하나를 골라 요일별 유형(문제 정의, 지표 설계, 우선순위, 개선안, 역기획) 질문에 답변
- AI 피드백: 강점, 빈틈, 개선 제안. 도움됨/아쉬움 평가
- 내 아카이브: 지난 답변과 피드백을 날짜순으로, 유형별 필터
- 운영진 검수: 케이스 생성, 수정, 부분 발행 (`ADMIN_PASSWORD`로 보호)

## 로컬 실행

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # 값 7개 입력
.venv/bin/streamlit run app.py
```

## Supabase 설정

1. 새 프로젝트를 만들고 SQL Editor에서 `schema.sql`을 실행해요.
2. Project Settings → API Keys의 Project URL과 **secret(service_role) 키**를 `SUPABASE_URL`, `SUPABASE_KEY`에 넣어요. 모든 테이블에 RLS가 켜져 있고 정책이 없어서 anon/publishable 키로는 동작하지 않아요.

## 배포

Streamlit Community Cloud에서 이 저장소의 `main` 브랜치, `app.py`, Python 3.12를 고르고, Advanced settings → Secrets에 `secrets.toml` 내용을 붙여넣어요.

## 디자인

토스 디자인 시스템의 시각 언어(단일 강조색 `#3182F6`, Pretendard, 라운드, 해요체)를 `.streamlit/config.toml` 테마로 적용했어요. 토스 브랜드와는 관련이 없어요.

## 약관 주의

슬롯 2는 네이버 뉴스 검색 결과를 OpenAI에 넣어 케이스를 만드는데, 네이버 검색 API 약관의 AI 활용 금지 조항에 걸릴 수 있으니 공개 운영 전에 약관을 확인하고 필요하면 출처를 바꿔야 해요.

## 범위 밖 (P1)

동료 답변 투표, 저녁 메모, 카카오 로그인·알림

## 기획 문서

- [기획서](docs/PO%20데일리%20트레이닝%20기획서.md)
- [PRD](docs/PRD%20PO%20데일리%20트레이닝%20(MVP).md)
