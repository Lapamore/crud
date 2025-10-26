#!/bin/bash

# Скрипт для полного тестирования API
# Останавливается при первой ошибке
set -e

# --- Конфигурация ---
BASE_URL="http://localhost:8001/api"
EMAIL="testuser-$(date +%s)@example.com" # Уникальный email каждый раз
USERNAME="testuser-$(date +%s)"
PASSWORD="password123"

echo "--- Начинаем тестирование API по адресу $BASE_URL ---"
echo "Используем пользователя: $USERNAME, Email: $EMAIL"
echo ""

# --- 1. Регистрация ---
echo "1. Регистрация нового пользователя..."
curl -s -X 'POST' \
  "$BASE_URL/users" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{
  \"email\": \"$EMAIL\",
  \"username\": \"$USERNAME\",
  \"password\": \"$PASSWORD\"
}" > /dev/null # Скрываем вывод, так как он не нужен
echo "Успешно."
echo ""

# --- 2. Аутентификация и получение токена ---
echo "2. Вход в систему для получения токена..."
LOGIN_RESPONSE=$(curl -s -X 'POST' \
  "$BASE_URL/users/login" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d "username=$USERNAME&password=$PASSWORD")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r .access_token)

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Ошибка: Не удалось получить токен доступа!"
    echo "Ответ сервера: $LOGIN_RESPONSE"
    exit 1
fi
echo "Токен получен."
echo ""

# --- 3. Пользователь ---
echo "3. Получение данных текущего пользователя..."
curl -s -X 'GET' \
  "$BASE_URL/user" \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

echo "4. Обновление данных пользователя..."
curl -s -X 'PUT' \
  "$BASE_URL/user" \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
  "bio": "My new automated bio."
}' | jq .
echo ""

# --- 4. Статьи ---
echo "5. Создание новой статьи..."
ARTICLE_RESPONSE=$(curl -s -X 'POST' \
  "$BASE_URL/articles" \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Automated Test Article",
  "description": "This is a test.",
  "body": "This article was created by an automated script."
}')

SLUG=$(echo $ARTICLE_RESPONSE | jq -r .slug)

if [ "$SLUG" == "null" ] || [ -z "$SLUG" ]; then
    echo "Ошибка: Не удалось получить slug статьи!"
    echo "Ответ сервера: $ARTICLE_RESPONSE"
    exit 1
fi
echo "Статья создана со слагом: $SLUG"
echo ""

# --- 5. Комментарии ---
echo "6. Добавление комментария к статье..."
COMMENT_RESPONSE=$(curl -s -X 'POST' \
  "$BASE_URL/articles/$SLUG/comments" \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
  "body": "This is an automated comment!"
}')
echo "Комментарий добавлен."
echo ""

echo "7. Получение списка комментариев..."
COMMENTS_LIST=$(curl -s -X 'GET' \
  "$BASE_URL/articles/$SLUG/comments" \
  -H 'accept: application/json')

COMMENT_ID=$(echo $COMMENTS_LIST | jq -r '.[0].id')

if [ "$COMMENT_ID" == "null" ] || [ -z "$COMMENT_ID" ]; then
    echo "Ошибка: Не удалось получить ID комментария!"
    echo "Ответ сервера: $COMMENTS_LIST"
    exit 1
fi
echo "ID комментария для удаления: $COMMENT_ID"
echo ""

echo "8. Удаление комментария..."
curl -s -X 'DELETE' \
  "$BASE_URL/articles/$SLUG/comments/$COMMENT_ID" \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo "Комментарий удален."
echo ""

# --- 6. Очистка ---
echo "9. Удаление тестовой статьи..."
curl -s -X 'DELETE' \
  "$BASE_URL/articles/$SLUG" \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $TOKEN" > /dev/null
echo "Статья удалена."
echo ""

echo "--- Тестирование успешно завершено! ---"
