create table users (
  id bigint generated always as identity primary key,
  nickname text unique not null,
  pin_hash text not null,
  created_at timestamptz default now()
);
create table cases (
  id bigint generated always as identity primary key,
  date date not null,
  slot int not null,
  case_type text not null,
  headline text,
  summary text,
  source_url text,
  question text,
  rubric text,
  status text not null default 'draft',   -- 'draft' | 'published'
  created_at timestamptz default now()
);
create table answers (
  id bigint generated always as identity primary key,
  user_id bigint references users,
  case_id bigint references cases,
  body text not null,
  feedback text,
  rating text,                              -- 'helpful' | 'meh' | null
  created_at timestamptz default now()
);
create table events (
  id bigint generated always as identity primary key,
  user_id bigint references users,
  name text not null,
  case_id bigint,
  created_at timestamptz default now()
);
-- 정책을 두지 않으므로 anon 키로는 접근할 수 없다. 앱은 서버에서 secret 키로만 접근한다.
alter table users enable row level security;
alter table cases enable row level security;
alter table answers enable row level security;
alter table events enable row level security;
