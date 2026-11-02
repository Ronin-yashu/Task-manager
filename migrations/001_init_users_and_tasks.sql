create extension if not exists "pgcrypto";

create type task_status as enum ('pending', 'in_progress', 'completed');
create type task_priority as enum ('low', 'medium', 'high');

create table users (
  id          uuid primary key default gen_random_uuid(),
  google_id   text not null unique,
  email       text not null unique,
  name        text,
  avatar_url  text,
  created_at  timestamptz not null default now()
);

create table tasks (
  id           uuid primary key default gen_random_uuid(),
  title        text not null check (char_length(title) between 1 and 200),
  description  text,
  status       task_status not null default 'pending',
  priority     task_priority not null default 'medium',
  due_date     date,
  created_by   uuid not null references users(id) on delete cascade,
  assigned_to  uuid references users(id) on delete set null,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),
  completed_at timestamptz
);

create index idx_tasks_assigned_to on tasks(assigned_to);
create index idx_tasks_created_by  on tasks(created_by);
create index idx_tasks_status      on tasks(status);

create or replace function set_updated_at() returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger trg_tasks_updated_at
before update on tasks
for each row execute function set_updated_at();

alter table users enable row level security;
alter table tasks enable row level security;