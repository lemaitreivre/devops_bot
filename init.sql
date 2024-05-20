CREATE DATABASE DB_DATABASE;

CREATE USER DB_USER WITH REPLICATION ENCRYPTED PASSWORD 'DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE DB_DATABASE TO DB_USER;

CREATE USER DB_REPL_USER WITH REPLICATION ENCRYPTED PASSWORD 'DB_REPL_PASSWORD';

\connect DB_DATABASE;

CREATE TABLE IF NOT EXISTS emails(
	id SERIAL PRIMARY KEY,
	email VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS phones(
	id SERIAL PRIMARY KEY,
	phone VARCHAR(20) UNIQUE
);

INSERT INTO emails (email) VALUES ('testemail1@mail.com'),('testemail2@test.com');

INSERT INTO phones (phone) VALUES ('+77777777777'), ('+71231231231');
