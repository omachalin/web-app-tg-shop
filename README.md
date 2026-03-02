# TG WebApp Shop (Django + Telegram Bot)

Веб-приложение магазина с интеграцией **Telegram Mini App** и ботом для авторизованного доступа.

## Стек

- Python 3.11+
- Django
- PostgreSQL
- MinIO / S3 (`django-storages`, `django-minio-backend`)
- Pillow
- CKEditor
- pyTelegramBotAPI (`telebot`)
- Telegram WebApp

## 📦 Функциональность

### Каталог

- Список товаров
- Фильтрация:
  - категории
  - название
  - теги
- Сортировка
- Пагинация (`offset/limit`)
- AJAX поиск (`/search-product/`)

### Карточка товара

- Превью
- Галерея изображений
- Теги
- RichText описание
- Контактные данные

### Файлы

- Модель `Attachment`
- Хранение:
  - Public bucket
  - Private bucket
- Автоматическая конвертация изображений:
  - JPEG / PNG → WEBP

### Telegram Bot

- Проверка доступа через таблицу `TgUserAllow`
- Кнопка открытия Mini App
- Webhook endpoint `/telegram_webhook/`


```bash
git clone <repo_url>
cd <project>
