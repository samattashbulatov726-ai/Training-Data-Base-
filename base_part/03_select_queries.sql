-- 15 SELECT-запросов к базе cinema (PostgreSQL).
-- Для каждого запроса указан сценарий использования и применённые приёмы.
-- «Текущим моментом» считается дата последнего просмотра в таблице watch, чтобы результаты не зависели от дня запуска.

-- ============================================================================
-- 1. Топ-10 фильмов по среднему рейтингу (каталог «Лучшее по оценкам зрителей»)
--    Приёмы: JOIN, GROUP BY + HAVING, коррелированный подзапрос со STRING_AGG
-- ============================================================================
SELECT m.movie_id,
       m.title,
       m.release_year,
       ROUND(AVG(r.rating), 2) AS avg_rating,
       COUNT(*)                AS reviews_cnt,
       (SELECT STRING_AGG(g.name, ', ' ORDER BY g.name)
          FROM movie_genre mg
          JOIN genre g ON g.genre_id = mg.genre_id
         WHERE mg.movie_id = m.movie_id) AS genres
FROM movie m
JOIN review r ON r.movie_id = m.movie_id
GROUP BY m.movie_id, m.title, m.release_year
HAVING COUNT(*) >= 3
ORDER BY avg_rating DESC, reviews_cnt DESC, m.title
LIMIT 10;

-- ============================================================================
-- 2. Выручка по тарифам и доля тарифа в общей выручке (отчёт для финансистов)
--    Приёмы: LEFT JOIN (тарифы без оплат тоже попадают в отчёт), условие в ON,
--            оконная функция SUM() OVER () поверх агрегата
-- ============================================================================
SELECT p.plan_id,
       p.name AS plan_name,
       p.max_resolution,
       COUNT(pay.payment_id)                AS successful_payments,
       COALESCE(SUM(pay.amount), 0)         AS revenue,
       ROUND(100.0 * COALESCE(SUM(pay.amount), 0)
             / SUM(COALESCE(SUM(pay.amount), 0)) OVER (), 2) AS revenue_share_pct
FROM plan p
LEFT JOIN subscription s   ON s.plan_id = p.plan_id
LEFT JOIN payment pay      ON pay.subscription_id = s.subscription_id
                          AND pay.status = 'success'
GROUP BY p.plan_id, p.name, p.max_resolution
ORDER BY revenue DESC, p.plan_id
LIMIT 15;

-- ============================================================================
-- 3. Топ-3 фильма в каждом жанре («Лучшее в жанре» на главной странице)
--    Приёмы: CTE, JOIN четырёх таблиц, ROW_NUMBER() OVER (PARTITION BY ...)
-- ============================================================================
WITH genre_movie_rating AS (
    SELECT g.genre_id,
           g.name  AS genre,
           m.movie_id,
           m.title,
           ROUND(AVG(r.rating), 2) AS avg_rating,
           COUNT(r.review_id)      AS reviews_cnt
    FROM genre g
    JOIN movie_genre mg ON mg.genre_id = g.genre_id
    JOIN movie m        ON m.movie_id  = mg.movie_id
    JOIN review r       ON r.movie_id  = m.movie_id
    GROUP BY g.genre_id, g.name, m.movie_id, m.title
    HAVING COUNT(r.review_id) >= 2
),
ranked AS (
    SELECT gmr.*,
           ROW_NUMBER() OVER (PARTITION BY genre_id
                              ORDER BY avg_rating DESC, reviews_cnt DESC, title) AS rn
    FROM genre_movie_rating gmr
)
SELECT genre, rn AS place, title, avg_rating, reviews_cnt
FROM ranked
WHERE rn <= 3
ORDER BY genre, rn;

-- ============================================================================
-- 4. Кандидаты на возврат: смотрели в последние 90 дней, но активной подписки нет
--    (рассылка «вернитесь со скидкой»)
--    Приёмы: CTE, NOT EXISTS, скалярные подзапросы
-- ============================================================================
WITH recent_watch AS (
    SELECT user_id, COUNT(*) AS watches_cnt
    FROM watch
    WHERE started_at >= (SELECT MAX(started_at) FROM watch) - INTERVAL '90 days'
    GROUP BY user_id
)
SELECT u.user_id,
       u.display_name,
       c.name AS country,
       rw.watches_cnt AS watches_last_90d,
       (SELECT MAX(s.end_date) FROM subscription s WHERE s.user_id = u.user_id) AS last_subscription_end
