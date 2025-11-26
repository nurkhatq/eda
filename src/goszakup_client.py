"""
Клиент для работы с API goszakup.gov.kz
Поддерживает все 74 эндпоинта
"""

import requests
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoszakupAPIClient:
    """Клиент для работы с API goszakup.gov.kz"""

    BASE_URL = "https://ows.goszakup.gov.kz"

    def __init__(self, token: Optional[str] = None, retry_count: int = 3, delay: int = 1):
        """
        Инициализация клиента

        Args:
            token: API токен (если требуется)
            retry_count: Количество попыток при ошибке
            delay: Задержка между запросами в секундах
        """
        self.token = token
        self.retry_count = retry_count
        self.delay = delay
        self.session = requests.Session()

        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                     json_data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Выполнение HTTP запроса с повторными попытками

        Args:
            method: HTTP метод (GET, POST)
            endpoint: Путь эндпоинта
            params: Query параметры
            json_data: JSON данные для POST

        Returns:
            Ответ в виде словаря или None при ошибке
        """
        url = f"{self.BASE_URL}{endpoint}"

        for attempt in range(self.retry_count):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=30)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=json_data, timeout=30)
                else:
                    logger.error(f"Неподдерживаемый HTTP метод: {method}")
                    return None

                response.raise_for_status()
                time.sleep(self.delay)  # Задержка между запросами

                return response.json()

            except requests.exceptions.RequestException as e:
                logger.warning(f"Попытка {attempt + 1}/{self.retry_count} не удалась для {endpoint}: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)  # Экспоненциальная задержка
                else:
                    logger.error(f"Все попытки исчерпаны для {endpoint}")
                    return None

    def _paginate(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Получение всех страниц данных с пагинацией

        Args:
            endpoint: Путь эндпоинта
            params: Query параметры

        Returns:
            Список всех элементов со всех страниц
        """
        all_items = []
        next_page = None

        while True:
            if next_page:
                # Используем URL следующей страницы
                current_endpoint = next_page.replace(self.BASE_URL, '')
                response = self._make_request('GET', current_endpoint)
            else:
                response = self._make_request('GET', endpoint, params=params)

            if not response:
                break

            items = response.get('items', [])
            all_items.extend(items)

            logger.info(f"Получено {len(items)} записей с {endpoint}, всего: {len(all_items)}")

            # Проверяем наличие следующей страницы
            next_page = response.get('next_page')
            if not next_page or next_page == '':
                break

        return all_items

    # ========== ЖУРНАЛ ИЗМЕНЕНИЙ ==========

    def get_journal(self, date_from: str, date_to: str) -> List[Dict]:
        """Получение списка измененных объектов"""
        params = {'date_from': date_from, 'date_to': date_to}
        return self._paginate('/v3/journal', params=params)

    # ========== РЕЕСТР УЧАСТНИКОВ ==========

    def get_subjects(self) -> List[Dict]:
        """Получение списка компаний участников"""
        return self._paginate('/v3/subject')

    def get_subjects_all(self) -> List[Dict]:
        """Получение полного списка участников"""
        return self._paginate('/v3/subject/all')

    def get_subject_by_biin(self, biin: str) -> Optional[Dict]:
        """Поиск участника по БИН/ИИН"""
        return self._make_request('GET', f'/v3/subject/biin/{biin}')

    def get_subject_by_id(self, subject_id: int) -> Optional[Dict]:
        """Поиск участника по ИД"""
        return self._make_request('GET', f'/v3/subject/{subject_id}')

    def get_subject_addresses(self, biin: str) -> List[Dict]:
        """Получение адресов компании"""
        response = self._make_request('GET', f'/v3/subject/biin/{biin}/address')
        return response.get('items', []) if response else []

    def get_subject_employees(self, biin: str) -> List[Dict]:
        """Получение сотрудников компании"""
        response = self._make_request('GET', f'/v3/subject/biin/{biin}/employees')
        return response.get('items', []) if response else []

    # ========== РНУ (РЕЕСТР НЕДОБРОСОВЕСТНЫХ) ==========

    def get_rnu(self) -> List[Dict]:
        """Реестр недобросовестных поставщиков"""
        return self._paginate('/v3/rnu')

    def get_rnu_by_biin(self, biin: str) -> List[Dict]:
        """Расширенный реестр РНУ по БИН/ИИН"""
        response = self._make_request('GET', f'/v3/rnu/{biin}')
        return response.get('items', []) if response else []

    # ========== ПЛАНЫ ЗАКУПОК ==========

    def get_plans(self) -> List[Dict]:
        """Реестр заказчиков"""
        return self._paginate('/v3/plans')

    def get_plans_by_bin(self, bin_num: str) -> List[Dict]:
        """Реестр пунктов плана по БИН заказчика"""
        return self._paginate(f'/v3/plans/{bin_num}')

    def get_plan_by_id(self, plan_id: int) -> Optional[Dict]:
        """Получение одного пункта плана"""
        return self._make_request('GET', f'/v3/plans/view/{plan_id}')

    def get_plans_all(self) -> List[Dict]:
        """Реестр пунктов плана (все)"""
        return self._paginate('/v3/plans/all')

    def get_plans_kato(self) -> List[Dict]:
        """Реестр мест поставки"""
        return self._paginate('/v3/plans/kato')

    def get_plans_spec(self) -> List[Dict]:
        """Реестр специфик"""
        return self._paginate('/v3/plans/spec')

    def get_plans_deleted(self) -> List[Dict]:
        """Список снятых с публикации пунктов плана"""
        return self._paginate('/v2/plans/deleted')

    # ========== ОБЪЯВЛЕНИЯ ==========

    def get_trd_buy(self) -> List[Dict]:
        """Получение списка объявлений"""
        return self._paginate('/v3/trd-buy')

    def get_trd_buy_all(self) -> List[Dict]:
        """Получение полного списка объявлений"""
        return self._paginate('/v3/trd-buy/all')

    def get_trd_buy_by_bin(self, bin_num: str) -> List[Dict]:
        """Поиск объявлений по БИН организатора"""
        return self._paginate(f'/v3/trd-buy/bin/{bin_num}')

    def get_trd_buy_by_number(self, number: str) -> Optional[Dict]:
        """Объявление детально по номеру объявления"""
        return self._make_request('GET', f'/v3/trd-buy/number-anno/{number}')

    def get_trd_buy_by_id(self, buy_id: int) -> Optional[Dict]:
        """Объявление детально по ИД"""
        return self._make_request('GET', f'/v3/trd-buy/{buy_id}')

    def get_trd_buy_commission(self, buy_id: int) -> List[Dict]:
        """Конкурсная комиссия"""
        response = self._make_request('GET', f'/v3/trd-buy/{buy_id}/commission')
        return response.get('items', []) if response else []

    def get_trd_buy_pause(self, buy_id: int) -> Optional[Dict]:
        """Информация о приостановлении объявления"""
        return self._make_request('GET', f'/v3/trd-buy/{buy_id}/pause')

    def get_trd_buy_cancel(self, buy_id: int) -> Optional[Dict]:
        """Информация об отмене закупки по решению суда"""
        return self._make_request('GET', f'/v3/trd-buy/{buy_id}/cancel')

    # ========== ЗАЯВКИ ПОСТАВЩИКОВ ==========

    def get_trd_app(self) -> List[Dict]:
        """Получение списка заявок поставщиков"""
        return self._paginate('/v3/trd-app')

    # ========== ЛОТЫ ==========

    def get_lots(self) -> List[Dict]:
        """Реестр лотов"""
        return self._paginate('/v3/lots')

    def get_lots_by_number(self, number: str) -> List[Dict]:
        """Поиск лотов по номеру объявления"""
        return self._paginate(f'/v3/lots/number-anno/{number}')

    def get_lots_by_bin(self, bin_num: str) -> List[Dict]:
        """Поиск лотов по БИН заказчика"""
        return self._paginate(f'/v3/lots/bin/{bin_num}')

    def get_lot_by_id(self, lot_id: int) -> Optional[Dict]:
        """Лот детально"""
        return self._make_request('GET', f'/v3/lots/{lot_id}')

    # ========== ДОГОВОРЫ ==========

    def get_contracts(self) -> List[Dict]:
        """Реестр договоров"""
        return self._paginate('/v3/contract')

    def get_contracts_all(self) -> List[Dict]:
        """Полная информация по договорам"""
        return self._paginate('/v3/contract/all')

    def get_contracts_by_number_anno(self, number: str) -> List[Dict]:
        """Поиск договоров по номеру объявления"""
        return self._paginate(f'/v3/contract/number-anno/{number}')

    def get_contracts_by_supplier(self, biin: str) -> List[Dict]:
        """Поиск договоров по БИН/ИИН поставщика"""
        return self._paginate(f'/v3/contract/supplier/{biin}')

    def get_contracts_by_customer(self, bin_num: str) -> List[Dict]:
        """Поиск договоров по БИН заказчика"""
        return self._paginate(f'/v3/contract/customer/{bin_num}')

    def get_contract_by_number(self, number: str) -> Optional[Dict]:
        """Детальная информация договора по номеру"""
        params = {'number': number}
        return self._make_request('GET', '/v3/contract/number/', params=params)

    def get_contract_by_sys_number(self, number: str) -> Optional[Dict]:
        """Детальная информация договора по системному номеру"""
        params = {'number': number}
        return self._make_request('GET', '/v3/contract/number-sys/', params=params)

    def get_contract_by_id(self, contract_id: int) -> Optional[Dict]:
        """Детальная информация договора по ИД"""
        return self._make_request('GET', f'/v3/contract/{contract_id}')

    def get_contract_units(self, contract_id: int) -> List[Dict]:
        """Предметы договора"""
        response = self._make_request('GET', f'/v3/contract/{contract_id}/units')
        return response.get('items', []) if response else []

    # ========== АКТЫ ==========

    def get_acts(self) -> List[Dict]:
        """Реестр электронных актов"""
        return self._paginate('/v3/acts')

    def get_act_by_id(self, act_id: int) -> Optional[Dict]:
        """Акт детально"""
        return self._make_request('GET', f'/v3/acts/{act_id}')

    # ========== ПЛАТЕЖИ ==========

    def get_treasury_payments(self) -> List[Dict]:
        """Получение полного списка платежей"""
        return self._paginate('/v3/treasury-pay')

    def get_treasury_payments_by_contract(self, contract_id: int) -> List[Dict]:
        """Получение списка платежей по договору"""
        return self._paginate(f'/v3/treasury-pay/{contract_id}')

    # ========== СПРАВОЧНИКИ ==========

    def get_ref_lots_status(self) -> List[Dict]:
        """Статусы лотов"""
        return self._paginate('/v3/refs/ref_lots_status')

    def get_ref_trade_methods(self) -> List[Dict]:
        """Способ закупки"""
        return self._paginate('/v3/refs/ref_trade_methods')

    def get_ref_units(self) -> List[Dict]:
        """МКЕЙ"""
        return self._paginate('/v3/refs/ref_units')

    def get_ref_months(self) -> List[Dict]:
        """Месяца"""
        return self._paginate('/v3/refs/ref_months')

    def get_ref_pln_point_status(self) -> List[Dict]:
        """Статусы пунктов планов"""
        return self._paginate('/v3/refs/ref_pln_point_status')

    def get_ref_subject_type(self) -> List[Dict]:
        """Вид предмета закупки"""
        return self._paginate('/v3/refs/ref_subject_type')

    def get_ref_finsource(self) -> List[Dict]:
        """Источник финансирования"""
        return self._paginate('/v3/refs/ref_finsource')

    def get_ref_abp(self) -> List[Dict]:
        """Администратор бюджетной программы"""
        return self._paginate('/v3/refs/ref_abp')

    def get_ref_point_type(self) -> List[Dict]:
        """Тип пункта плана"""
        return self._paginate('/v3/refs/ref_point_type')

    def get_ref_kato(self) -> List[Dict]:
        """КАТО"""
        return self._paginate('/v3/refs/ref_kato')

    def get_ref_countries(self) -> List[Dict]:
        """Страны"""
        return self._paginate('/v3/refs/ref_countries')

    def get_ref_ekrb(self) -> List[Dict]:
        """Справочник специфик"""
        return self._paginate('/v3/refs/ref_ekrb')

    def get_ref_fkrb_program(self) -> List[Dict]:
        """Справочник программ ФКР"""
        return self._paginate('/v3/refs/ref_fkrb_program')

    def get_ref_fkrb_subprogram(self) -> List[Dict]:
        """Справочник подпрограмм ФКР"""
        return self._paginate('/v3/refs/ref_fkrb_subprogram')

    def get_ref_justification(self) -> List[Dict]:
        """Обоснование применения способа закупки"""
        return self._paginate('/v3/refs/ref_justification')

    def get_ref_amendment_agreem_type(self) -> List[Dict]:
        """Вид дополнительного соглашения"""
        return self._paginate('/v3/refs/ref_amendment_agreem_type')

    def get_ref_amendm_agreem_justif(self) -> List[Dict]:
        """Основания создания дополнительного соглашения"""
        return self._paginate('/v3/refs/ref_amendm_agreem_justif')

    def get_ref_budget_type(self) -> List[Dict]:
        """Вид бюджета"""
        return self._paginate('/v3/refs/ref_budget_type')

    def get_ref_type_trade(self) -> List[Dict]:
        """Тип закупки"""
        return self._paginate('/v3/refs/ref_type_trade')

    def get_ref_buy_status(self) -> List[Dict]:
        """Статус объявления"""
        return self._paginate('/v3/refs/ref_buy_status')

    def get_ref_po_st(self) -> List[Dict]:
        """Статусы ценовых предложений"""
        return self._paginate('/v3/refs/ref_po_st')

    def get_ref_comm_roles(self) -> List[Dict]:
        """Роль члена комиссии"""
        return self._paginate('/v3/refs/ref_comm_roles')

    def get_ref_contract_status(self) -> List[Dict]:
        """Статус договора"""
        return self._paginate('/v3/refs/ref_contract_status')

    def get_ref_contract_agr_form(self) -> List[Dict]:
        """Справочник форм заключения договора"""
        return self._paginate('/v3/refs/ref_contract_agr_form')

    def get_ref_contract_year_type(self) -> List[Dict]:
        """Тип договора (однолетний/многолетний)"""
        return self._paginate('/v3/refs/ref_contract_year_type')

    def get_ref_currency(self) -> List[Dict]:
        """Справочник валют"""
        return self._paginate('/v3/refs/ref_currency')

    def get_ref_contract_cancel(self) -> List[Dict]:
        """Справочник статей для расторжения договора"""
        return self._paginate('/v3/refs/ref_contract_cancel')

    def get_ref_contract_type(self) -> List[Dict]:
        """Справочник типов договора"""
        return self._paginate('/v3/refs/ref_contract_type')

    def get_ref_reason(self) -> List[Dict]:
        """Справочник причин внесения в РНУ"""
        return self._paginate('/v3/refs/ref_reason')

    def get_ref_buy_lot_reject_reason(self) -> List[Dict]:
        """Список причин по которым не состоялся аукцион по лоту"""
        return self._paginate('/v3/refs/ref_buy_lot_reject_reason')


if __name__ == '__main__':
    # Пример использования
    client = GoszakupAPIClient()

    # Получаем справочники
    print("Получение справочников...")
    trade_methods = client.get_ref_trade_methods()
    print(f"Способы закупки: {len(trade_methods)}")

    # Получаем участников
    print("\nПолучение участников...")
    subjects = client.get_subjects()
    print(f"Участники: {len(subjects)}")
