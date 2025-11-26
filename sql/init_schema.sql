-- Схема БД для системы сбора данных Goszakup
-- Используем JSONB для гибкого хранения данных

-- Удаление существующих таблиц
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS acts CASCADE;
DROP TABLE IF EXISTS contracts CASCADE;
DROP TABLE IF EXISTS lots CASCADE;
DROP TABLE IF EXISTS applications CASCADE;
DROP TABLE IF EXISTS announcements CASCADE;
DROP TABLE IF EXISTS plans CASCADE;
DROP TABLE IF EXISTS rnu CASCADE;
DROP TABLE IF EXISTS subjects CASCADE;
DROP TABLE IF EXISTS journal CASCADE;

-- Справочники
DROP TABLE IF EXISTS ref_lots_status CASCADE;
DROP TABLE IF EXISTS ref_trade_methods CASCADE;
DROP TABLE IF EXISTS ref_units CASCADE;
DROP TABLE IF EXISTS ref_months CASCADE;
DROP TABLE IF EXISTS ref_pln_point_status CASCADE;
DROP TABLE IF EXISTS ref_subject_type CASCADE;
DROP TABLE IF EXISTS ref_finsource CASCADE;
DROP TABLE IF EXISTS ref_abp CASCADE;
DROP TABLE IF EXISTS ref_point_type CASCADE;
DROP TABLE IF EXISTS ref_kato CASCADE;
DROP TABLE IF EXISTS ref_countries CASCADE;
DROP TABLE IF EXISTS ref_ekrb CASCADE;
DROP TABLE IF EXISTS ref_fkrb_program CASCADE;
DROP TABLE IF EXISTS ref_fkrb_subprogram CASCADE;
DROP TABLE IF EXISTS ref_justification CASCADE;
DROP TABLE IF EXISTS ref_amendment_agreem_type CASCADE;
DROP TABLE IF EXISTS ref_amendm_agreem_justif CASCADE;
DROP TABLE IF EXISTS ref_budget_type CASCADE;
DROP TABLE IF EXISTS ref_type_trade CASCADE;
DROP TABLE IF EXISTS ref_buy_status CASCADE;
DROP TABLE IF EXISTS ref_po_st CASCADE;
DROP TABLE IF EXISTS ref_comm_roles CASCADE;
DROP TABLE IF EXISTS ref_contract_status CASCADE;
DROP TABLE IF EXISTS ref_contract_agr_form CASCADE;
DROP TABLE IF EXISTS ref_contract_year_type CASCADE;
DROP TABLE IF EXISTS ref_currency CASCADE;
DROP TABLE IF EXISTS ref_contract_cancel CASCADE;
DROP TABLE IF EXISTS ref_contract_type CASCADE;
DROP TABLE IF EXISTS ref_reason CASCADE;
DROP TABLE IF EXISTS ref_buy_lot_reject_reason CASCADE;

-- =================================================================
-- ОСНОВНЫЕ ТАБЛИЦЫ
-- =================================================================