FROM recent_watch rw
JOIN users u   ON u.user_id = rw.user_id
JOIN country c ON c.country_id = u.country_id
WHERE NOT EXISTS (SELECT 1
                    FROM subscription s
                   WHERE s.user_id = u.user_id
                     AND s.status = 'active')
ORDER BY rw.watches_cnt DESC, u.user_id
LIMIT 20;

-- ============================================================================
-- 5. Доля досмотревших фильм до конца и место в рейтинге «вовлечённости»
--    Приёмы: FILTER, RANK() OVER (ORDER BY ...) поверх агрегатов
-- ============================================================================
SELECT m.movie_id,
       m.title,
       COUNT(*)                                        AS watches_cnt,
       COUNT(*) FILTER (WHERE w.is_finished)           AS finished_cnt,
       ROUND(100.0 * COUNT(*) FILTER (WHERE w.is_finished) / COUNT(*), 1) AS completion_pct,
       RANK() OVER (ORDER BY 1.0 * COUNT(*) FILTER (WHERE w.is_finished) / COUNT(*) DESC) AS engagement_rank
FROM movie m
JOIN watch w ON w.movie_id = m.movie_id
GROUP BY m.movie_id, m.title
HAVING COUNT(*) >= 10
ORDER BY engagement_rank, watches_cnt DESC
LIMIT 15;

-- ============================================================================
-- 6. Выручка по месяцам: накопительный итог и прирост к прошлому месяцу
--    Приёмы: CTE, DATE_TRUNC, SUM() OVER (ORDER BY ...), LAG()
-- ============================================================================
WITH monthly AS (
    SELECT CAST(DATE_TRUNC('month', paid_at) AS DATE) AS month,
           SUM(amount)                                AS revenue
    FROM payment
    WHERE status = 'success'
    GROUP BY CAST(DATE_TRUNC('month', paid_at) AS DATE)
)
SELECT month,
       revenue,
       SUM(revenue) OVER (ORDER BY month)  AS cumulative_revenue,
       LAG(revenue) OVER (ORDER BY month)  AS prev_month_revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- ============================================================================
-- 7. Главный плательщик каждой страны (региональный отчёт по клиентам)
--    Приёмы: CTE, JOIN пяти таблиц, DENSE_RANK() и COUNT() OVER (PARTITION BY ...)
-- ============================================================================
WITH user_spend AS (
    SELECT u.user_id,
           u.display_name,
           c.country_id,
           c.name AS country,
           SUM(pay.amount) AS total_spent
    FROM users u
    JOIN country c      ON c.country_id = u.country_id
    JOIN subscription s ON s.user_id = u.user_id
    JOIN payment pay    ON pay.subscription_id = s.subscription_id
    WHERE pay.status = 'success'
    GROUP BY u.user_id, u.display_name, c.country_id, c.name
),
ranked AS (
    SELECT us.*,
           DENSE_RANK() OVER (PARTITION BY country_id ORDER BY total_spent DESC) AS spend_rank,
           COUNT(*)     OVER (PARTITION BY country_id)                           AS payers_in_country
    FROM user_spend us
)
SELECT country, display_name, total_spent, payers_in_country
FROM ranked
WHERE spend_rank = 1
ORDER BY total_spent DESC, country
LIMIT 15;

-- ============================================================================
-- 8. Актёры, чьи фильмы оцениваются выше всего (раздел «Любимцы зрителей»)
--    Приёмы: JOIN с подзапросом в FROM, GROUP BY + HAVING
-- ============================================================================
SELECT p.person_id,
       p.full_name,
       COUNT(*)                        AS movies_cnt,
       ROUND(AVG(mr.avg_rating), 2)    AS avg_movie_rating
