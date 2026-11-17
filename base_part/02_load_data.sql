

BEGIN;

\copy country      (country_id, iso_code, name)                                                          FROM 'data/country.csv'      WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy plan         (plan_id, name, price, max_screens, max_resolution)                                   FROM 'data/plan.csv'         WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy genre        (genre_id, name)                                                                      FROM 'data/genre.csv'        WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy person       (person_id, full_name, birth_date)                                                    FROM 'data/person.csv'       WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy movie        (movie_id, title, description, release_year, duration_min, age_rating)                FROM 'data/movie.csv'        WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy users        (user_id, country_id, email, password_hash, display_name, birth_date, registered_at)  FROM 'data/users.csv'        WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy subscription (subscription_id, user_id, plan_id, start_date, end_date, status)                     FROM 'data/subscription.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy payment      (payment_id, subscription_id, amount, paid_at, payment_method, status)                FROM 'data/payment.csv'      WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy movie_genre  (movie_id, genre_id)                                                                  FROM 'data/movie_genre.csv'  WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy movie_cast   (movie_id, person_id, role, character_name)                                           FROM 'data/movie_cast.csv'   WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy watch        (watch_id, user_id, movie_id, started_at, watched_seconds, is_finished)               FROM 'data/watch.csv'        WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy review       (review_id, user_id, movie_id, rating, review_text, created_at)                       FROM 'data/review.csv'       WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

SELECT setval(pg_get_serial_sequence('country',      'country_id'),      (SELECT MAX(country_id)      FROM country));
SELECT setval(pg_get_serial_sequence('plan',         'plan_id'),         (SELECT MAX(plan_id)         FROM plan));
SELECT setval(pg_get_serial_sequence('genre',        'genre_id'),        (SELECT MAX(genre_id)        FROM genre));
SELECT setval(pg_get_serial_sequence('person',       'person_id'),       (SELECT MAX(person_id)       FROM person));
SELECT setval(pg_get_serial_sequence('movie',        'movie_id'),        (SELECT MAX(movie_id)        FROM movie));
SELECT setval(pg_get_serial_sequence('users',        'user_id'),         (SELECT MAX(user_id)         FROM users));
SELECT setval(pg_get_serial_sequence('subscription', 'subscription_id'), (SELECT MAX(subscription_id) FROM subscription));
SELECT setval(pg_get_serial_sequence('payment',      'payment_id'),      (SELECT MAX(payment_id)      FROM payment));
SELECT setval(pg_get_serial_sequence('watch',        'watch_id'),        (SELECT MAX(watch_id)        FROM watch));
SELECT setval(pg_get_serial_sequence('review',       'review_id'),       (SELECT MAX(review_id)       FROM review));

COMMIT;

SELECT 'country' AS tbl, COUNT(*) AS cnt FROM country
UNION ALL SELECT 'plan',         COUNT(*) FROM plan
UNION ALL SELECT 'genre',        COUNT(*) FROM genre
UNION ALL SELECT 'person',       COUNT(*) FROM person
UNION ALL SELECT 'movie',        COUNT(*) FROM movie
UNION ALL SELECT 'users',        COUNT(*) FROM users
UNION ALL SELECT 'subscription', COUNT(*) FROM subscription
UNION ALL SELECT 'payment',      COUNT(*) FROM payment
UNION ALL SELECT 'movie_genre',  COUNT(*) FROM movie_genre
UNION ALL SELECT 'movie_cast',   COUNT(*) FROM movie_cast
UNION ALL SELECT 'watch',        COUNT(*) FROM watch
UNION ALL SELECT 'review',       COUNT(*) FROM review
ORDER BY tbl;
