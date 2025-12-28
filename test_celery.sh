#!/bin/bash

set -e

# Базовый URL Nginx
BASE_URL="http://localhost"

echo "🔍 DEBUG: Checking routes..."

# 1. Пробуем получить токен (разные варианты путей)

echo "--- Attempt 1: POST /api/users/login ---"
curl -v -X POST "$BASE_URL/api/users/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test&password=test" 2>&1 | grep "< HTTP"

echo "--- Attempt 2: POST /users/api/users/login (через Swagger path) ---"
curl -v -X POST "$BASE_URL/users/api/users/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test&password=test" 2>&1 | grep "< HTTP"

echo "--- Attempt 3: POST /login (напрямую в корень users service, если proxy убирает путь) ---"
# Это вряд ли сработает через ваш конфиг nginx, но для проверки
# Нам нужно изменить запрос, предполагая ошибку в nginx config.

# Функция регистрации с выводом ошибки
register_and_log() {
    local username=$1
    local email=$2
    local password=$3
    
    echo "Registering $username..."
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/users" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$username\",\"email\":\"$email\",\"password\":\"$password\"}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    echo "HTTP: $http_code"
    echo "Body: $body"
    
    if [[ "$http_code" == "404" ]]; then
        echo "❌ 404 Error! Route not found."
        echo "Try checking: docker logs users-api"
        return 1
    fi
}

# Тестовые данные
AuthorName="author_$(shuf -i 1000-9999 -n 1)"
AuthorPass="pass123"
AuthorEmail="$AuthorName@example.com"

# Запуск теста регистрации
register_and_log "$AuthorName" "$AuthorEmail" "$AuthorPass"
