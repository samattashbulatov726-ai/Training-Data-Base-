#!/usr/bin/env python3
"""Генератор синтетических данных для БД cinema (seed зафиксирован -> результат воспроизводим).

Запуск из корня репозитория:  python3 data/generate_data.py
Результат: data/*.csv (по одному файлу на таблицу).
Данные полностью вымышленные: фильмы, люди, e-mail и хэши паролей не принадлежат реальным лицам.
"""
import csv
import hashlib
import os
import random
from calendar import monthrange
from datetime import date, datetime, timedelta, timezone

random.seed(42)
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = date(2026, 11, 17)
NOW = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)


def write(name, header, rows):
    with open(os.path.join(OUT, name + ".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}.csv: {len(rows)} строк")


def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    y += d.year
    mo += 1
    return date(y, mo, min(d.day, monthrange(y, mo)[1]))


def ts(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S+00")


def wchoice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]


# ------------------------------------------------------------------ country
COUNTRIES = [
    ("RU", "Russia"), ("US", "United States"), ("GB", "United Kingdom"), ("DE", "Germany"),
    ("FR", "France"), ("IT", "Italy"), ("ES", "Spain"), ("PT", "Portugal"), ("NL", "Netherlands"),
    ("BE", "Belgium"), ("CH", "Switzerland"), ("AT", "Austria"), ("SE", "Sweden"), ("NO", "Norway"),
    ("DK", "Denmark"), ("FI", "Finland"), ("PL", "Poland"), ("CZ", "Czechia"), ("SK", "Slovakia"),
    ("HU", "Hungary"), ("RO", "Romania"), ("BG", "Bulgaria"), ("GR", "Greece"), ("TR", "Turkey"),
    ("UA", "Ukraine"), ("BY", "Belarus"), ("KZ", "Kazakhstan"), ("UZ", "Uzbekistan"), ("AM", "Armenia"),
    ("GE", "Georgia"), ("AZ", "Azerbaijan"), ("EE", "Estonia"), ("LV", "Latvia"), ("LT", "Lithuania"),
    ("IE", "Ireland"), ("IS", "Iceland"), ("CA", "Canada"), ("MX", "Mexico"), ("BR", "Brazil"),
    ("AR", "Argentina"), ("CL", "Chile"), ("CO", "Colombia"), ("PE", "Peru"), ("CN", "China"),
    ("JP", "Japan"), ("KR", "South Korea"), ("IN", "India"), ("ID", "Indonesia"), ("TH", "Thailand"),
    ("VN", "Vietnam"), ("PH", "Philippines"), ("MY", "Malaysia"), ("SG", "Singapore"), ("AU", "Australia"),
    ("NZ", "New Zealand"), ("ZA", "South Africa"), ("EG", "Egypt"), ("MA", "Morocco"), ("NG", "Nigeria"),
    ("KE", "Kenya"), ("AE", "United Arab Emirates"), ("IL", "Israel"), ("SA", "Saudi Arabia"),
]
country_rows = [(i + 1, iso, n) for i, (iso, n) in enumerate(COUNTRIES)]
write("country", ["country_id", "iso_code", "name"], country_rows)

# ------------------------------------------------------------------ plan
TIERS = [  # name, screens, resolution, базовая цена за месяц
    ("Mobile", 1, "SD", 2.99), ("Basic", 1, "SD", 4.99), ("Student", 1, "HD", 3.99),
    ("Kids", 2, "HD", 5.49), ("Standard", 2, "HD", 7.99), ("Plus", 3, "FHD", 9.99),
    ("Premium", 4, "4K", 13.99), ("Family", 6, "FHD", 15.99), ("Ultra", 5, "4K", 17.99),
    ("Business", 10, "4K", 29.99),
]
DURATIONS = [("Monthly", 1, 1.0), ("Quarterly", 3, 0.95), ("Semiannual", 6, 0.9),
             ("Annual", 12, 0.8), ("Promo", 1, 0.5)]
plan_rows, plan_months, plan_price = [], {}, {}
pid = 0
for tname, scr, res, base in TIERS:
    for dname, months, disc in DURATIONS:
        pid += 1
        price = round(base * months * disc, 2)
        plan_rows.append((pid, f"{tname} {dname}", f"{price:.2f}", scr, res))
        plan_months[pid] = months
        plan_price[pid] = price
write("plan", ["plan_id", "name", "price", "max_screens", "max_resolution"], plan_rows)

# ------------------------------------------------------------------ genre
GENRES = [
    "Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary", "Drama",
    "Family", "Fantasy", "History", "Horror", "Music", "Musical", "Mystery", "Romance", "Sci-Fi",
    "Sport", "Thriller", "War", "Western", "Cyberpunk", "Space Opera", "Post-Apocalyptic",
    "Superhero", "Martial Arts", "Heist", "Noir", "Dark Comedy", "Romantic Comedy",
    "Psychological Thriller", "Political Drama", "Legal Drama", "Medical Drama", "Coming-of-Age",
    "Road Movie", "Disaster", "Spy", "Survival", "Slasher", "Supernatural", "Folk Horror",
    "Mockumentary", "Satire", "Anime", "Courtroom", "Time Travel", "Zombie", "Found Footage",
    "Historical Epic", "Fairy Tale", "Buddy Comedy",
]
assert len(GENRES) == len(set(GENRES)) >= 50
genre_rows = [(i + 1, g) for i, g in enumerate(GENRES)]
write("genre", ["genre_id", "name"], genre_rows)

# ------------------------------------------------------------------ person
FIRST = ["Alex", "Maria", "John", "Anna", "Peter", "Elena", "David", "Sofia", "Michael", "Olga",
         "Daniel", "Laura", "Ivan", "Emma", "Thomas", "Nina", "Lucas", "Clara", "Viktor", "Irina",
         "Adam", "Julia", "Marco", "Eva", "Oscar", "Lena", "Samuel", "Alice", "Igor", "Mia",
         "Robert", "Sara", "Pavel", "Hannah", "Andre", "Katia", "Leo", "Vera", "Henry", "Zoe",
         "Max", "Dina", "Felix", "Tanya", "Jack", "Rita", "Boris", "Nora", "Ethan", "Lydia",
         "Carlos", "Mei", "Hiro", "Aisha", "Omar", "Priya", "Kenji", "Yuna", "Tariq", "Lina"]
LAST = ["Brown", "Ivanov", "Schmidt", "Rossi", "Dubois", "Novak", "Larsen", "Garcia", "Kim", "Tanaka",
        "Petrov", "Miller", "Silva", "Jansen", "Nowak", "Cohen", "Weber", "Moreau", "Lopez", "Fischer",
        "Costa", "Hansen", "Kovac", "Sokolov", "Murphy", "Bianchi", "Andersson", "Popov", "Reyes", "Clarke",
        "Volkov", "Keller", "Meyer", "Santos", "Kowalski", "Morozov", "Evans", "Berg", "Horvat", "Lindgren",
        "Fontaine", "Ortega", "Yamamoto", "Park", "Singh", "Haddad", "Nilsson", "Orlov", "Wright", "Duarte",
        "Stein", "Lebedev", "Hughes", "Marino", "Svensson", "Barros", "Kuznetsov", "Walsh", "Ricci", "Zielinski"]
combos = set()
while len(combos) < 150:
    combos.add((random.choice(FIRST), random.choice(LAST)))
combos = sorted(combos)
random.shuffle(combos)
person_rows = []
for i, (f, l) in enumerate(combos, 1):
    bd = None if random.random() < 0.10 else date(1940, 1, 1) + timedelta(days=random.randint(0, 62 * 365))
    person_rows.append((i, f"{f} {l}", bd.isoformat() if bd else None))
write("person", ["person_id", "full_name", "birth_date"], person_rows)

# ------------------------------------------------------------------ movie
ADJ = ["Last", "Silent", "Broken", "Hidden", "Golden", "Crimson", "Lonely", "Distant", "Frozen", "Burning",
       "Endless", "Forgotten", "Midnight", "Electric", "Hollow", "Wild", "Secret", "Falling", "Rising", "Iron",
       "Pale", "Scarlet", "Quiet", "Savage", "Neon", "Shattered", "Eternal", "Restless", "Velvet", "Bitter"]
NOUN = ["Horizon", "Garden", "Signal", "Harbor", "Kingdom", "Shadow", "Highway", "Orbit", "Mirror", "Echo",
        "Island", "Letter", "Empire", "River", "Machine", "Witness", "Frontier", "Lighthouse", "Carnival", "Archive",
        "Voyage", "Season", "Promise", "Tower", "Station", "Dream", "Storm", "Border", "Circus", "Prophecy",
        "Garrison", "Valley", "Heist", "Verdict", "Sanctuary", "Comet", "Labyrinth", "Reunion", "Fortress", "Lullaby"]
PATTERNS = ["The {a} {n}", "{a} {n}", "{n} of {n2}", "Beyond the {n}", "The {n} Protocol", "Return to {n}", "{a} {n} Blues"]
titles = set()
while len(titles) < 120:
    p = random.choice(PATTERNS)
    titles.add(p.format(a=random.choice(ADJ), n=random.choice(NOUN), n2=random.choice(NOUN)))
titles = sorted(titles)
random.shuffle(titles)

GENRE_BLURB = {
    "Action": "A former courier is forced back into the field when a convoy goes missing.",
    "Drama": "Three generations of one family face the sale of their last shared property.",
    "Comedy": "A mix-up at a wedding agency turns one weekend into a chain of absurd coincidences.",
    "Sci-Fi": "A research crew detects a signal that should not exist and has hours to decide what to do.",
    "Horror": "A night-shift worker realizes the building has more floors than the plan says.",
    "Thriller": "An auditor finds a ledger that predicts events before they happen.",
    "Romance": "Two translators meet at a conference and keep missing each other across three cities.",
    "Fantasy": "A cartographer discovers that her maps change the land they describe.",
    "Crime": "A retired detective reopens the one case that made his name.",
    "Documentary": "A year-long portrait of a small town that is about to disappear from the map.",
}
age_ratings = ["0+", "6+", "12+", "16+", "18+"]
movie_rows, movie_info = [], {}
for i, t in enumerate(titles, 1):
    year = wchoice(list(range(1975, 2027)), [1 + (y - 1975) ** 1.3 / 20 for y in range(1975, 2027)])
    dur = random.randint(78, 190)
    ar = wchoice(age_ratings, [8, 14, 28, 28, 22])
    movie_info[i] = {"year": year, "dur": dur, "age": int(ar.rstrip("+"))}
    movie_rows.append([i, t, None, year, dur, ar])
write_later_movie = movie_rows  # описание добавим после выбора жанров

# ------------------------------------------------------------------ movie_genre
popular = list(range(1, 21))
mg = set()
for m in range(1, 121):
    k = wchoice([1, 2, 3, 4], [25, 40, 25, 10])
    for _ in range(k):
        g = random.choice(popular) if random.random() < 0.7 else random.randint(1, len(GENRES))
        mg.add((m, g))
for g in range(1, len(GENRES) + 1):  # каждый жанр хотя бы у одного фильма
    if not any(x[1] == g for x in mg):
        mg.add((random.randint(1, 120), g))
mg = sorted(mg)
write("movie_genre", ["movie_id", "genre_id"], mg)

first_genre = {}
for m, g in mg:
    first_genre.setdefault(m, GENRES[g - 1])
for r in movie_rows:
    if random.random() < 0.05:
        r[2] = None
    else:
        base = GENRE_BLURB.get(first_genre[r[0]], "A story of choices, consequences and an unexpected ally.")
        r[2] = base
write("movie", ["movie_id", "title", "description", "release_year", "duration_min", "age_rating"], movie_rows)

# ------------------------------------------------------------------ movie_cast
directors, writers = range(1, 31), range(20, 51)
producers, composers, actors = range(40, 66), range(60, 76), range(50, 151)
CHARS = ["Detective", "Captain", "Doctor", "Professor", "Mechanic", "Courier", "Pilot", "Journalist",
         "Neighbor", "Stranger", "Inspector", "Engineer", "Bartender", "Student", "Smuggler", "Sheriff"]
SURN = ["Vale", "Stone", "Reed", "Hart", "Quinn", "Frost", "Blake", "Cross", "Hale", "Moss"]
cast = {}
for m in range(1, 121):
    d = random.choice(directors)
    cast[(m, d, "director")] = None
    if random.random() < 0.1:
        cast[(m, random.choice(directors), "director")] = None
    if random.random() < 0.3:  # режиссёр и сценарист одновременно (одна персона - две роли)
        cast[(m, d, "writer")] = None
    for _ in range(random.randint(1, 2)):
        cast[(m, random.choice(writers), "writer")] = None
    for _ in range(random.randint(1, 2)):
        cast[(m, random.choice(producers), "producer")] = None
    if random.random() < 0.8:
        cast[(m, random.choice(composers), "composer")] = None
    for _ in range(random.randint(4, 8)):
        cast[(m, random.choice(actors), "actor")] = f"{random.choice(CHARS)} {random.choice(SURN)}"
cast_rows = [(m, p, r, c) for (m, p, r), c in sorted(cast.items())]
write("movie_cast", ["movie_id", "person_id", "role", "character_name"], cast_rows)

# ------------------------------------------------------------------ users
DOMAINS = ["example.com", "mail.test", "demo.org", "stream.test", "inbox.example"]
user_rows, user_info = [], {}
cw = [12 if c[0] == "RU" else 8 if c[0] in ("US", "DE", "GB") else 3 if i < 40 else 1 for i, c in enumerate(COUNTRIES)]
for uid in range(1, 201):
    f, l = random.choice(FIRST), random.choice(LAST)
    cid = wchoice(list(range(1, len(COUNTRIES) + 1)), cw)
    bd = date(1960, 1, 1) + timedelta(days=random.randint(0, (date(2012, 6, 1) - date(1960, 1, 1)).days))
    reg = datetime(2023, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=random.randint(0, int((NOW - datetime(2023, 1, 1, tzinfo=timezone.utc)).total_seconds()) - 30 * 86400))
    email = f"{f.lower()}.{l.lower()}{uid}@{random.choice(DOMAINS)}"
    pw = hashlib.sha256(f"demo-password-{uid}".encode()).hexdigest()
    user_rows.append((uid, cid, email, pw, f"{f} {l[0]}.", bd.isoformat(), ts(reg)))
    user_info[uid] = {"birth": bd, "reg": reg}
write("users", ["user_id", "country_id", "email", "password_hash", "display_name", "birth_date", "registered_at"], user_rows)

# ------------------------------------------------------------------ subscription + payment
TIER_W = [4, 12, 6, 4, 18, 14, 18, 8, 6, 2]
DUR_W = [45, 15, 10, 20, 10]
sub_rows, pay_rows = [], []
sub_id = pay_id = 0
subs_by_user = {}
for uid in range(1, 201):
    if random.random() < 0.15:
        continue  # пользователь без подписок (пример для LEFT JOIN)
    start = user_info[uid]["reg"].date() + timedelta(days=random.randint(0, 14))
    for _ in range(wchoice([1, 2, 3, 4], [35, 30, 22, 13])):
        if start > TODAY - timedelta(days=1):
            break
        tier = wchoice(list(range(10)), TIER_W)
        dur = wchoice(list(range(5)), DUR_W)
        plan_id = tier * 5 + dur + 1
        end = add_months(start, plan_months[plan_id])
        if end > TODAY:
            status = "cancelled" if random.random() < 0.05 else "active"
        else:
            status = "cancelled" if random.random() < 0.10 else "expired"
        sub_id += 1
        sub_rows.append((sub_id, uid, plan_id, start.isoformat(), end.isoformat(), status))
        subs_by_user.setdefault(uid, []).append((sub_id, start, end))
        method = wchoice(["card", "paypal", "sbp", "apple_pay", "google_pay"], [45, 15, 20, 12, 8])
        paid = datetime(start.year, start.month, start.day, random.randint(6, 22), random.randint(0, 59), random.randint(0, 59), tzinfo=timezone.utc)
        reg_ts = user_info[uid]["reg"]
        paid = max(paid, reg_ts + timedelta(minutes=5))  # платёж не раньше регистрации
        if random.random() < 0.12:  # неудачная попытка перед успешной оплатой
            pay_id += 1
            failed_at = max(paid - timedelta(minutes=random.randint(2, 90)), reg_ts + timedelta(minutes=1))
            pay_rows.append((pay_id, sub_id, f"{plan_price[plan_id]:.2f}", ts(failed_at), method, "failed"))
        pay_id += 1
        if status == "cancelled" and random.random() < 0.4:
            pst = "refunded"
        elif status == "active" and end > TODAY and (TODAY - start).days < 2 and random.random() < 0.5:
            pst = "pending"
        else:
            pst = "success"
        pay_rows.append((pay_id, sub_id, f"{plan_price[plan_id]:.2f}", ts(paid), method, pst))
        if status in ("active",) and end > TODAY:
            break
        start = end + timedelta(days=random.choice([0, 0, 0, 1, 3, 10, 20]))
write("subscription", ["subscription_id", "user_id", "plan_id", "start_date", "end_date", "status"], sub_rows)
write("payment", ["payment_id", "subscription_id", "amount", "paid_at", "payment_method", "status"], pay_rows)

# ------------------------------------------------------------------ watch + review
def age_on(uid, d):
    b = user_info[uid]["birth"]
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day))


