-- ============================================================
-- setup_dev.sql
-- Snowflake setup for dbt dev environment
-- Project: pharmacy_benefits
-- ============================================================

USE ROLE ACCOUNTADMIN;

-- ------------------------------------------------------------
-- 1. Create dbt dev role
-- ------------------------------------------------------------

CREATE ROLE IF NOT EXISTS DBT_DEV_ROLE;

-- Grant role to your Snowflake user
GRANT ROLE DBT_DEV_ROLE TO USER JMOORE87JR;

-- ------------------------------------------------------------
-- 2. Create dev warehouse
-- ------------------------------------------------------------

CREATE WAREHOUSE IF NOT EXISTS DBT_DEV_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

GRANT USAGE ON WAREHOUSE DBT_DEV_WH TO ROLE DBT_DEV_ROLE;

-- ------------------------------------------------------------
-- 3. Create dev database
-- ------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS PHARMACY_BENEFITS_DEV;

GRANT USAGE ON DATABASE PHARMACY_BENEFITS_DEV TO ROLE DBT_DEV_ROLE;

-- Allow dbt dev role to create personal/dev schemas
GRANT CREATE SCHEMA ON DATABASE PHARMACY_BENEFITS_DEV TO ROLE DBT_DEV_ROLE;

-- ------------------------------------------------------------
-- 4. Create personal dev schema
-- ------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS PHARMACY_BENEFITS_DEV.DBT_JMOORE;

GRANT USAGE ON SCHEMA PHARMACY_BENEFITS_DEV.DBT_JMOORE TO ROLE DBT_DEV_ROLE;

GRANT CREATE TABLE ON SCHEMA PHARMACY_BENEFITS_DEV.DBT_JMOORE TO ROLE DBT_DEV_ROLE;
GRANT CREATE VIEW ON SCHEMA PHARMACY_BENEFITS_DEV.DBT_JMOORE TO ROLE DBT_DEV_ROLE;
GRANT CREATE STAGE ON SCHEMA PHARMACY_BENEFITS_DEV.DBT_JMOORE TO ROLE DBT_DEV_ROLE;
GRANT CREATE FILE FORMAT ON SCHEMA PHARMACY_BENEFITS_DEV.DBT_JMOORE TO ROLE DBT_DEV_ROLE;
GRANT CREATE SEQUENCE ON SCHEMA PHARMACY_BENEFITS_DEV.DBT_JMOORE TO ROLE DBT_DEV_ROLE;
GRANT CREATE FUNCTION ON SCHEMA PHARMACY_BENEFITS_DEV.DBT_JMOORE TO ROLE DBT_DEV_ROLE;
GRANT CREATE PROCEDURE ON SCHEMA PHARMACY_BENEFITS_DEV.DBT_JMOORE TO ROLE DBT_DEV_ROLE;

-- ------------------------------------------------------------
-- 5. Optional default user settings
-- ------------------------------------------------------------

ALTER USER JMOORE87JR SET
  DEFAULT_ROLE = DBT_DEV_ROLE
  DEFAULT_WAREHOUSE = DBT_DEV_WH
  DEFAULT_NAMESPACE = PHARMACY_BENEFITS_DEV.DBT_JMOORE;