FROM movie_cast mc
JOIN person p ON p.person_id = mc.person_id
JOIN (SELECT movie_id, AVG(rating) AS avg_rating
        FROM review
       GROUP BY movie_id) mr ON mr.movie_id = mc.movie_id
WHERE mc.role = 'actor'
GROUP BY p.person_id, p.full_name
HAVING COUNT(*) >= 5
ORDER BY avg_movie_rating DESC, movies_cnt DESC, p.full_name
LIMIT 10;

-- ============================================================================
-- 9. Режиссёры, которые сами писали сценарии своих фильмов, и их оценки
--    относительно среднего по сервису
--    Приёмы: самосоединение movie_cast (две роли одной персоны), LEFT JOIN, скалярный подзапрос
-- ============================================================================
SELECT p.full_name,
       COUNT(DISTINCT d.movie_id)                            AS films_cnt,
       ROUND(AVG(r.rating), 2)                               AS avg_rating,
       (SELECT ROUND(AVG(rating), 2) FROM review)            AS service_avg_rating,
       ROUND(AVG(r.rating) - (SELECT AVG(rating) FROM review), 2) AS diff_from_avg
FROM movie_cast d
JOIN movie_cast w ON w.movie_id  = d.movie_id
                 AND w.person_id = d.person_id
                 AND w.role      = 'writer'
JOIN person p     ON p.person_id = d.person_id
LEFT JOIN review r ON r.movie_id = d.movie_id
WHERE d.role = 'director'
GROUP BY p.person_id, p.full_name
HAVING COUNT(DISTINCT d.movie_id) >= 2
ORDER BY avg_rating DESC NULLS LAST, films_cnt DESC, p.full_name
LIMIT 10;

-- ============================================================================
-- 10. Доля отмен подписок по качеству тарифа (поиск «проблемных» уровней)
--     Приёмы: JOIN, FILTER, SUM(COUNT(*)) OVER ()
-- ============================================================================
SELECT pl.max_resolution,
       COUNT(*)                                                           AS subscriptions_cnt,
       COUNT(*) FILTER (WHERE s.status = 'cancelled')                     AS cancelled_cnt,
       ROUND(100.0 * COUNT(*) FILTER (WHERE s.status = 'cancelled') / COUNT(*), 1) AS cancelled_pct,
       ROUND(AVG(pl.price), 2)                                            AS avg_plan_price,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)                 AS share_of_all_subscriptions_pct
FROM subscription s
JOIN plan pl ON pl.plan_id = s.plan_id
GROUP BY pl.max_resolution
ORDER BY cancelled_pct DESC;

-- ============================================================================
-- 11. Самые «разносторонние» зрители: сколько разных жанров досмотрели до конца
--     (основа для рекомендаций и сегментации)
--     Приёмы: JOIN трёх таблиц, COUNT(DISTINCT), HAVING с подзапросом
-- ============================================================================
SELECT u.user_id,
       u.display_name,
       COUNT(DISTINCT mg.genre_id) AS distinct_genres,
       COUNT(DISTINCT w.movie_id)  AS distinct_movies
FROM users u
JOIN watch w        ON w.user_id  = u.user_id
JOIN movie_genre mg ON mg.movie_id = w.movie_id
WHERE w.is_finished
GROUP BY u.user_id, u.display_name
HAVING COUNT(DISTINCT w.movie_id) > (SELECT AVG(cnt)
                                       FROM (SELECT COUNT(DISTINCT movie_id) AS cnt
                                               FROM watch
                                              WHERE is_finished
                                              GROUP BY user_id) t)
ORDER BY distinct_genres DESC, distinct_movies DESC, u.user_id
LIMIT 10;

