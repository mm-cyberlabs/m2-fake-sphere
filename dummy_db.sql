CREATE TABLE USER_DEV.USER_TYPE (
    ID SERIAL PRIMARY KEY,
    NAME VARCHAR(10) NOT NULL UNIQUE,
    CREATED_BY VARCHAR(40) NOT NULL,
    LAST_MODIFIED_BY VARCHAR(40),
    CREATED_DATE_TIME TIMESTAMPTZ NOT NULL,
    LAST_MODIFIED_DATE_TIME TIMESTAMPTZ,
    VERSION INTEGER DEFAULT 0 NOT NULL
);

-- TABLE Comments -> TRUE/FALSE (For if data needs to be generated) | Business name of table | Description of table.
comment on table user_dev.user_type is 'FALSE | User Type | ENUM table for types of users.';

CREATE TABLE USER_DEV.USER (
    ID SERIAL PRIMARY KEY,
    USER_TYPE_ID INTEGER REFERENCES USER_DEV.USER_TYPE(ID) NOT NULL,
    USER_UUID VARCHAR(10) NOT NULL,
    USER_ID VARCHAR(60) NOT NULL UNIQUE UNIQUE,
    CREATED_BY VARCHAR(40) NOT NULL,
    LAST_MODIFIED_BY VARCHAR(40),
    CREATED_DATE_TIME TIMESTAMPTZ NOT NULL,
    LAST_MODIFIED_DATE_TIME TIMESTAMPTZ,
    VERSION INTEGER DEFAULT 0 NOT NULL
);
-- TABLE Comments -> TRUE/FALSE (For if data needs to be generated) | Business name of table | Description of table.
comment on table user_dev.USER is 'TRUE | Users | Contains user information.';
-- Comment rules -> TRUE/FALSE (For if data needs to be generated) | Business name of column | Description of column.
comment on column user_dev.user.id is 'FALSE | identifier | Surrogate key';
comment on column user_dev.user.user_type_id is 'TRUE | [1-3] | Foreign key to user type table.';
comment on column user_dev.user.user_uuid is 'TRUE | [uuid] | Users UUID';
comment on column user_dev.user.user_id is 'TRUE | user name | Users name';
comment on column user_dev.user.created_by is 'TRUE | [sys] | record created by user name';
comment on column user_dev.user.last_modified_by is 'TRUE | [sys] | record updated by user name';
comment on column user_dev.user.created_date_time is 'TRUE | [timestamp] | record created timestamp';
comment on column user_dev.user.last_modified_date_time is 'TRUE | [timestamp] | record updated timestamp';
comment on column user_dev.user.version is 'TRUE | [0] | record updated by user name';

CREATE TABLE USER_DEV.USER_DEMOGRAPHIC (
    ID SERIAL PRIMARY KEY,
    USER_ID INTEGER REFERENCES USER_DEV.USER(ID) UNIQUE,
    ADDRESS_LINE_1 VARCHAR(100) NOT NULL,
    ADDRESS_LINE_2 VARCHAR(100),
    CITY VARCHAR(100) NOT NULL,
    STATE VARCHAR(100) NOT NULL,
    COUNTRY VARCHAR(200) NOT NULL,    
    CREATED_BY VARCHAR(40) NOT NULL,
    LAST_MODIFIED_BY VARCHAR(40),
    CREATED_DATE_TIME TIMESTAMPTZ NOT NULL,
    LAST_MODIFIED_DATE_TIME TIMESTAMPTZ,
    VERSION INTEGER DEFAULT 0 NOT NULL
);

-- TABLE Comments -> TRUE/FALSE (For if data needs to be generated) | Business name of table | Description of table.
comment on table user_dev.user_demographic is 'TRUE | user demographic | Contains user demographic.';
-- Comment rules -> TRUE/FALSE (For if data needs to be generated) | Business name of column | Description of column.
comment on column user_dev.user_demographic.id is 'FALSE | identifier | Surrogate key';

comment on column user_dev.user_demographic.user_id is 'TRUE | [~user_dev.user(id)] | Foreign key to the user table.';
comment on column user_dev.user_demographic.address_line_1 is 'TRUE | address line 1 | Address line 1.';
comment on column user_dev.user_demographic.address_line_2 is 'TRUE | address line 2 | Address line 2.';
comment on column user_dev.user_demographic.city is 'TRUE | city | City.';
comment on column user_dev.user_demographic.state is 'TRUE | state name | State name.';
comment on column user_dev.user_demographic.country is 'TRUE | country name | Country name.';

comment on column user_dev.user_demographic.created_by is 'TRUE | [sys] | record created by user name';
comment on column user_dev.user_demographic.last_modified_by is 'TRUE | [sys] | record updated by user name';
comment on column user_dev.user_demographic.created_date_time is 'TRUE | [timestamp] | record created timestamp';
comment on column user_dev.user_demographic.last_modified_date_time is 'TRUE | [timestamp] | record updated timestamp';
comment on column user_dev.user_demographic.version is 'TRUE | [0] | record updated by user name';

SELECT
    n.nspname AS schema,
    c.relname AS table,
    d.description AS comment
FROM
    pg_class c
JOIN
    pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN
    pg_description d ON d.objoid = c.oid AND d.objsubid = 0
WHERE
    n.nspname = 'user_dev'
    and c.relkind = 'r';

    SELECT
    n.nspname AS schema,
    c.relname AS table,
    x.comment AS table_comment,
    a.attname AS column,
    d.description AS column_comment
FROM
    pg_class c
JOIN
    pg_namespace n ON n.oid = c.relnamespace
JOIN
    pg_attribute a ON a.attrelid = c.oid
LEFT JOIN
    pg_description d ON d.objoid = a.attrelid AND d.objsubid = a.attnum
JOIN
    (SELECT
    c.relname AS table,
    d.description AS comment
FROM
    pg_class c
JOIN
    pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN
    pg_description d ON d.objoid = c.oid AND d.objsubid = 0
WHERE
    n.nspname = 'user_dev'
    and c.relkind = 'r') x on x.table = c.relname
WHERE
    n.nspname = 'user_dev'
    AND a.attnum > 0
    AND NOT a.attisdropped
    and c.relkind = 'r'
    and d.description is not null;