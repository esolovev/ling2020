--Выведите 5 произвольных заказов.
select * from orders limit 5;

--Выведите 5 первых заказов.
select * from orders order by created limit 5;

--Выведите общее количество заказов, количество встретившихся городов и количество встретившихся пользователей.
select
    count(*) as total_orders,
    count(distinct city) as total_cities,
    count(distinct user_id) as total_users
from orders;

--Выведите 15 последних заказов в Москве.
select * from orders where city = 'Москва' order by created desc limit 5;

--Выведите 5 первых и 5 последних заказов одним запросом
(select * from orders order by created limit 5)
union all
(select * from orders order by created desc limit 5);


--Для каждого пользователя выведите количество его заказов. Отсортируйте результат по убыванию количества заказов.
select
    user_id,
    count(*) as orders
from
    orders
group by
    user_id
order by
    count(*) desc;

--Для каждого пользователя выведите количество его заказов за последнюю неделю (https://www.postgresqltutorial.com/postgresql-now/).
select
    user_id,
    count(*) as cnt
from orders
where created + interval '13 month' >= now() -- выведем за другой период, чтобы был хоть какой-то результат
group by user_id
order by cnt desc;

--Для каждого пользователя выведите количество его заказов за последнюю неделю, если это количество больше 1.
select
    user_id,
    count(*) as cnt
from orders
where created + interval '13 month' >= now() -- выведем за другой период, чтобы был хоть какой-то результат
group by user_id
having count(*) > 1
order by cnt desc;

--Выведите количество заказов по дням. Добавьте к результату предыдущего запроса количество пользователей, совершивших хотя бы один заказ в этот день (эта метрика называется DAU - Daily Active Users)
select
    date_trunc('day', created) as dt,
    count(*) as orders_cnt,
    count(distinct user_id) as dau
from
    orders
group by date_trunc('day', created)
order by orders_cnt desc;

--Выведите количество пользователей, сделавших заказы как минимум в двух городах (за всю историю)
select count(*) from (
     select
        user_id,
        count(distinct city) as cities_cnt
     from
        orders
     group by
        user_id
 ) u
where cities_cnt = 2;


--Посчитайте величину "среднее количество городов, в которых делает заказ пользователь" подневно (например, если в день Х пользователь A совершал заказы в двух разных городах, а пользователи B и C каждый в каком-то одном городе, метрика в этот день будет равна 4/3 = 1.33..)
select dt, avg(cities_cnt) as avg_cities_cnt_by_user from (
     select
        user_id,
        date_trunc('day', created) as dt,
        count(distinct city) as cities_cnt
     from
        orders
     group by
        user_id, date_trunc('day', created)
 ) u
group by dt;

--Назовём пользователя активированным в день Х, если в этот день он совершил свой первый заказ. Посчитайте количество активированных пользователей по дням.

select
    first_order_dt,
    count(*) as new_users
from (
    select
        user_id,
        min(date_trunc('day', created)) as first_order_dt
    from
        orders
    group by
        user_id
) u
group by first_order_dt
order by first_order_dt;





--Вычислите для каждого пользователя величину "время, прошедшее от регистрации до первого заказа".
with first_order_timestamps as (
    select user_id,
           min(created) as first_order_timestamp
    from orders
    group by user_id
)

select
    user_id,
    first_order_timestamp - created as time_to_first_order
from users join first_order_timestamps on users.id = first_order_timestamps.user_id;

--Посчитайте среднее значение этой величины для каждого города (под городом пользователя подразумевается город его первого заказа).
with first_order_timestamps as (
    select user_id,
           min(created) as first_order_timestamp
    from orders
    group by user_id
),
     first_order_timestamps_and_cities as (
    select
        first_order_timestamps.user_id,
        min(first_order_timestamp) as first_order_timestamp,
        min(city) as first_order_city
    from
         orders
    join -- после джойна у нас могла получиться ситуация, что у одного пользователя есть два или больше самых ранних заказа,
        first_order_timestamps -- произошедших одновременно. Поэтому в данном случае можно вытащить произольный город с помощью группировки по пользователям
    on orders.user_id = first_order_timestamps.user_id and first_order_timestamps.first_order_timestamp = orders.created
    group by first_order_timestamps.user_id
)
select
    first_order_city,
    avg(time_to_first_order) as avg_time_to_first_order
from (
    select
        user_id,
        first_order_city,
        first_order_timestamp - created as time_to_first_order
    from users join first_order_timestamps_and_cities on users.id = first_order_timestamps_and_cities.user_id
) v
group by first_order_city
;



--Назовём пользователя принадлежащего когорте Х, если он совершил свой первый заказ в день Х. Постройте таблицу вида "день, когорта, retention", где retention когорты Х в день Y - доля пользователей, совершивших хотя бы один заказ в день Y, среди пользователей, совершивших первый заказ в день X. (подробнее о когортном анализе здесь https://en.wikipedia.org/wiki/Cohort_analysis https://gopractice.ru/cohort_analysis/)
--- TODO
--Выведите 10% первых заказов (примечание: нужно сделать это за один запрос, а не посчитать отдельно количество строк в таблице, поделить его на 10 и вставить в другой запрос)
--- TODO
--Выполните задание 3.3 (про когорты) с помощью оконных функций.
--- TODO







