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

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# запустить локальный PostgreSQL и Redis, задать переменные из .env.example
python manage.py migrate
python manage.py runserver
```

## Полезные команды

```bash
python manage.py generate_monthly_charges --period 2026-09
python manage.py generate_receipts --period 2026-09
```
