-- Создание базы данных онлайн-кинотеатра (PostgreSQL 13+).
-- Выполнять в psql под пользователем с правом CREATE DATABASE.

CREATE DATABASE cinema
    ENCODING 'UTF8'
    TEMPLATE template0;

-- Переключение на созданную БД (команда psql, не SQL):
\c cinema
