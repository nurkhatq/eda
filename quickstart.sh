#!/bin/bash

# Скрипт быстрого старта системы Goszakup ETL

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Goszakup ETL System - Быстрый старт                   ║"
echo "║     ForteBank Hackathon 2024                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и повторите попытку."
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и повторите попытку."
    exit 1
fi

echo "✅ Docker и Docker Compose обнаружены"
echo ""

# Создание необходимых директорий
echo "📁 Создание директорий..."
mkdir -p logs data config
echo "✅ Директории созданы"
echo ""

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден, но это нормально (будут использованы значения по умолчанию)"
fi
echo ""

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров (если есть)..."
docker-compose down 2>/dev/null || true
echo ""

# Запуск сервисов
echo "🚀 Запуск сервисов..."
echo "   Это может занять несколько минут при первом запуске..."
docker-compose up -d

echo ""
echo "⏳ Ожидание запуска сервисов (30 секунд)..."
sleep 30

# Проверка статуса
echo ""
echo "📊 Статус контейнеров:"
docker-compose ps

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  Сервисы запущены!                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Веб-интерфейсы:"
echo "   • Airflow:  http://localhost:8080"
echo "     Логин: admin | Пароль: admin"
echo ""
echo "   • PgAdmin:  http://localhost:5050"
echo "     Email: admin@admin.com | Пароль: admin"
echo ""
echo "🗄️  Подключение к PostgreSQL:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: goszakup"
echo "   User: goszakup"
echo "   Password: goszakup123"
echo ""
echo "📝 Полезные команды:"
echo "   • make help          - Показать все доступные команды"
echo "   • make logs          - Показать логи"
echo "   • make test-api      - Протестировать API"
echo "   • make trigger-dag   - Запустить ETL вручную"
echo "   • make stats         - Статистика данных в БД"
echo "   • make down          - Остановить все сервисы"
echo ""
echo "📚 Документация: README.md"
echo ""
echo "🎯 Следующие шаги:"
echo "   1. Откройте Airflow UI: http://localhost:8080"
echo "   2. Найдите DAG 'goszakup_full_etl'"
echo "   3. Включите его и запустите"
echo "   4. Наблюдайте за процессом загрузки данных"
echo ""
echo "✨ Готово! Удачи на хакатоне! 🚀"
echo ""
