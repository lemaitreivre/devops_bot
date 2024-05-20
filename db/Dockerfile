# Базовый образ PostgreSQL:latest
FROM postgres:latest

# Копируем файл инициализации в контейнер
COPY init.sql /docker-entrypoint-initdb.d/init.sql

# Устанавливаем необходимые пакеты для замены переменных в init.sql
RUN apt-get update && apt-get install -y sed gettext-base && rm -rf /var/lib/apt/lists/*

# Определяем переменные для подстановки в init.sql
ARG DB_REPL_USER
ARG DB_REPL_PASSWORD
ARG DB_DATABASE
ARG DB_PORT

# Создаем каталог для архива WAL и устанавливаем права
RUN mkdir -p /var/lib/postgresql/data/pg_archive/ \
    && chown postgres:postgres /var/lib/postgresql/data/pg_archive/

# Выполняем замену переменных в init.sql и сохраняем результат в том же файле
RUN sed -i "s/\${DB_REPL_USER}/${DB_REPL_USER}/g" /docker-entrypoint-initdb.d/init.sql \
    && sed -i "s/\${DB_REPL_PASSWORD}/${DB_REPL_PASSWORD}/g" /docker-entrypoint-initdb.d/init.sql \
    && sed -i "s/\${DB_DATABASE}/${DB_DATABASE}/g" /docker-entrypoint-initdb.d/init.sql \
    && sed -i "s/\${DB_PORT}/${DB_PORT}/g" /docker-entrypoint-initdb.d/init.sql

# Обновляем конфигурацию PostgreSQL
RUN echo "listen_addresses = '*'" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "port = ${DB_PORT}" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "archive_mode = on" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "archive_command = 'mkdir -p /var/lib/postgresql/data/pg_archive/ && cp %p /var/lib/postgresql/data/pg_archive/%f'" >> /var/lib/postgresql/data/postgresql.conf.sample \
    && echo "log_destination = 'stderr'" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "logging_collector = on" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "log_directory = '/var/log/postgresql/'" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "log_filename = 'postgresql.log'" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "max_wal_senders=10" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "wal_level=replica" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "wal_log_hints = on" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "hot_standby=on" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "max_replication_slots=10" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "hot_standby_feedback=on" >> /usr/share/postgresql/postgresql.conf.sample \
    && echo "log_replication_commands=on" >> /usr/share/postgresql/postgresql.conf.sample


# Открываем порт для PostgreSQL
EXPOSE $DB_PORT
