SELECT row_to_json(r) AS DATA
FROM (
     WITH comments as (
         SELECT tablename
         FROM pg_catalog.pg_tables
         WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'
     )
     SELECT obj_description(oid) as table_comment,
            relname, TABLE_NAME, COLUMN_NAME, data_type,
            (
                SELECT pg_catalog.col_description(c.oid, cols.ordinal_position::int)
                FROM pg_catalog.pg_class c
                WHERE c.oid = (SELECT ('"' || cols.table_name || '"')::regclass::oid)
                  AND c.relname = cols.table_name
            ) AS column_comment
     FROM INFORMATION_SCHEMA.COLUMNS as cols, pg_class, comments
     WHERE TABLE_NAME = tablename  AND relname = tablename
) r;