-- ============================================================================
-- 12. Самые «неожиданные» отзывы: оценка сильнее всего отличается от средней по фильму
--     (модерация и поиск накруток)
--     Приёмы: AVG() и COUNT() OVER (PARTITION BY movie_id), JOIN
-- ============================================================================
WITH rv AS (
    SELECT r.review_id,
           r.user_id,
           r.movie_id,
           r.rating,
           AVG(r.rating) OVER (PARTITION BY r.movie_id) AS movie_avg,
           COUNT(*)      OVER (PARTITION BY r.movie_id) AS movie_reviews
    FROM review r
)
SELECT u.display_name,
       m.title,
       rv.rating,
       ROUND(rv.movie_avg, 2)              AS movie_avg,
       ROUND(rv.rating - rv.movie_avg, 2)  AS diff
FROM rv
JOIN users u ON u.user_id  = rv.user_id
JOIN movie m ON m.movie_id = rv.movie_id
WHERE rv.movie_reviews >= 3
ORDER BY ABS(rv.rating - rv.movie_avg) DESC, m.title, u.display_name
LIMIT 10;

-- ============================================================================
-- 13. Просмотры по возрастным группам: сколько часов смотрят и доля группы
--     Приёмы: два CTE, EXTRACT, CASE, SUM() OVER ()
-- ============================================================================
WITH viewer AS (
    SELECT w.watch_id,
           w.watched_seconds,
           EXTRACT(YEAR FROM w.started_at) - EXTRACT(YEAR FROM u.birth_date) AS age
    FROM watch w
    JOIN users u ON u.user_id = w.user_id
),
bucketed AS (
    SELECT CASE WHEN age < 18 THEN '1) under 18'
                WHEN age < 25 THEN '2) 18-24'
                WHEN age < 35 THEN '3) 25-34'
                WHEN age < 45 THEN '4) 35-44'
                ELSE '5) 45+' END AS age_group,
           watched_seconds
    FROM viewer
)
SELECT age_group,
       COUNT(*)                                      AS watches_cnt,
       ROUND(SUM(watched_seconds) / 3600.0, 1)       AS hours_watched,
       ROUND(AVG(watched_seconds) / 60.0, 1)         AS avg_minutes_per_watch,
       ROUND(100.0 * SUM(watched_seconds) / SUM(SUM(watched_seconds)) OVER (), 1) AS share_of_hours_pct
FROM bucketed
GROUP BY age_group
ORDER BY age_group;

-- ============================================================================
-- 14. Фильмы, которые чаще всего пересматривают (признак «культового» контента)
--     Приёмы: подзапрос в FROM с HAVING, JOIN, агрегат над агрегатом
-- ============================================================================
SELECT m.movie_id,
       m.title,
       COUNT(*)      AS users_who_rewatched,
       SUM(t.times)  AS total_views_by_them
FROM (SELECT user_id, movie_id, COUNT(*) AS times
        FROM watch
       GROUP BY user_id, movie_id
      HAVING COUNT(*) > 1) t
JOIN movie m ON m.movie_id = t.movie_id
GROUP BY m.movie_id, m.title
ORDER BY users_who_rewatched DESC, total_views_by_them DESC, m.title
LIMIT 10;

-- ============================================================================
-- 15. Профиль активности пользователя: последний просмотренный фильм и суммарное время
--     в часах нарастающим итогом (блок «Продолжить знакомство» в личном кабинете)
--     Приёмы: CTE, SUM() OVER (PARTITION BY ... ORDER BY ...), ROW_NUMBER()
-- ============================================================================
WITH ordered_watch AS (
    SELECT w.user_id,
           w.movie_id,
           w.started_at,
           SUM(w.watched_seconds) OVER (PARTITION BY w.user_id
                                        ORDER BY w.started_at, w.watch_id) / 3600.0 AS cumulative_hours,
           ROW_NUMBER() OVER (PARTITION BY w.user_id
                              ORDER BY w.started_at DESC, w.watch_id DESC)          AS rn
    FROM watch w
)
SELECT u.user_id,
       u.display_name,
       m.title                        AS last_watched,
       ow.started_at                  AS last_watched_at,
       ROUND(ow.cumulative_hours, 1)  AS total_hours
FROM ordered_watch ow
JOIN users u ON u.user_id  = ow.user_id
JOIN movie m ON m.movie_id = ow.movie_id
WHERE ow.rn = 1
ORDER BY total_hours DESC, u.user_id
LIMIT 15;
