#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

BASE_URL="http://localhost"
RANDOM_ID=$((1 + RANDOM % 10000))

echo -e "${CYAN}=== Запуск полного теста Лабораторной работы №3 ===${NC}\n"

# 1. Регистрация Автора
echo -e "${YELLOW}[1/7] Регистрация Автора...${NC}"
AUTHOR_EMAIL="author_${RANDOM_ID}@test.com"
AUTHOR_NAME="Author_${RANDOM_ID}"
AUTHOR_DATA=$(curl -s -X POST "$BASE_URL/api/users" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$AUTHOR_NAME\", \"email\": \"$AUTHOR_EMAIL\", \"password\": \"pass123\"}")

AUTHOR_ID=$(echo $AUTHOR_DATA | jq '.id')
echo -e "Автор зарегистрирован. ID: $AUTHOR_ID"

# 2. Логин Автора для получения токена
AUTHOR_TOKEN=$(curl -s -X POST "$BASE_URL/api/users/login" \
  -d "username=$AUTHOR_NAME&password=pass123" | jq -r '.access_token')
echo -e "Токен Автора получен."

# 3. Регистрация Подписчика
echo -e "\n${YELLOW}[2/7] Регистрация Подписчика...${NC}"
SUB_EMAIL="sub_${RANDOM_ID}@test.com"
SUB_NAME="Sub_${RANDOM_ID}"
SUB_DATA=$(curl -s -X POST "$BASE_URL/api/users" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$SUB_NAME\", \"email\": \"$SUB_EMAIL\", \"password\": \"pass123\"}")

SUB_ID=$(echo $SUB_DATA | jq '.id')
SUB_TOKEN=$(curl -s -X POST "$BASE_URL/api/users/login" \
  -d "username=$SUB_NAME&password=pass123" | jq -r '.access_token')
echo -e "Подписчик зарегистрирован (ID: $SUB_ID) и залогинен."

# 4. Установка ключа уведомлений (PUT /users/me/subscription-key)
echo -e "\n${YELLOW}[3/7] Установка subscription_key для Подписчика...${NC}"
TEST_KEY="super-secret-push-key-${RANDOM_ID}"
KEY_RESP=$(curl -s -w "%{http_code}" -X PUT "$BASE_URL/api/users/me/subscription-key" \
  -H "Authorization: Bearer $SUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"subscription_key\": \"$TEST_KEY\"}")

HTTP_CODE="${KEY_RESP: -3}"
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}Ключ успешно установлен (200 OK)${NC}"
else
    echo -e "${RED}Ошибка установки ключа: $HTTP_CODE${NC}"
    exit 1
fi

# 5. Подписка (POST /users/subscribe)
echo -e "\n${YELLOW}[4/7] Подписка: Подписчик -> Автор...${NC}"
SUB_RESP=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/api/users/subscribe" \
  -H "Authorization: Bearer $SUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"target_user_id\": $AUTHOR_ID}")

HTTP_CODE="${SUB_RESP: -3}"
if [ "$HTTP_CODE" == "204" ] || [ "$HTTP_CODE" == "201" ]; then
    echo -e "${GREEN}Подписка оформлена (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}Ошибка подписки: $HTTP_CODE${NC}"
    exit 1
fi

# 6. Публикация поста (Триггер Celery задачи)
echo -e "\n${YELLOW}[5/7] Публикация поста Автором (Триггер уведомлений)...${NC}"
POST_TITLE="New Post ${RANDOM_ID}"
ARTICLE_DATA=$(curl -s -X POST "$BASE_URL/api/articles" \
  -H "Authorization: Bearer $AUTHOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"$POST_TITLE\", \"description\": \"Desc\", \"body\": \"Full Body Text\", \"tagList\": [\"lab3\"]}")

ARTICLE_ID=$(echo $ARTICLE_DATA | jq '.id')

if [ "$ARTICLE_ID" != "null" ]; then
    echo -e "${GREEN}Пост создан! ID: $ARTICLE_ID${NC}"
else
    echo -e "${RED}Ошибка создания поста! Ответ: $ARTICLE_DATA${NC}"
    exit 1
fi

# 7. Проверка работы воркера
echo -e "\n${YELLOW}[6/7] Ожидание обработки задачи воркером (5 сек)...${NC}"
sleep 5

echo -e "${CYAN}=== ПРОВЕРКА ЛОГОВ ВОРКЕРА ===${NC}"
WORKER_LOGS=$(docker logs worker --tail 20)

if echo "$WORKER_LOGS" | grep -q "Processing notification for author_id=$AUTHOR_ID"; then
    echo -e "${GREEN}✔ Воркер поймал задачу для автора $AUTHOR_ID${NC}"
else
    echo -e "${RED}✘ Воркер не получал задачу! Проверь Celery и Redis.${NC}"
fi

if echo "$WORKER_LOGS" | grep -q "Notification sent to subscriber $SUB_ID"; then
    echo -e "${GREEN}✔ Уведомление успешно отправлено подписчику $SUB_ID${NC}"
else
    echo -e "${RED}✘ Уведомление не отправлено. Проверь логи воркера: docker logs worker${NC}"
fi

# 8. Финальная проверка ограничений (длина заголовка)
echo -e "\n${YELLOW}[7/7] Проверка ограничения длины заголовка (по требованиям лабы < 10 симв)...${NC}"
if echo "$WORKER_LOGS" | grep -q "выпустил новый пост: ${POST_TITLE:0:10}..."; then
    echo -e "${GREEN}✔ Длина заголовка в уведомлении обрезана правильно.${NC}"
else
    echo -e "${YELLOW}⚠ Проверь формат сообщения вручную в логах воркера.${NC}"
fi

echo -e "\n${CYAN}=== Тест завершен ===${NC}"