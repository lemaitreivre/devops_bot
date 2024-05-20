-- СОЗДАЕМ ПОЛЬЗОВАТЕЛЯ ДЛЯ РЕПЛИКАЦИИ
CREATE USER ${DB_REPL_USER} WITH REPLICATION LOGIN PASSWORD '${DB_REPL_PASSWORD}';

-- ПОДКЛЮЧЕНИЕ К БД
\connect ${DB_DATABASE};

--СОЗДАНИЕ ТАБЛИЦЫ С EMAILS
CREATE TABLE IF NOT EXISTS emails(
	id SERIAL PRIMARY KEY,
	email VARCHAR(255) UNIQUE
);

-- СОЗДАНИЕ ТАБЛИЦЫ С ТЕЛЕФОНАМИ
CREATE TABLE IF NOT EXISTS phones(
	id SERIAL PRIMARY KEY,
	phone VARCHAR(20) UNIQUE
);

--ВСТАВКА В EMAILS
INSERT INTO emails (email) VALUES ('testemail1@mail.com'),('testemail2@test.com');

--ВСТАВКА В PHONES
INSERT INTO phones (phone) VALUES ('+77777777777'), ('+71231231231');
