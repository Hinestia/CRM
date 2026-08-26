# CRM ЖКУ

Внутренняя биллинговая CRM для начисления и перерасчёта услуг ЖКХ
(лицевые счета, тарифы, начисления, квитанции). Только для сотрудников —
бухгалтерии, паспортного стола, инженеров. Наниматели доступа не имеют.

Архитектура, модели данных и поэтапный план разработки — в [DESIGN.md](DESIGN.md).

## Стек

Django 5 + PostgreSQL + Celery/Redis (фоновые задачи и расписание) +
WeasyPrint (PDF-квитанции). Web/Redis/Celery/Nginx — в Docker Compose;
**PostgreSQL — нативно на хосте** (см. ниже), общий для нескольких проектов
на сервере и не зависящий от жизненного цикла `docker compose`.

## PostgreSQL на хосте

Ставится один раз, отдельно от `docker compose up`/`down` этого проекта.

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
```

Создать базу и пользователя (значения должны совпадать с `.env`):

```bash
sudo -u postgres psql -c "CREATE USER crm WITH PASSWORD 'сюда-свой-пароль';"
sudo -u postgres psql -c "CREATE DATABASE crm OWNER crm;"
```

Контейнеры (`web`, `celery_worker`, `celery_beat`) достают Postgres с хоста
через `host.docker.internal` — по умолчанию нативный PostgreSQL слушает
только `localhost` и не пускает подключения из Docker-сети. Нужно открыть
это явно:

```bash
# Найти файлы конфигурации (версия у вас может отличаться от 16)
sudo -u postgres psql -c "SHOW config_file;"
sudo -u postgres psql -c "SHOW hba_file;"
```

В `postgresql.conf`:
```
listen_addresses = 'localhost,172.17.0.1'
```
(`172.17.0.1` — стандартный адрес хоста в дефолтной Docker-сети `bridge`;
если у вас Docker создаёт сети с другими подсетями — проще и надёжнее
`listen_addresses = '*'`, доступ извне сервера при этом всё равно
закрывается файрволом, см. ниже).

В `pg_hba.conf` добавить строку (доступ только из приватных Docker-подсетей):
```
host    crm    crm    172.16.0.0/12    scram-sha-256
```

Перезапустить:
```bash
sudo systemctl restart postgresql
sudo systemctl enable postgresql
```

**Обязательно закрыть порт 5432 от внешнего мира** — Postgres нужен только
локально/из Docker-сети этого сервера, не из интернета:
```bash
sudo ufw deny 5432/tcp
```
(если `ufw` не включён — просто не пробрасывайте порт 5432 никуда и не
открывайте его на роутере).

## Быстрый старт (Docker Compose: web/redis/celery/nginx)

```bash
cp .env.example .env   # заполнить POSTGRES_PASSWORD и остальные секреты
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Admin доступен на `http://localhost/admin/`.

## Разработка без Docker вообще

Нужен запущенный локальный PostgreSQL (см. выше, без шага с
`host.docker.internal`/`pg_hba.conf` — раз всё на одной машине без Docker,
достаточно `listen_addresses = 'localhost'` по умолчанию) и Redis, если
нужны Celery-задачи (`runserver`/`migrate` без Redis работают).

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

cp .env.example .env
# Замените POSTGRES_HOST=host.docker.internal на POSTGRES_HOST=localhost

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Файл `.env` подхватывается автоматически (`config/settings.py` вызывает
`load_dotenv()`) — отдельно экспортировать переменные не нужно.

## Полезные команды

```bash
python manage.py generate_monthly_charges --period 2026-09
python manage.py generate_receipts --period 2026-09
```