movie_ids = list(range(1, 121))
movie_w = [1 + random.random() * 6 for _ in movie_ids]  # у фильмов разная популярность
watch_rows, review_rows = [], []
watch_id = review_id = 0
reviewed = set()
TEXTS = {
    "high": ["Great pacing and a memorable cast.", "One of the best I have seen this year.", "Beautiful camera work, watched twice.",
             "Strong script, the ending works.", "Highly recommend to anyone who likes the genre."],
    "mid": ["Decent, though the middle drags a little.", "Good idea, uneven execution.", "Worth a watch on a quiet evening.",
            "Nice soundtrack, forgettable plot."],
    "low": ["Too long and predictable.", "Could not connect with the characters.", "Disappointing compared to the trailer."],
}
for uid, subs in subs_by_user.items():
    for sid, s_start, s_end in subs:
        last_day = min(s_end - timedelta(days=1), TODAY - timedelta(days=1))
        span = (last_day - s_start).days
        if span < 0:
            continue
        n = random.randint(1, min(20, span // 20 + 1))
        for _ in range(n):
            day = s_start + timedelta(days=random.randint(0, span))
            started = datetime(day.year, day.month, day.day, random.randint(7, 23), random.randint(0, 59), tzinfo=timezone.utc)
            started = max(started, user_info[uid]["reg"] + timedelta(minutes=10))  # просмотр не раньше регистрации
            age = age_on(uid, day)
            for _try in range(30):
                m = random.choices(movie_ids, weights=movie_w, k=1)[0]
                mi = movie_info[m]
                if mi["age"] <= age and mi["year"] <= day.year:
                    break
            else:
                continue
            total = mi["dur"] * 60
            if random.random() < 0.65:
                watched = random.randint(int(total * 0.92), total)
            else:
                watched = random.randint(int(total * 0.03), int(total * 0.85))
            finished = watched >= 0.9 * total
            watch_id += 1
            watch_rows.append((watch_id, uid, m, ts(started), watched, "true" if finished else "false"))
            if finished and (uid, m) not in reviewed and random.random() < 0.30:
                reviewed.add((uid, m))
                rating = wchoice(list(range(1, 11)), [2, 2, 3, 5, 9, 14, 22, 22, 14, 7])
                kind = "high" if rating >= 8 else "mid" if rating >= 5 else "low"
                text = None if random.random() < 0.3 else random.choice(TEXTS[kind])
                created = started + timedelta(seconds=watched) + timedelta(hours=random.randint(0, 48))
                if created > NOW:
                    created = NOW - timedelta(minutes=random.randint(1, 600))
                review_id += 1
                review_rows.append((review_id, uid, m, rating, text, ts(created)))
write("watch", ["watch_id", "user_id", "movie_id", "started_at", "watched_seconds", "is_finished"], watch_rows)
write("review", ["review_id", "user_id", "movie_id", "rating", "review_text", "created_at"], review_rows)
