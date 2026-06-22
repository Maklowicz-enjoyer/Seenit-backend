
CREATE TYPE user_role  AS ENUM ('admin', 'user');
CREATE TYPE media_type AS ENUM ('movie', 'series');


CREATE TABLE users (
    id            SERIAL       PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100),
    role          user_role    NOT NULL DEFAULT 'user',
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE movies (
    id               SERIAL       PRIMARY KEY,
    title            VARCHAR(200) NOT NULL,
    year             INT,
    director         VARCHAR(150),
    genre            VARCHAR(100),
    description      TEXT,
    media_type       media_type   NOT NULL,
    duration_minutes INT,
    country          VARCHAR(100),
    avg_rating       FLOAT        NOT NULL DEFAULT 0,   -- liczy backend
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE watchlist (
    id         SERIAL      PRIMARY KEY,
    user_id    INT         NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    movie_id   INT         NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    watched    BOOLEAN     NOT NULL DEFAULT FALSE,
    added_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    watched_at TIMESTAMPTZ,
    CONSTRAINT uq_watchlist_user_movie UNIQUE (user_id, movie_id)
);


CREATE TABLE reviews (
    id         SERIAL      PRIMARY KEY,
    user_id    INT         NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    movie_id   INT         NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    rating     FLOAT       NOT NULL CHECK (rating >= 1 AND rating <= 10),
    content    TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_review_user_movie UNIQUE (user_id, movie_id)
);


CREATE INDEX idx_watchlist_user   ON watchlist (user_id);
CREATE INDEX idx_watchlist_movie  ON watchlist (movie_id);
CREATE INDEX idx_reviews_movie    ON reviews   (movie_id);
CREATE INDEX idx_reviews_user     ON reviews   (user_id);
CREATE INDEX idx_movies_title     ON movies    (title);  -- wyszukiwarka ?search=



INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@seenit.local', '$2b$12$4PGm7umCJOE6HzPwszSpTOzIo3mqLF0CMTb.bWUqiMB9BqbABXwSS', 'Administrator', 'admin'),
('kuba',  'kuba@seenit.local',  '$2b$12$/suywbpOK52Qm35uUfBuv.VtnVTQ4HbsvMvCskkEM7yE0byt0Et5S', 'Kuba Nowak',    'user'),
('ola',   'ola@seenit.local',   '$2b$12$XygSpW/XVoaGqs58LAdqn.CZ1eEcd6ZsEvP4UkDje4LXpoTJwB/rS', 'Ola Wisniewska','user');

INSERT INTO movies (title, year, director, genre, description, media_type, duration_minutes, country) VALUES
('Incepcja',        2010, 'Christopher Nolan', 'sci-fi',   'Złodziej kradnący sekrety z podświadomości.',        'movie',  148, 'USA'),
('Interstellar',    2014, 'Christopher Nolan', 'sci-fi',   'Podróż przez tunel czasoprzestrzenny.',              'movie',  169, 'USA'),
('Parasite',        2019, 'Bong Joon-ho',      'thriller', 'Uboga rodzina wkrada się do bogatego domu.',         'movie',  132, 'Korea'),
('Breaking Bad',    2008, 'Vince Gilligan',    'dramat',   'Nauczyciel chemii zostaje producentem narkotyków.',  'series', 49,  'USA'),
('Wiedzmin',        2019, 'Lauren S. Hissrich','fantasy',  'Losy Geralta z Rivii.',                              'series', 60,  'Polska'),
('Czarnobyl',       2019, 'Johan Renck',       'dramat',   'Rekonstrukcja katastrofy z 1986 roku.',              'series', 65,  'USA');

-- watchlista: (kuba=2, ola=3) ; filmy id 1..6
INSERT INTO watchlist (user_id, movie_id, watched, watched_at) VALUES
(2, 1, TRUE,  NOW() - INTERVAL '3 days'),
(2, 4, FALSE, NULL),
(2, 6, TRUE,  NOW() - INTERVAL '1 day'),
(3, 3, TRUE,  NOW() - INTERVAL '10 days'),
(3, 5, FALSE, NULL);

-- recenzje (rating 1..10, jedna na parę user+film)
INSERT INTO reviews (user_id, movie_id, rating, content) VALUES
(2, 1, 9.0,  'Genialna konstrukcja, trzyma w napięciu.'),
(3, 1, 8.5,  'Trzeba obejrzeć dwa razy.'),
(2, 6, 10.0, 'Najlepszy serial jaki widziałem.'),
(3, 3, 9.5,  'Zasłużony Oscar.'),
(2, 4, 9.0,  'Powolny start, ale warto.');


UPDATE movies m
SET avg_rating = sub.avg_r
FROM (
    SELECT movie_id, ROUND(AVG(rating)::numeric, 2) AS avg_r
    FROM reviews
    GROUP BY movie_id
) AS sub
WHERE m.id = sub.movie_id;
