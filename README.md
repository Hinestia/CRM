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
по фиксированному IP `172.28.0.1` — это шлюз Docker-сети compose-проекта,
явно закреплённый в `docker-compose.yml` (`networks.default.ipam`), а не
`host.docker.internal`: в некоторых конфигурациях Docker резолвит это имя
в адрес дефолтной сети `docker0`, а не в шлюз сети конкретного проекта —
пакеты в этом случае уходят не туда и просто зависают вместо явной ошибки.
Фиксированный IP снимает эту неоднозначность полностью.

По умолчанию нативный PostgreSQL слушает только `localhost` и не пускает
подключения из Docker-сети. Нужно открыть это явно:

```bash
# Найти файлы конфигурации (версия у вас может отличаться от 16)
sudo -u postgres psql -c "SHOW config_file;"
sudo -u postgres psql -c "SHOW hba_file;"
```

В `postgresql.conf`:
```
listen_addresses = 'localhost,172.28.0.1'
```

В `pg_hba.conf` добавить строку (доступ только из приватных Docker-подсетей,
`172.16.0.0/12` покрывает и `172.28.0.0/24`, и `docker0`, и подсети других
compose-проектов на этом сервере):
```
host    crm    crm    172.16.0.0/12    scram-sha-256
```

Перезапустить:
```bash
sudo systemctl restart postgresql
sudo systemctl enable postgresql
```

**Обязательно открыть порт 5432 только для Docker-подсетей, не для всего
мира** — по умолчанию `ufw` (если включён) молча дропает всё, что не
разрешено явно, что выглядит как зависание, а не понятная ошибка:
```bash
sudo ufw allow from 172.16.0.0/12 to any port 5432 proto tcp
```
(если `ufw` не включён — просто не пробрасывайте порт 5432 никуда и не
открывайте его на роутере).

## Быстрый старт (Docker Compose: web/redis/celery/nginx)

```bash
cp .env.example .env   # заполнить POSTGRES_PASSWORD и остальные секреты
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Рабочий интерфейс сотрудника — `http://localhost/` (лицевые счета, начисления,
квитанции, должники и т.д.). Django admin (`http://localhost/admin/`)
остаётся доступен отдельно — как резервный доступ к редким справочникам.

## Разработка без Docker вообще

Нужен запущенный локальный PostgreSQL (см. выше, без шага с
`pg_hba.conf`/фиксированным IP — раз всё на одной машине без Docker,
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
# Замените POSTGRES_HOST=172.28.0.1 на POSTGRES_HOST=localhost

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
