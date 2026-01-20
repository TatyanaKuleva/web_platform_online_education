Платворма Онлайн-Образование — Запуск через Docker Compose
Этот проект использует Docker Compose для запуска всех необходимых сервисов: Django (web), PostgreSQL (db), Redis, 
Celery worker и Celery beat.

Предварительные требования
- В корне проекта должен быть файл .env с необходимыми настройками (пример ниже)

1. Подготовка
- Склонируйте репозиторий 
git clone <https://github.com/TatyanaKuleva/web_platform_online_education.git>
- Создайте файл .env в корне проекта (если его нет) с таким содержанием (укажите свои значения):
STRIPE_SECRET_KEY=your_real_stripe_secret_key_here
DATABASE_URL=postgres://postgres:postgres@db:5432/online_education
REDIS_URL=redis://redis:6379
DJANGO_SETTINGS_MODULE=config.settings
- Скачайте скрипт ожидания базы (если используется в docker-compose):
curl -o wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
chmod +x wait-for-it.sh


2.Запуск проекта
- Выполните команду для сборки и запуска всех контейнеров:
docker-compose up --build
Эта команда построит образы и запустит все сервисы.
- Ваш Django-сервер будет доступен по адресу: http://localhost:8000


3. Проверка работоспособности сервисов
Web (Django)
- Перейдите по адресу http://localhost:8000
- Проверьте, что сервер запущен, и отображается ваш сайт или API.

PostgreSQL (db)
- Подключитесь к базе через psql:
docker exec -it online_education_db psql -U postgres -d online_education
- Выполните запрос, например:
SELECT 1;
Если запрос прошел успешно, база работает.

Redis
- Подключитесь к Redis командой:
docker exec -it online_education_redis redis-cli
- Выполните команду ping:
ping
- Если Redis отвечает PONG, он работает корректно.


Celery Worker
- Логи Celery выводятся в терминал, в котором запущен docker-compose up.
- Вы также можете подключиться к контейнеру Celery и проверить процессы:
docker exec -it online_education_celery bash
- Там можно запускать команды Celery (например, запускать задачи вручную для теста).


Celery Beat
- Автоматически планирует периодические задачи.
- Проверить работу можно через логи контейнера:
docker logs online_education_celery_beat



4. Остановка проекта
Для остановки всех контейнеров используйте:
docker-compose down



Полезные команды
- Сбилдить образы без запуска:
docker-compose build

- Запустить контейнеры в фоне (демоне):
docker-compose up -d

- Просмотр логов:
docker-compose logs -f

- Подключиться в терминал работающего контейнера, например web:
docker exec -it online-education bash


