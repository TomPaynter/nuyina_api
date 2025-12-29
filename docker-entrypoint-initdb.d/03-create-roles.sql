-- -- Create read-only role if it does not exist
-- DO
-- $$
-- BEGIN
--     IF NOT EXISTS (
--         SELECT 1 FROM pg_roles WHERE rolname = 'nuyinapi_ro'
--     ) THEN
--         CREATE ROLE nuyinapi_ro
--             NOLOGIN
--             NOSUPERUSER
--             NOCREATEDB
--             NOCREATEROLE
--             NOINHERIT;
--     END IF;
-- END
-- $$;

-- -- Allow role to connect to the database
-- GRANT CONNECT ON DATABASE app_db TO nuyinapi_ro;

-- -- Allow usage of the schema (elog)
-- GRANT USAGE ON SCHEMA elog TO nuyinapi_ro;

-- -- Allow read-only access to all existing tables
-- GRANT SELECT ON ALL TABLES IN SCHEMA elog TO nuyinapi_ro;

-- -- Ensure future tables are also readable
-- ALTER DEFAULT PRIVILEGES IN SCHEMA elog
-- GRANT SELECT ON TABLES TO nuyinapi_ro;


-- -- Create role if missing
-- DO $$
-- BEGIN
--     IF NOT EXISTS (
--         SELECT 1 FROM pg_roles WHERE rolname = 'nuyinapi_rw'
--     ) THEN
--         CREATE ROLE nuyinapi_rw
--             NOLOGIN
--             NOSUPERUSER
--             NOCREATEDB
--             NOCREATEROLE
--             INHERIT;
--     END IF;
-- END
-- $$;

-- -- Allow database access
-- GRANT CONNECT ON DATABASE app_db TO nuyinapi_rw;

-- -- Schema access (adjust schema name if needed)
-- GRANT USAGE ON SCHEMA elog TO nuyinapi_rw;

-- -- Read/write on existing tables
-- GRANT
--   SELECT,
--   INSERT,
--   UPDATE,
--   DELETE,
--   TRUNCATE
-- ON ALL TABLES IN SCHEMA elog
-- TO nuyinapi_rw;

-- -- Sequence access (needed for INSERTs)
-- GRANT
--   USAGE,
--   SELECT
-- ON ALL SEQUENCES IN SCHEMA elog
-- TO nuyinapi_rw;

-- -- Ensure future tables get same privileges
-- ALTER DEFAULT PRIVILEGES IN SCHEMA elog
-- GRANT
--   SELECT,
--   INSERT,
--   UPDATE,
--   DELETE,
--   TRUNCATE
-- ON TABLES
-- TO nuyinapi_rw;

-- -- Ensure future sequences work
-- ALTER DEFAULT PRIVILEGES IN SCHEMA elog
-- GRANT
--   USAGE,
--   SELECT
-- ON SEQUENCES
-- TO nuyinapi_rw;


-- ============================================================================
-- PostgREST roles for app_db / elog schema
-- ============================================================================

-- ----------------------------
-- READ-ONLY ROLE
-- ----------------------------
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'nuyinapi_ro'
    ) THEN
        CREATE ROLE nuyinapi_ro
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOINHERIT;
    END IF;
END
$$;

-- Allow database connection
GRANT CONNECT ON DATABASE app_db TO nuyinapi_ro;

-- Allow schema usage
GRANT USAGE ON SCHEMA elog TO nuyinapi_ro;

-- Read-only access to existing tables
GRANT SELECT
ON ALL TABLES IN SCHEMA elog
TO nuyinapi_ro;

-- Ensure future tables are readable
ALTER DEFAULT PRIVILEGES IN SCHEMA elog
GRANT SELECT
ON TABLES
TO nuyinapi_ro;


-- ----------------------------
-- READ / WRITE ROLE
-- ----------------------------
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'nuyinapi_rw'
    ) THEN
        CREATE ROLE nuyinapi_rw
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            INHERIT;
    END IF;
END
$$;

-- Allow database connection
GRANT CONNECT ON DATABASE app_db TO nuyinapi_rw;

-- Allow schema usage
GRANT USAGE ON SCHEMA elog TO nuyinapi_rw;

-- Full DML access on existing tables
GRANT
    SELECT,
    INSERT,
    UPDATE,
    DELETE,
    TRUNCATE
ON ALL TABLES IN SCHEMA elog
TO nuyinapi_rw;

-- Required for INSERTs on SERIAL / IDENTITY columns
GRANT
    USAGE,
    SELECT
ON ALL SEQUENCES IN SCHEMA elog
TO nuyinapi_rw;

-- Ensure future tables get same privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA elog
GRANT
    SELECT,
    INSERT,
    UPDATE,
    DELETE,
    TRUNCATE
ON TABLES
TO nuyinapi_rw;

-- Ensure future sequences work
ALTER DEFAULT PRIVILEGES IN SCHEMA elog
GRANT
    USAGE,
    SELECT
ON SEQUENCES
TO nuyinapi_rw;

GRANT nuyinapi_ro TO app_user;
GRANT nuyinapi_rw TO app_user;