-- Журнал изменений
CREATE TABLE journal (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_journal_data ON journal USING GIN (data);
CREATE INDEX idx_journal_created_at ON journal (created_at);

-- Реестр участников (компании)
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subjects_data ON subjects USING GIN (data);
CREATE INDEX idx_subjects_bin ON subjects ((data->>'bin'));
CREATE INDEX idx_subjects_iin ON subjects ((data->>'iin'));
CREATE INDEX idx_subjects_pid ON subjects ((data->>'pid'));

-- Реестр недобросовестных поставщиков
CREATE TABLE rnu (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rnu_data ON rnu USING GIN (data);
CREATE INDEX idx_rnu_supplier_biin ON rnu ((data->>'supplier_biin'));

-- Планы закупок
CREATE TABLE plans (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_plans_data ON plans USING GIN (data);
CREATE INDEX idx_plans_subject_biin ON plans ((data->>'subject_biin'));
CREATE INDEX idx_plans_fin_year ON plans ((data->>'plan_fin_year'));

-- Объявления о закупках
CREATE TABLE announcements (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_announcements_data ON announcements USING GIN (data);
CREATE INDEX idx_announcements_number ON announcements ((data->>'number_anno'));
CREATE INDEX idx_announcements_organizer ON announcements ((data->>'organizer_bin'));
CREATE INDEX idx_announcements_status ON announcements ((data->>'ref_buy_status_id'));

-- Заявки поставщиков
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_applications_data ON applications USING GIN (data);
CREATE INDEX idx_applications_supplier ON applications ((data->>'supplier_biin'));

-- Лоты
CREATE TABLE lots (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_lots_data ON lots USING GIN (data);
CREATE INDEX idx_lots_number ON lots ((data->>'lot_number'));
CREATE INDEX idx_lots_customer ON lots ((data->>'customer_bin'));

-- Договоры
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contracts_data ON contracts USING GIN (data);
CREATE INDEX idx_contracts_number ON contracts ((data->>'contract_number'));
CREATE INDEX idx_contracts_supplier ON contracts ((data->>'supplier_biin'));
CREATE INDEX idx_contracts_customer ON contracts ((data->>'customer_bin'));
CREATE INDEX idx_contracts_status ON contracts ((data->>'ref_contract_status_id'));

-- Акты
CREATE TABLE acts (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_acts_data ON acts USING GIN (data);
CREATE INDEX idx_acts_contract ON acts ((data->>'contract_id'));

-- Платежи
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_data ON payments USING GIN (data);
CREATE INDEX idx_payments_contract ON payments ((data->>'contract_id'));

-- =================================================================
-- СПРАВОЧНИКИ (REFERENCES)
-- =================================================================

-- Статусы лотов
CREATE TABLE ref_lots_status (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_lots_status_data ON ref_lots_status USING GIN (data);

-- Способы закупки
CREATE TABLE ref_trade_methods (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_trade_methods_data ON ref_trade_methods USING GIN (data);

-- МКЕЙ (единицы измерения)
CREATE TABLE ref_units (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_units_data ON ref_units USING GIN (data);

-- Месяца
CREATE TABLE ref_months (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_months_data ON ref_months USING GIN (data);

-- Статусы пунктов планов
CREATE TABLE ref_pln_point_status (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_pln_point_status_data ON ref_pln_point_status USING GIN (data);

-- Вид предмета закупки
CREATE TABLE ref_subject_type (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_subject_type_data ON ref_subject_type USING GIN (data);

-- Источник финансирования
CREATE TABLE ref_finsource (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_finsource_data ON ref_finsource USING GIN (data);

-- Администратор бюджетной программы
CREATE TABLE ref_abp (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_abp_data ON ref_abp USING GIN (data);

-- Тип пункта плана
CREATE TABLE ref_point_type (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_point_type_data ON ref_point_type USING GIN (data);

-- КАТО
CREATE TABLE ref_kato (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_kato_data ON ref_kato USING GIN (data);

-- Страны
CREATE TABLE ref_countries (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_countries_data ON ref_countries USING GIN (data);

-- Справочник специфик
CREATE TABLE ref_ekrb (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_ekrb_data ON ref_ekrb USING GIN (data);

-- Справочник программ ФКР
CREATE TABLE ref_fkrb_program (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_fkrb_program_data ON ref_fkrb_program USING GIN (data);

-- Справочник подпрограмм ФКР
CREATE TABLE ref_fkrb_subprogram (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_fkrb_subprogram_data ON ref_fkrb_subprogram USING GIN (data);

-- Обоснование применения способа закупки
CREATE TABLE ref_justification (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_justification_data ON ref_justification USING GIN (data);

-- Вид дополнительного соглашения
CREATE TABLE ref_amendment_agreem_type (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_amendment_agreem_type_data ON ref_amendment_agreem_type USING GIN (data);

-- Основания создания дополнительного соглашения
CREATE TABLE ref_amendm_agreem_justif (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_amendm_agreem_justif_data ON ref_amendm_agreem_justif USING GIN (data);

-- Вид бюджета
CREATE TABLE ref_budget_type (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_budget_type_data ON ref_budget_type USING GIN (data);

-- Тип закупки
CREATE TABLE ref_type_trade (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_type_trade_data ON ref_type_trade USING GIN (data);

-- Статус объявления
CREATE TABLE ref_buy_status (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_buy_status_data ON ref_buy_status USING GIN (data);

-- Статусы ценовых предложений
CREATE TABLE ref_po_st (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_po_st_data ON ref_po_st USING GIN (data);

-- Роль члена комиссии
CREATE TABLE ref_comm_roles (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_comm_roles_data ON ref_comm_roles USING GIN (data);

-- Статус договора
CREATE TABLE ref_contract_status (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_contract_status_data ON ref_contract_status USING GIN (data);

-- Справочник форм заключения договора
CREATE TABLE ref_contract_agr_form (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_contract_agr_form_data ON ref_contract_agr_form USING GIN (data);

-- Тип договора (однолетний/многолетний)
CREATE TABLE ref_contract_year_type (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_contract_year_type_data ON ref_contract_year_type USING GIN (data);

-- Справочник валют
CREATE TABLE ref_currency (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_currency_data ON ref_currency USING GIN (data);

-- Справочник статей для расторжения договора
CREATE TABLE ref_contract_cancel (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_contract_cancel_data ON ref_contract_cancel USING GIN (data);

-- Справочник типов договора
CREATE TABLE ref_contract_type (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_contract_type_data ON ref_contract_type USING GIN (data);

-- Справочник причин внесения в РНУ
CREATE TABLE ref_reason (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_reason_data ON ref_reason USING GIN (data);

-- Список причин по которым не состоялся аукцион по лоту
CREATE TABLE ref_buy_lot_reject_reason (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ref_buy_lot_reject_reason_data ON ref_buy_lot_reject_reason USING GIN (data);

-- =================================================================
-- ТРИГГЕРЫ ДЛЯ АВТОМАТИЧЕСКОГО ОБНОВЛЕНИЯ updated_at
-- =================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Применяем триггер к основным таблицам
CREATE TRIGGER update_subjects_updated_at BEFORE UPDATE ON subjects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rnu_updated_at BEFORE UPDATE ON rnu
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plans_updated_at BEFORE UPDATE ON plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_announcements_updated_at BEFORE UPDATE ON announcements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lots_updated_at BEFORE UPDATE ON lots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contracts_updated_at BEFORE UPDATE ON contracts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_acts_updated_at BEFORE UPDATE ON acts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =================================================================
-- ПРЕДСТАВЛЕНИЯ ДЛЯ УДОБНОЙ РАБОТЫ С ДАННЫМИ
-- =================================================================

-- Вью для удобного просмотра участников
CREATE OR REPLACE VIEW v_subjects AS
SELECT
    id,
    data->>'pid' AS pid,
    data->>'bin' AS bin,
    data->>'iin' AS iin,
    data->>'name_ru' AS name_ru,
    data->>'name_kz' AS name_kz,
    data->>'email' AS email,
    data->>'phone' AS phone,
    data->>'customer' AS is_customer,
    data->>'supplier' AS is_supplier,
    created_at,
    updated_at
FROM subjects;

-- Вью для просмотра договоров
CREATE OR REPLACE VIEW v_contracts AS
SELECT
    id,
    data->>'id' AS contract_id,
    data->>'contract_number' AS contract_number,
    data->>'customer_bin' AS customer_bin,
    data->>'supplier_biin' AS supplier_biin,
    data->>'contract_sum' AS contract_sum,
    data->>'sign_date' AS sign_date,
    data->>'ref_contract_status_id' AS status_id,
    created_at,
    updated_at
FROM contracts;

-- Вью для просмотра объявлений
CREATE OR REPLACE VIEW v_announcements AS
SELECT
    id,
    data->>'id' AS announcement_id,
    data->>'number_anno' AS number_anno,
    data->>'name_ru' AS name_ru,
    data->>'organizer_bin' AS organizer_bin,
    data->>'total_sum' AS total_sum,
    data->>'ref_buy_status_id' AS status_id,
    data->>'start_date' AS start_date,
    data->>'end_date' AS end_date,
    created_at,
    updated_at
FROM announcements;
