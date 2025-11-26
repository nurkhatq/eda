"""
Модуль для работы с PostgreSQL базой данных
"""

import psycopg2
from psycopg2.extras import execute_values, Json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoszakupDB:
    """Класс для работы с БД Goszakup"""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """
        Инициализация подключения к БД

        Args:
            host: Хост БД
            port: Порт БД
            database: Имя БД
            user: Пользователь
            password: Пароль
        """
        self.conn_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.conn = None

    def connect(self):
        """Установка соединения с БД"""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            logger.info("Соединение с БД установлено")
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise

    def close(self):
        """Закрытие соединения"""
        if self.conn:
            self.conn.close()
            logger.info("Соединение с БД закрыто")

    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Выполнение SQL запроса"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Ошибка выполнения запроса: {e}")
            raise

    def insert_batch(self, table: str, data: List[Dict[str, Any]]):
        """
        Batch вставка данных

        Args:
            table: Имя таблицы
            data: Список словарей с данными
        """
        if not data:
            logger.warning(f"Нет данных для вставки в таблицу {table}")
            return

        # Получаем колонки из первой записи
        columns = list(data[0].keys())
        values = [[record.get(col) for col in columns] for record in data]

        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))

        query = f"""
            INSERT INTO {table} ({columns_str})
            VALUES %s
            ON CONFLICT DO NOTHING
        """

        try:
            with self.conn.cursor() as cursor:
                execute_values(cursor, query, values, template=f'({placeholders})')
                self.conn.commit()
                logger.info(f"Вставлено {len(data)} записей в таблицу {table}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Ошибка вставки в {table}: {e}")
            raise

    def insert_jsonb_batch(self, table: str, data: List[Dict[str, Any]]):
        """
        Batch вставка данных с JSONB полем

        Args:
            table: Имя таблицы
            data: Список словарей с данными
        """
        if not data:
            logger.warning(f"Нет данных для вставки в таблицу {table}")
            return

        query = f"""
            INSERT INTO {table} (data, created_at)
            VALUES %s
            ON CONFLICT DO NOTHING
        """

        values = [(Json(record), datetime.now()) for record in data]

        try:
            with self.conn.cursor() as cursor:
                execute_values(cursor, query, values)
                self.conn.commit()
                logger.info(f"Вставлено {len(data)} записей в таблицу {table}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Ошибка вставки в {table}: {e}")
            raise

    def upsert_batch(self, table: str, data: List[Dict[str, Any]], conflict_columns: List[str]):
        """
        Batch upsert (INSERT ... ON CONFLICT UPDATE)

        Args:
            table: Имя таблицы
            data: Список словарей с данными
            conflict_columns: Колонки для определения конфликта
        """
        if not data:
            logger.warning(f"Нет данных для upsert в таблицу {table}")
            return

        columns = list(data[0].keys())
        values = [[record.get(col) for col in columns] for record in data]

        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        conflict_str = ', '.join(conflict_columns)

        # UPDATE clause (все колонки кроме conflict)
        update_columns = [col for col in columns if col not in conflict_columns]
        update_str = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])

        query = f"""
            INSERT INTO {table} ({columns_str})
            VALUES %s
            ON CONFLICT ({conflict_str})
            DO UPDATE SET {update_str}
        """

        try:
            with self.conn.cursor() as cursor:
                execute_values(cursor, query, values, template=f'({placeholders})')
                self.conn.commit()
                logger.info(f"Upsert выполнен для {len(data)} записей в таблице {table}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Ошибка upsert в {table}: {e}")
            raise

    def table_exists(self, table_name: str) -> bool:
        """Проверка существования таблицы"""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            );
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (table_name,))
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Ошибка проверки существования таблицы {table_name}: {e}")
            return False

    def get_table_count(self, table_name: str) -> int:
        """Получение количества записей в таблице"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Ошибка получения количества записей в {table_name}: {e}")
            return 0

    def truncate_table(self, table_name: str):
        """Очистка таблицы"""
        query = f"TRUNCATE TABLE {table_name} CASCADE"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                self.conn.commit()
                logger.info(f"Таблица {table_name} очищена")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Ошибка очистки таблицы {table_name}: {e}")
            raise


class GoszakupETL:
    """ETL процесс для загрузки данных из API в БД"""

    def __init__(self, api_client, db: GoszakupDB):
        """
        Args:
            api_client: Экземпляр GoszakupAPIClient
            db: Экземпляр GoszakupDB
        """
        self.api = api_client
        self.db = db

    def load_references(self):
        """Загрузка всех справочников"""
        logger.info("Начало загрузки справочников...")

        references = {
            'ref_lots_status': self.api.get_ref_lots_status,
            'ref_trade_methods': self.api.get_ref_trade_methods,
            'ref_units': self.api.get_ref_units,
            'ref_months': self.api.get_ref_months,
            'ref_pln_point_status': self.api.get_ref_pln_point_status,
            'ref_subject_type': self.api.get_ref_subject_type,
            'ref_finsource': self.api.get_ref_finsource,
            'ref_abp': self.api.get_ref_abp,
            'ref_point_type': self.api.get_ref_point_type,
            'ref_kato': self.api.get_ref_kato,
            'ref_countries': self.api.get_ref_countries,
            'ref_ekrb': self.api.get_ref_ekrb,
            'ref_fkrb_program': self.api.get_ref_fkrb_program,
            'ref_fkrb_subprogram': self.api.get_ref_fkrb_subprogram,
            'ref_justification': self.api.get_ref_justification,
            'ref_amendment_agreem_type': self.api.get_ref_amendment_agreem_type,
            'ref_amendm_agreem_justif': self.api.get_ref_amendm_agreem_justif,
            'ref_budget_type': self.api.get_ref_budget_type,
            'ref_type_trade': self.api.get_ref_type_trade,
            'ref_buy_status': self.api.get_ref_buy_status,
            'ref_po_st': self.api.get_ref_po_st,
            'ref_comm_roles': self.api.get_ref_comm_roles,
            'ref_contract_status': self.api.get_ref_contract_status,
            'ref_contract_agr_form': self.api.get_ref_contract_agr_form,
            'ref_contract_year_type': self.api.get_ref_contract_year_type,
            'ref_currency': self.api.get_ref_currency,
            'ref_contract_cancel': self.api.get_ref_contract_cancel,
            'ref_contract_type': self.api.get_ref_contract_type,
            'ref_reason': self.api.get_ref_reason,
            'ref_buy_lot_reject_reason': self.api.get_ref_buy_lot_reject_reason,
        }

        for table_name, api_method in references.items():
            try:
                logger.info(f"Загрузка {table_name}...")
                data = api_method()
                if data:
                    self.db.insert_jsonb_batch(table_name, data)
                else:
                    logger.warning(f"Нет данных для {table_name}")
            except Exception as e:
                logger.error(f"Ошибка загрузки {table_name}: {e}")

        logger.info("Загрузка справочников завершена")

    def load_subjects(self):
        """Загрузка участников"""
        logger.info("Начало загрузки участников...")
        try:
            subjects = self.api.get_subjects_all()
            if subjects:
                self.db.insert_jsonb_batch('subjects', subjects)
            logger.info("Загрузка участников завершена")
        except Exception as e:
            logger.error(f"Ошибка загрузки участников: {e}")

    def load_rnu(self):
        """Загрузка реестра недобросовестных"""
        logger.info("Начало загрузки РНУ...")
        try:
            rnu = self.api.get_rnu()
            if rnu:
                self.db.insert_jsonb_batch('rnu', rnu)
            logger.info("Загрузка РНУ завершена")
        except Exception as e:
            logger.error(f"Ошибка загрузки РНУ: {e}")

    def load_plans(self):
        """Загрузка планов закупок"""
        logger.info("Начало загрузки планов...")
        try:
            plans = self.api.get_plans_all()
            if plans:
                self.db.insert_jsonb_batch('plans', plans)
            logger.info("Загрузка планов завершена")
        except Exception as e:
            logger.error(f"Ошибка загрузки планов: {e}")

    def load_announcements(self):
        """Загрузка объявлений"""
        logger.info("Начало загрузки объявлений...")
        try:
            announcements = self.api.get_trd_buy_all()
            if announcements:
                self.db.insert_jsonb_batch('announcements', announcements)
            logger.info("Загрузка объявлений завершена")
        except Exception as e:
            logger.error(f"Ошибка загрузки объявлений: {e}")

    def load_applications(self):
        """Загрузка заявок поставщиков"""
        logger.info("Начало загрузки заявок...")
        try:
            applications = self.api.get_trd_app()
            if applications:
                self.db.insert_jsonb_batch('applications', applications)
            logger.info("Загрузка заявок завершена")
        except Exception as e:
            logger.error(f"Ошибка загрузки заявок: {e}")

    def load_lots(self):
        """Загрузка лотов"""
        logger.info("Начало загрузки лотов...")
        try:
            lots = self.api.get_lots()
            if lots:
                self.db.insert_jsonb_batch('lots', lots)
            logger.info("Загрузка лотов завершена")
        except Exception as e:
            logger.error(f"Ошибка загрузки лотов: {e}")

    def load_contracts(self):
        """Загрузка договоров"""
        logger.info("Начало загрузки договоров...")
        try:
            contracts = self.api.get_contracts_all()
            if contracts:
                self.db.insert_jsonb_batch('contracts', contracts)
            logger.info("Загрузка договоров завершена")
        except Exception as e:
            logger.error(f"Ошибка загрузки договоров: {e}")

    def load_acts(self):
        """Загрузка актов"""
        logger.info("Начало загрузки актов...")
        try:
            acts = self.api.get_acts()
            if acts:
                self.db.insert_jsonb_batch('acts', acts)
            logger.info("Загрузка актов завершена")
        except Exception as e:
            logger.error(f"Ошибка загрузки актов: {e}")

    def load_payments(self):
        """Загрузка платежей"""
        logger.info("Начало загрузки платежей...")
        try:
            payments = self.api.get_treasury_payments()
            if payments:
                self.db.insert_jsonb_batch('payments', payments)
            logger.info("Загрузка платежей завершена")
        except Exception as e:
            logger.error(f"Ошибка загрузки платежей: {e}")

    def run_full_etl(self):
        """Запуск полного ETL процесса"""
        logger.info("=" * 50)
        logger.info("НАЧАЛО ПОЛНОГО ETL ПРОЦЕССА")
        logger.info("=" * 50)

        try:
            # 1. Справочники (их загружаем первыми)
            self.load_references()

            # 2. Участники
            self.load_subjects()

            # 3. РНУ
            self.load_rnu()

            # 4. Планы
            self.load_plans()

            # 5. Объявления
            self.load_announcements()

            # 6. Заявки
            self.load_applications()

            # 7. Лоты
            self.load_lots()

            # 8. Договоры
            self.load_contracts()

            # 9. Акты
            self.load_acts()

            # 10. Платежи
            self.load_payments()

            logger.info("=" * 50)
            logger.info("ETL ПРОЦЕСС ЗАВЕРШЕН УСПЕШНО")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"Критическая ошибка в ETL процессе: {e}")
            raise
