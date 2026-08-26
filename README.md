# CRM ЖКУ

Внутренняя биллинговая CRM для начисления и перерасчёта услуг ЖКХ
(лицевые счета, тарифы, начисления, квитанции). Только для сотрудников —
бухгалтерии, паспортного стола, инженеров. Наниматели доступа не имеют.

Архитектура, модели данных и поэтапный план разработки — в [DESIGN.md](DESIGN.md).

## Стек

Django 5 + PostgreSQL + Celery/Redis (фоновые задачи и расписание) +
WeasyPrint (PDF-квитанции), развёртывание через Docker Compose.

## Быстрый старт

```bash
cp .env.example .env   # заполнить пароли/секреты
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

Admin доступен на `http://localhost/admin/`.

## Разработка без Docker

Нужны локально установленные и запущенные PostgreSQL и Redis (Celery-задачи
без Redis не запустятся, но `runserver`/`migrate` для них не требуются).

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

cp .env.example .env
# В .env обязательно замените POSTGRES_HOST=db на POSTGRES_HOST=localhost
# (значение "db" — это имя сервиса в docker-compose, вне Docker оно не
# резолвится) и создайте в PostgreSQL базу/пользователя с этими данными:
#   createdb crm && createuser crm --password

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
