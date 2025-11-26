#!/usr/bin/env python3
"""
Скрипт для быстрого тестирования API Goszakup
Проверяет доступность всех эндпоинтов
"""

import sys
from goszakup_client import GoszakupAPIClient
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_api_endpoints():
    """Тестирование основных эндпоинтов API"""

    client = GoszakupAPIClient(delay=2)  # Увеличенная задержка для тестирования

    tests = [
        # Название теста, функция, ожидается ли результат
        ("Справочник: Способы закупки", client.get_ref_trade_methods, True),
        ("Справочник: Статусы объявлений", client.get_ref_buy_status, True),
        ("Справочник: Статусы договоров", client.get_ref_contract_status, True),
        ("Справочник: Единицы измерения", client.get_ref_units, True),
        ("Справочник: КАТО", client.get_ref_kato, True),
        ("Реестр участников", client.get_subjects, True),
        ("Планы закупок: Заказчики", client.get_plans, True),
        ("Объявления о закупках", client.get_trd_buy, True),
        ("Лоты", client.get_lots, True),
        ("Договоры", client.get_contracts, True),
        ("РНУ (недобросовестные)", client.get_rnu, False),  # Может быть пустым
        ("Акты", client.get_acts, False),  # Может быть пустым
    ]

    results = {
        'success': 0,
        'failed': 0,
        'empty': 0
    }

    print("=" * 80)
    print("ТЕСТИРОВАНИЕ API GOSZAKUP.GOV.KZ")
    print("=" * 80)
    print()

    for i, (name, func, expect_data) in enumerate(tests, 1):
        print(f"[{i}/{len(tests)}] Тестирование: {name}...")

        try:
            data = func()

            if data is None:
                print(f"    ❌ ОШИБКА: Не удалось получить данные")
                results['failed'] += 1
                continue

            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict):
                count = 1
            else:
                count = 0

            if count == 0 and expect_data:
                print(f"    ⚠️  ПУСТО: Данные не найдены (ожидались)")
                results['empty'] += 1
            elif count == 0:
                print(f"    ℹ️  ПУСТО: Данные не найдены (норма)")
                results['success'] += 1
            else:
                print(f"    ✅ OK: Получено {count:,} записей")
                results['success'] += 1

                # Показываем пример данных
                if isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    keys = list(first_item.keys())[:3]  # Первые 3 ключа
                    print(f"       Пример полей: {', '.join(keys)}")

        except Exception as e:
            print(f"    ❌ ОШИБКА: {str(e)}")
            results['failed'] += 1

        print()

    # Итоговая статистика
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 80)
    print(f"✅ Успешно:     {results['success']}")
    print(f"⚠️  Пустые:      {results['empty']}")
    print(f"❌ Ошибки:      {results['failed']}")
    print(f"📊 Всего тестов: {len(tests)}")
    print("=" * 80)

    success_rate = (results['success'] / len(tests)) * 100
    print(f"\nПроцент успеха: {success_rate:.1f}%")

    if results['failed'] == 0:
        print("\n🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print(f"\n⚠️  Обнаружены проблемы в {results['failed']} тестах")
        return 1


def test_specific_endpoints():
    """Тестирование специфичных эндпоинтов с параметрами"""

    client = GoszakupAPIClient(delay=2)

    print("\n" + "=" * 80)
    print("ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ")
    print("=" * 80)
    print()

    # Тест поиска по БИН (используем известный БИН Минфина)
    print("Тест: Поиск участника по БИН...")
    try:
        subject = client.get_subject_by_biin("201040000013")
        if subject:
            print(f"    ✅ Найден: {subject.get('name_ru', 'N/A')}")
        else:
            print("    ⚠️  Участник не найден")
    except Exception as e:
        print(f"    ❌ Ошибка: {e}")

    print()

    # Тест получения полного списка участников
    print("Тест: Полный список участников...")
    try:
        subjects = client.get_subjects_all()
        print(f"    ✅ Получено участников: {len(subjects):,}")
    except Exception as e:
        print(f"    ❌ Ошибка: {e}")

    print()


def main():
    """Главная функция"""

    print("\n🔍 Запуск тестирования API Goszakup\n")

    # Основные тесты
    exit_code = test_api_endpoints()

    # Дополнительные тесты
    test_specific_endpoints()

    print("\n✨ Тестирование завершено!\n")

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
