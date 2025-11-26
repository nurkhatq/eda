.PHONY: help build up down restart logs clean test-api db-cli airflow-cli stats

help:
	@echo "Goszakup ETL System - Команды управления"
	@echo ""
	@echo "Основные команды:"
	@echo "  make up          - Запустить все сервисы"
	@echo "  make down        - Остановить все сервисы"
	@echo "  make restart     - Перезапустить все сервисы"
	@echo "  make logs        - Показать логи всех сервисов"
	@echo "  make clean       - Остановить и удалить все данные"
	@echo ""
	@echo "Тестирование:"
	@echo "  make test-api    - Протестировать API эндпоинты"
	@echo ""
	@echo "База данных:"
	@echo "  make db-cli      - Открыть psql консоль"
	@echo "  make db-init     - Переинициализировать схему БД"
	@echo "  make stats       - Показать статистику данных в БД"
	@echo ""
	@echo "Airflow:"
	@echo "  make airflow-cli - Открыть Airflow CLI"
	@echo "  make trigger-dag - Запустить ETL вручную"
	@echo ""
	@echo "Веб-интерфейсы:"
	@echo "  Airflow:  http://localhost:8080 (admin/admin)"
	@echo "  PgAdmin:  http://localhost:5050 (admin@admin.com/admin)"

# Сборка и запуск
build:
	docker-compose build

up:
	@echo "Запуск сервисов..."
	mkdir -p logs data
	docker-compose up -d
	@echo ""
	@echo "✅ Сервисы запущены!"
	@echo ""
	@echo "Веб-интерфейсы:"
	@echo "  Airflow:  http://localhost:8080 (admin/admin)"
	@echo "  PgAdmin:  http://localhost:5050 (admin@admin.com/admin)"

down:
	@echo "Остановка сервисов..."
	docker-compose down
	@echo "✅ Сервисы остановлены"

restart:
	@echo "Перезапуск сервисов..."
	docker-compose restart
	@echo "✅ Сервисы перезапущены"

# Логи
logs:
	docker-compose logs -f

logs-airflow:
	docker-compose logs -f airflow-scheduler airflow-webserver

logs-db:
	docker-compose logs -f postgres-goszakup

# Очистка
clean:
	@echo "⚠️  ВНИМАНИЕ: Это удалит все данные!"
	@read -p "Продолжить? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		rm -rf logs/* data/*; \
		echo "✅ Все данные удалены"; \
	else \
		echo "Отменено"; \
	fi

# Тестирование API
test-api:
	@echo "Запуск тестирования API..."
	docker exec -it goszakup_airflow_webserver python /opt/airflow/src/test_api.py

# База данных
db-cli:
	@echo "Подключение к PostgreSQL..."
	docker exec -it goszakup_postgres_data psql -U goszakup -d goszakup

db-init:
	@echo "Переинициализация схемы БД..."
	docker exec -i goszakup_postgres_data psql -U goszakup -d goszakup < sql/init_schema.sql
	@echo "✅ Схема БД переинициализирована"

stats:
	@echo "Статистика данных в БД:"
	@docker exec -it goszakup_postgres_data psql -U goszakup -d goszakup -c "\
		SELECT \
			'subjects' as table_name, COUNT(*) as count FROM subjects \
		UNION ALL SELECT 'rnu', COUNT(*) FROM rnu \
		UNION ALL SELECT 'plans', COUNT(*) FROM plans \
		UNION ALL SELECT 'announcements', COUNT(*) FROM announcements \
		UNION ALL SELECT 'applications', COUNT(*) FROM applications \
		UNION ALL SELECT 'lots', COUNT(*) FROM lots \
		UNION ALL SELECT 'contracts', COUNT(*) FROM contracts \
		UNION ALL SELECT 'acts', COUNT(*) FROM acts \
		UNION ALL SELECT 'payments', COUNT(*) FROM payments;"

# Airflow
airflow-cli:
	@echo "Открытие Airflow CLI..."
	docker exec -it goszakup_airflow_scheduler bash

trigger-dag:
	@echo "Запуск ETL процесса..."
	docker exec -it goszakup_airflow_scheduler airflow dags trigger goszakup_full_etl
	@echo "✅ DAG запущен! Откройте http://localhost:8080 для просмотра прогресса"

list-dags:
	docker exec -it goszakup_airflow_scheduler airflow dags list

# Проверка статуса
status:
	@echo "Статус контейнеров:"
	@docker-compose ps

# Установка зависимостей в контейнер
install-deps:
	docker exec -it goszakup_airflow_webserver pip install -r /opt/airflow/requirements.txt
