-- создаем табличку

create table visits (
    id serial primary key, -- целочисленное поле, которое увеличивается на 1 для каждой новой вставляемой строки. это нужно, чтобы не указывать id каждый раз при вставке
    ts timestamp,
    user_id int,
    url varchar
);

-- заполняем её данными
insert into visits
    (user_id, ts, url)
values
    (1, '2020-01-01 00:10', 'https://google.com'),
    (1, '2020-01-01 00:30', 'https://yandex.com'),
    (1, '2020-01-01 01:00', 'https://google.com'),
    (1, '2020-01-01 01:45', 'https://google.com'),
    (1, '2020-01-01 01:50', 'https://vk.com'),
    (2, '2020-02-01 10:10', 'https://google.com'),
    (2, '2020-02-01 13:10', 'https://google.ru'),
    (2, '2020-02-01 13:49:59', 'https://google.by');



with raw_sessions as ( -- конструкция with нужна, чтобы переиспользовать далее результат подзапроса
    select v.*,
           v.user_id::varchar || '_' || sum(case when v.start_session_flag then 1 else 0 end)
                                        over (partition by user_id order by ts)::varchar as session_number
    from (
             select user_id,
                    ts,
                    visit_id,
                    url,
                    time_from_prev_visit is null or time_from_prev_visit >= interval '40 minutes' as start_session_flag
             from (
                      select ts,
                             user_id,
                             ts - lag(ts) over (partition by user_id order by ts) as time_from_prev_visit,
                             url,
                             id                                                   as visit_id
                      from visits
                      order by user_id
                  ) u
         ) v
),
sessions as ( -- в блоке with можно объявлять несколько подзапросов
    select *,
           rank() over (partition by session_number order by ts) as visit_number_in_session
    from raw_sessions
)
select
    session_number,
    min(ts) as session_start_timestamp,
    max(ts) + interval '40 minutes' as session_end_timestamp,
    user_id,
    count(*) as visits_count,
    count(*) / extract('epoch' from (max(ts) + interval '40 minutes' - min(ts))) as visits_frequency,
    json_agg(url)::varchar as all_visited_urls
from sessions
group by session_number, user_id
;

