"""
DAG для ETL процесса загрузки данных из Goszakup API в PostgreSQL
Запускается ежедневно в 02:00
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os
import logging

# Добавляем путь к модулям
sys.path.insert(0, '/opt/airflow/src')

from goszakup_client import GoszakupAPIClient
from database import GoszakupDB, GoszakupETL

logger = logging.getLogger(__name__)

# Параметры подключения к БД из переменных окружения
DB_CONFIG = {
    'host': os.getenv('GOSZAKUP_DB_HOST', 'postgres-goszakup'),
    'port': int(os.getenv('GOSZAKUP_DB_PORT', 5432)),
    'database': os.getenv('GOSZAKUP_DB_NAME', 'goszakup'),
    'user': os.getenv('GOSZAKUP_DB_USER', 'goszakup'),
    'password': os.getenv('GOSZAKUP_DB_PASSWORD', 'goszakup123'),
}

# Параметры API
API_TOKEN = os.getenv('GOSZAKUP_API_TOKEN', None)
RETRY_COUNT = int(os.getenv('ETL_RETRY_COUNT', 3))
DELAY_SECONDS = int(os.getenv('ETL_DELAY_SECONDS', 1))

# Параметры DAG по умолчанию
default_args = {
    'owner': 'goszakup_etl',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Определение DAG
dag = DAG(
    'goszakup_full_etl',
    default_args=default_args,
    description='Полный ETL процесс для загрузки данных из Goszakup API',
    schedule_interval='0 2 * * *',  # Каждый день в 02:00
    catchup=False,
    tags=['goszakup', 'etl', 'procurement'],
)


def create_db_connection():
    """Создание подключения к БД"""
    db = GoszakupDB(**DB_CONFIG)
    db.connect()
    return db


def create_api_client():
    """Создание клиента API"""
    return GoszakupAPIClient(token=API_TOKEN, retry_count=RETRY_COUNT, delay=DELAY_SECONDS)


def check_db_connection(**kwargs):
    """Проверка подключения к БД"""
    logger.info("Проверка подключения к БД...")
    db = create_db_connection()
    try:
        logger.info("Подключение к БД успешно!")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        raise


def load_references(**kwargs):
    """Загрузка справочников"""
    logger.info("Начало загрузки справочников...")
    api = create_api_client()
    db = create_db_connection()

    try:
        etl = GoszakupETL(api, db)
        etl.load_references()
        logger.info("Справочники загружены успешно!")
    except Exception as e:
        logger.error(f"Ошибка при загрузке справочников: {e}")
        raise
    finally:
        db.close()


def load_subjects(**kwargs):
    """Загрузка участников"""
    logger.info("Начало загрузки участников...")
    api = create_api_client()
    db = create_db_connection()

    try:
        etl = GoszakupETL(api, db)
        etl.load_subjects()
        count = db.get_table_count('subjects')
        logger.info(f"Участников загружено: {count}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке участников: {e}")
        raise
    finally:
        db.close()


def load_rnu(**kwargs):
    """Загрузка реестра недобросовестных"""
    logger.info("Начало загрузки РНУ...")
    api = create_api_client()
    db = create_db_connection()

    try:
        etl = GoszakupETL(api, db)
        etl.load_rnu()
        count = db.get_table_count('rnu')
        logger.info(f"РНУ записей загружено: {count}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке РНУ: {e}")
        raise
    finally:
        db.close()


def load_plans(**kwargs):
    """Загрузка планов закупок"""
    logger.info("Начало загрузки планов...")
    api = create_api_client()
    db = create_db_connection()

    try:
        etl = GoszakupETL(api, db)
        etl.load_plans()
        count = db.get_table_count('plans')
        logger.info(f"Планов загружено: {count}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке планов: {e}")
        raise
    finally:
        db.close()


def load_announcements(**kwargs):
    """Загрузка объявлений"""
    logger.info("Начало загрузки объявлений...")
    api = create_api_client()
    db = create_db_connection()

    try:
        etl = GoszakupETL(api, db)
        etl.load_announcements()
        count = db.get_table_count('announcements')
        logger.info(f"Объявлений загружено: {count}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке объявлений: {e}")
        raise
    finally:
        db.close()


def load_applications(**kwargs):
    """Загрузка заявок поставщиков"""
    logger.info("Начало загрузки заявок...")
    api = create_api_client()
    db = create_db_connection()

    try:
        etl = GoszakupETL(api, db)
        etl.load_applications()
        count = db.get_table_count('applications')
        logger.info(f"Заявок загружено: {count}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке заявок: {e}")
        raise
    finally:
        db.close()


def load_lots(**kwargs):
    """Загрузка лотов"""
    logger.info("Начало загрузки лотов...")
    api = create_api_client()
    db = create_db_connection()

    try:
        etl = GoszakupETL(api, db)
        etl.load_lots()
        count = db.get_table_count('lots')
        logger.info(f"Лотов загружено: {count}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке лотов: {e}")
        raise
    finally:
        db.close()


def load_contracts(**kwargs):
    """Загрузка договоров"""
    logger.info("Начало загрузки договоров...")
    api = create_api_client()
    db = create_db_connection()

    try:
        etl = GoszakupETL(api, db)
        etl.load_contracts()
        count = db.get_table_count('contracts')
        logger.info(f"Договоров загружено: {count}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке договоров: {e}")
        raise
    finally:
        db.close()


def load_acts(**kwargs):
    """Загрузка актов"""
    logger.info("Начало загрузки актов...")
    api = create_api_client()
    db = create_db_connection()

    try:
        etl = GoszakupETL(api, db)
        etl.load_acts()
        count = db.get_table_count('acts')
        logger.info(f"Актов загружено: {count}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке актов: {e}")
        raise
    finally:
        db.close()


def load_payments(**kwargs):
    """Загрузка платежей"""
    logger.info("Начало загрузки платежей...")
    api = create_api_client()
    db = create_db_connection()

    try:
        etl = GoszakupETL(api, db)
        etl.load_payments()
        count = db.get_table_count('payments')
        logger.info(f"Платежей загружено: {count}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке платежей: {e}")
        raise
    finally:
        db.close()


def print_statistics(**kwargs):
    """Вывод статистики по загруженным данным"""
    logger.info("Сбор статистики...")
    db = create_db_connection()

    try:
        tables = [
            'subjects', 'rnu', 'plans', 'announcements',
            'applications', 'lots', 'contracts', 'acts', 'payments'
        ]

        stats = {}
        for table in tables:
            count = db.get_table_count(table)
            stats[table] = count
            logger.info(f"{table}: {count} записей")

        logger.info("=" * 50)
        logger.info("СТАТИСТИКА ЗАГРУЗКИ:")
        logger.info("=" * 50)
        for table, count in stats.items():
            logger.info(f"{table:20} : {count:10,}")
        logger.info("=" * 50)

        return stats
    finally:
        db.close()


# =================================================================
# ОПРЕДЕЛЕНИЕ ЗАДАЧ (TASKS)
# =================================================================

# Проверка подключения
task_check_db = PythonOperator(
    task_id='check_db_connection',
    python_callable=check_db_connection,
    dag=dag,
)

# Загрузка справочников (первыми!)
task_load_references = PythonOperator(
    task_id='load_references',
    python_callable=load_references,
    dag=dag,
)

# Загрузка основных данных
task_load_subjects = PythonOperator(
    task_id='load_subjects',
    python_callable=load_subjects,
    dag=dag,
)

task_load_rnu = PythonOperator(
    task_id='load_rnu',
    python_callable=load_rnu,
    dag=dag,
)

task_load_plans = PythonOperator(
    task_id='load_plans',
    python_callable=load_plans,
    dag=dag,
)

task_load_announcements = PythonOperator(
    task_id='load_announcements',
    python_callable=load_announcements,
    dag=dag,
)

task_load_applications = PythonOperator(
    task_id='load_applications',
    python_callable=load_applications,
    dag=dag,
)

task_load_lots = PythonOperator(
    task_id='load_lots',
    python_callable=load_lots,
    dag=dag,
)

task_load_contracts = PythonOperator(
    task_id='load_contracts',
    python_callable=load_contracts,
    dag=dag,
)

task_load_acts = PythonOperator(
    task_id='load_acts',
    python_callable=load_acts,
    dag=dag,
)

task_load_payments = PythonOperator(
    task_id='load_payments',
    python_callable=load_payments,
    dag=dag,
)

# Статистика
task_statistics = PythonOperator(
    task_id='print_statistics',
    python_callable=print_statistics,
    dag=dag,
)

# =================================================================
# ОПРЕДЕЛЕНИЕ ЗАВИСИМОСТЕЙ (DEPENDENCIES)
# =================================================================

# Проверка БД -> Справочники -> Остальные данные параллельно -> Статистика
task_check_db >> task_load_references

task_load_references >> [
    task_load_subjects,
    task_load_rnu,
    task_load_plans,
]

task_load_plans >> task_load_announcements
task_load_announcements >> [task_load_applications, task_load_lots]
task_load_lots >> task_load_contracts
task_load_contracts >> [task_load_acts, task_load_payments]

[task_load_subjects, task_load_rnu, task_load_acts, task_load_payments] >> task_statistics
