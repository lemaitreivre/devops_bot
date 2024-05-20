# Указываем базовый образ Python 3.10 на основе Alpine Linux
FROM python:3.10-alpine

# Копируем все файлы из текущей директории в директорию /app внутри контейнера
COPY . /app

# Устанавливаем /app как рабочую директорию
WORKDIR /app

# Обновляем pip до последней версии и устанавливаем зависимости из файла requirements.txt, без кеширования
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

# Задаем команду, которая будет выполнена при запуске контейнера, запуск бота
CMD ["python", "bot.py"]
