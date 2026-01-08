# Лабораторная работа №4: SAGA Choreography

## Цель работы

Реализация паттерна SAGA Choreography для публикации постов с модерацией, генерацией превью и уведомлениями подписчиков.

## Архитектура

### Жизненный цикл поста (статусы)

```
DRAFT → PENDING_PUBLISH → PUBLISHED
                       ↘ REJECTED
                       ↘ ERROR
```

| Статус | Описание |
|--------|----------|
| `DRAFT` | Черновик (по умолчанию при создании) |
| `PENDING_PUBLISH` | Автор запросил публикацию, идёт модерация/обработка |
| `PUBLISHED` | Пост опубликован, подписчики уведомлены |
| `REJECTED` | Модерация отклонила пост |
| `ERROR` | Произошла техническая ошибка при обработке |

### Поток задач SAGA

```
┌─────────────────┐
│  POST /publish  │  (Пользователь)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  post.moderate  │  (Moderation Worker)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
approved   rejected
    │         │
    ▼         ▼
┌─────────────────┐    ┌─────────────────┐
│post.generate_   │    │  POST /reject   │
│   preview       │    │  (компенсация)  │
└────────┬────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│  post.publish   │  (Publish Worker)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  post.notify    │  (Notification Worker)
└─────────────────┘
```

### Обработка ошибок и DLQ

- Все задачи имеют **3-5 попыток** с экспоненциальным backoff
- После исчерпания попыток задача попадает в **DLQ (Dead Letter Queue)**
- **DLQ Consumer** выполняет компенсирующие действия:
  - `post.moderate` → статус `REJECTED`
  - `post.generate_preview` → статус `ERROR`
  - `post.publish` → статус `ERROR`
  - `post.notify` → только логирование (пост уже опубликован)

### Идемпотентность

Все воркеры идемпотентны:
- Используется Redis для хранения ключей дедупликации
- Проверяется текущий статус поста перед операцией
- Повторные вызовы не приводят к дублированию действий

## Система внутренних API-ключей

### Архитектура авторизации

| Тип запроса | Заголовок | Доступ |
|-------------|-----------|--------|
| Пользовательский | `Authorization: Bearer <JWT>` | Публичные эндпоинты |
| Внутренний (service-to-service) | `X-API-Key: <key>` | `/api/internal/*` |

### Внутренние эндпоинты

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/api/internal/posts/{id}` | GET | Получение поста |
| `/api/internal/posts/{id}/reject` | POST | Отклонение поста |
| `/api/internal/posts/{id}/preview` | PUT | Обновление preview_url |
| `/api/internal/posts/{id}/publish` | POST | Публикация поста |
| `/api/internal/posts/{id}/error` | POST | Установка статуса ERROR |
| `/api/internal/init-keys` | POST | Инициализация API-ключей |

## Запуск

### 1. Запуск всех сервисов

```bash
docker-compose up -d --build
```

### 2. Применение миграций

```bash
# Backend миграции
docker exec backend alembic upgrade head

# Users миграции (если нужно)
docker exec users-api alembic upgrade head
```

### 3. Инициализация API-ключей

```bash
curl -X POST http://localhost/api/internal/init-keys
```

Ответ содержит API-ключи для воркеров. Скопируйте один из ключей и обновите `worker/.env`:

```env
internal_api_key=<скопированный_ключ>
```

### 4. Перезапуск воркеров

```bash
docker-compose restart worker dlq-worker
```

## Тестирование

### Запуск тестового скрипта

```bash
./test_saga.sh
```

### Ручное тестирование

#### 1. Регистрация пользователя

```bash
curl -X POST http://localhost/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "author@test.com",
    "username": "author",
    "password": "password123"
  }'
```

#### 2. Логин

```bash
curl -X POST http://localhost/api/users/login \
  -d "username=author&password=password123"
```

#### 3. Создание статьи (DRAFT)

```bash
curl -X POST http://localhost/api/articles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Article",
    "description": "Test description",
    "body": "Test body content"
  }'
```

#### 4. Публикация статьи (запуск SAGA)

```bash
curl -X POST http://localhost/api/articles/{article_id}/publish \
  -H "Authorization: Bearer <token>"
```

#### 5. Проверка статуса

```bash
curl http://localhost/api/articles/{slug}
```

### Просмотр логов воркеров

```bash
# Основной воркер
docker logs -f worker

# DLQ воркер
docker logs -f dlq-worker
```

## Структура файлов

```
backend/
├── src/
│   ├── models/
│   │   ├── ArticleStatus.py      # Enum статусов
│   │   └── ApiKey.py             # Модель API-ключей
│   ├── core/
│   │   └── deps.py               # Авторизация (JWT + API-ключи)
│   └── modules/
│       ├── articles/
│       │   ├── commands/
│       │   │   └── PublishArticleCommand.py
│       │   └── handlers/
│       │       └── PublishArticleHandler.py
│       └── internal/
│           └── api/
│               ├── ApiKeysRoutes.py
│               └── InternalArticlesRoutes.py
└── migrations/
    └── versions/
        └── b2c3d4e5f6g7_add_saga_fields_and_api_keys.py

worker/
├── services/
│   ├── RunTasks.py               # Точка входа Celery
│   └── SagaTasks.py              # Все SAGA воркеры
└── config.py                     # Конфигурация
```

## Acceptance Criteria ✓

- [x] Эндпоинт `POST /posts/{id}/publish` запускает SAGA
- [x] Moderation Worker: random approve/reject (80% approve)
- [x] Preview Worker: генерация фейкового URL превью
- [x] Publish Worker: переход в PUBLISHED + задача notify
- [x] Notification Worker: рассылка push-уведомлений
- [x] DLQ с компенсирующими действиями
- [x] Ретраи с экспоненциальным backoff
- [x] Идемпотентность всех операций
- [x] Система внутренних API-ключей
- [x] Внутренние эндпоинты защищены от пользовательских JWT
