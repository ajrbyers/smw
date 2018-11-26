# -*- coding: utf-8 -*-
"""SQLAlchemy-based scripts for migrating MySQL databases to PostgreSQL."""
import logging
import os
import sys

from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Boolean,
    DateTime,
    Float,
)
from sqlalchemy.types import (
    TIMESTAMP as POSTGRES_TIMESTAMP,
    TEXT as POSTGRES_TEXT,
    VARCHAR as POSTGRES_VARCHAR
)
from sqlalchemy.dialects.postgresql import BIT as POSTGRES_BIT
from sqlalchemy.dialects.mysql.base import (
    TINYINT,
    VARCHAR,
    DATETIME,
    TIMESTAMP,
    DOUBLE,
    TEXT,
    BIT,
    LONGTEXT
)

from sqlalchemy.ext.declarative import declarative_base

MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
LOCALHOST = '127.0.0.1'

SQL_QUERIES_BEFORE = [
    # 'alter table auth_permission disable_constraints constraint '
    # 'auth_permission_content_type_id_2f476e4b_fk_django_co;'
]

SQL_QUERIES_AFTER = [
    # 'alter table auth_permission enable_constraints constraint '
    # 'auth_permission_content_type_id_2f476e4b_fk_django_co;'
]

# Tables not to be copied
# Django's automatically generated content is needed in these cases
SKIP_DJANGO_TABLES = [
    'django_migrations',
]

# Triggers disabled due to mutually referencing foreign keys & other constraints
DISABLE_TRIGGERS_TABLES = [
    # 'auth_permission',
    # 'django_content_type',
]

# Tables to be cleared of content automatically generated upon first migration
CLEAR_FIRST_DJANGO_TABLES = [
    'auth_permission',
    'django_content_type',
]

# Tables to be copied fist, due to foreign key constraints
FIRST_DJANGO_TABLES = [
    'django_content_type',
    'auth_permission',
    'core_license',
    'core_stage',
    'review_form',
    'auth_user',
    'core_file',
    'core_contract',
    'core_series',
    'core_proposalform',
    'submission_proposal',
    'core_editor',
    'core_keyword',
    'core_language',
    'core_book',
    'core_reviewround',
    'review_formresult',
    'core_reviewassignment',
    'core_subject',
    'core_chapter',
    'core_chapterformat',
    'core_physicalformat',
    'core_role',
    'core_profile',
    'core_profile_roles',
    'core_proposalformelement',
    'core_proposalformelementsrelationship',
    'core_settinggroup',
    'review_formelement',
    'review_formelementsrelationship',
    'submission_proposalreview',
    'core_editorialreviewassignment',
]

logger = logging.getLogger('sqlalchemy.pool.QueuePool')
ch = logging.StreamHandler()
logger.addHandler(ch)


def copy_table_schemas_to_postgresdb(mysql_metadata, postgres_engine):
    postgres_engine._metadata = MetaData(bind=postgres_engine)

    for name, klass in mysql_metadata.tables.items():
        table = Table(klass.name, postgres_engine._metadata)
        for column in klass.columns:
            if isinstance(column.type, TEXT):
                table.append_column(
                    Column(
                        column.name,
                        POSTGRES_TEXT(collation=''),
                        nullable=column.nullable
                    )
                )
            elif isinstance(column.type, VARCHAR):
                table.append_column(
                    Column(
                        column.name,
                        POSTGRES_VARCHAR(
                            length=column.type.length,
                            collation=''
                        ),
                        nullable=column.nullable
                    )
                )
            elif isinstance(column.type, TINYINT):
                table.append_column(
                    Column(
                        column.name, Boolean(),
                        nullable=column.nullable
                    )
                )
            elif isinstance(column.type, DATETIME):
                table.append_column(
                    Column(
                        column.name, DateTime(),
                        nullable=column.nullable
                    )
                )
            elif isinstance(column.type, TIMESTAMP):
                table.append_column(
                    Column(
                        column.name,
                        POSTGRES_TIMESTAMP(),
                        nullable=column.nullable
                    )
                )
            elif isinstance(column.type, DOUBLE):
                table.append_column(
                    Column(column.name, Float(), nullable=column.nullable))
            elif isinstance(column.type, BIT):
                table.append_column(
                    Column(
                        column.name,
                        POSTGRES_BIT(
                            length=column.type.length
                        ),
                        nullable=column.nullable
                    )
                )
            elif isinstance(column.type, LONGTEXT):
                table.append_column(
                    Column(
                        column.name,
                        POSTGRES_TEXT(collation=''),
                        nullable=column.nullable
                    )
                )
            else:
                table.append_column(column.copy())

        print('create', table.name)
        table.create()


def quick_mapper(table):
    Base = declarative_base()

    pk_count = len([c for c in table.columns if c.primary_key])
    if pk_count == 0:
        primary_columns = [
            column.name for column in table.columns
            if 'id' in column.name
        ]
        if primary_columns:
            pk_name = primary_columns[0]
        else:
            pk_name = [column.name for column in table.columns][0]

        class GenericMapper(Base):
            __table__ = table
            __mapper_args__ = {
                'primary_key': [getattr(table.c, pk_name)]
            }

        return GenericMapper

    class GenericMapper(Base):
        __table__ = table

    return GenericMapper


def execure_custom_sql(
        database_engine,
        query,
):
    print('executing', query)
    with database_engine.connect() as connection:
        connection.execution_options(
            isolation_level='AUTOCOMMIT'
        ).execute(
            query
        )


def copy_table_rows(
        mysql_engine,
        mysql_session,
        postgres_engine,
        postgres_session,
        table_name,
):
    print('copying', table_name)
    dest_table = Table(
        table_name,
        MetaData(bind=postgres_engine),
        autoload=True
    )
    dest_columns = dest_table.columns.keys()

    table = Table(table_name, MetaData(bind=mysql_engine), autoload=True)
    NewRecord = quick_mapper(table)

    for record in mysql_session.query(table).all():
        data = {}
        for column in dest_columns:
            value = getattr(record, column)
            if isinstance(table.columns[column].type, TINYINT):
                value = bool(value)
            elif isinstance(value, bytes):
                value = value.decode('latin8')

            data[str(column)] = value
        postgres_session.merge(NewRecord(**data))
    postgres_session.commit()


def restart_id_sequence_auto_increment(
        postgres_engine,
        table_name,
):
    with postgres_engine.connect() as connection:

        id_column_exists = bool(
            next(
                connection.execute(
                    'SELECT COUNT(*) FROM information_schema.columns '
                    'WHERE table_schema=\'public\' '
                    f'AND table_name=\'{table_name}\''
                    'AND column_name=\'id\';'
                )
            )[0]
        )

        if id_column_exists:

            max_id = next(
                connection.execute(f'SELECT MAX(id) from {table_name}')
            )[0]
            # Set the sequence to 1 in cases of no
            max_id = max_id if max_id else 1

            sequence_exists = bool(
                next(
                    connection.execute(
                        'SELECT COUNT(*) FROM information_schema.sequences '
                        'WHERE sequence_schema=\'public\' '
                        f'AND sequence_name=\'{table_name}_id_seq\';'
                    )
                )[0]
            )

    if id_column_exists and sequence_exists:
        execure_custom_sql(
            database_engine=postgres_engine,
            query=(
                f'ALTER SEQUENCE {table_name}_id_seq RESTART WITH {max_id +1};'
            )
        )


def copy_table_data_to_postgresdb(
        mysql_metadata,
        mysql_engine,
        postgres_engine
):
    PostgresSession = sessionmaker(bind=postgres_engine, autoflush=False)
    postgres_session = PostgresSession()
    MySQLSession = sessionmaker(bind=mysql_engine)
    mysql_session = MySQLSession()

    for query in SQL_QUERIES_BEFORE:
        execure_custom_sql(
            database_engine=postgres_engine,
            query=query
        )

    for table_name in CLEAR_FIRST_DJANGO_TABLES:
        execure_custom_sql(
            database_engine=postgres_engine,
            query=f'DELETE FROM {table_name};'
        )

    for table_name in DISABLE_TRIGGERS_TABLES:
        execure_custom_sql(
            database_engine=postgres_engine,
            query=f'ALTER TABLE {table_name} DISABLE TRIGGER ALL;'
        )

    for table_name in FIRST_DJANGO_TABLES:
        copy_table_rows(
            mysql_engine=mysql_engine,
            mysql_session=mysql_session,
            postgres_engine=postgres_engine,
            postgres_session=postgres_session,
            table_name=table_name
        )
        restart_id_sequence_auto_increment(
            postgres_engine=postgres_engine,
            table_name=table_name,
        )

    for klass in mysql_metadata.tables.values():
        if (
                klass.name not in SKIP_DJANGO_TABLES and
                klass.name not in FIRST_DJANGO_TABLES
        ):
            copy_table_rows(
                mysql_engine=mysql_engine,
                mysql_session=mysql_session,
                postgres_engine=postgres_engine,
                postgres_session=postgres_session,
                table_name=klass.name
            )
            restart_id_sequence_auto_increment(
                postgres_engine=postgres_engine,
                table_name=klass.name,
            )

    for table_name in DISABLE_TRIGGERS_TABLES:
        execure_custom_sql(
            database_engine=postgres_engine,
            query=f'ALTER TABLE {table_name} ENABLE TRIGGER ALL;'
        )

    for query in SQL_QUERIES_AFTER:
        execure_custom_sql(
            database_engine=postgres_engine,
            query=query
        )


def create_postgres_database(
        database_name,
        username,
        password,
        host='127.0.0.1',
        port=POSTGRES_PORT
):
    postgres_engine = create_engine(
        f'postgresql+psycopg2://{username}:{password}@{host}:{port}/postgres'
    )

    with postgres_engine.connect() as connection:
        existing_databases = [
            row[0] for row in connection.execute(
                'SELECT datname FROM pg_database '
                'WHERE datistemplate = false;'
            )
        ]
        if database_name in existing_databases:
            connection.execution_options(
                isolation_level='AUTOCOMMIT'
            ).execute(
                f'DROP DATABASE {database_name};'
            )

        connection.execution_options(
            isolation_level='AUTOCOMMIT'
        ).execute(
            f'CREATE DATABASE {database_name};'
        )


def create_mysql_database(
        database_name,
        username,
        password,
        host='127.0.0.1',
        port=MYSQL_PORT
):
    postgres_engine = create_engine(
        f'mysql+pymysql://{username}:{password}'
        f'@{host}:{port}'
    )

    with postgres_engine.connect() as connection:
        existing_databases = [
            row[0] for row in connection.execute('SHOW DATABASES;')
        ]
        if database_name in existing_databases:
            connection.execution_options(
                isolation_level='AUTOCOMMIT'
            ).execute(
                f'DROP DATABASE {database_name};'
            )

        connection.execution_options(
            isolation_level='AUTOCOMMIT'
        ).execute(
            f'CREATE DATABASE {database_name};'
        )


def copy_from_mysqldb_to_postgresdb(
        mysql_db_name,
        mysql_user,
        mysql_pass,
        mysql_host,
        postgres_db_name,
        postgres_user,
        postgres_pass,
        postgres_host,
):
    print(
        f'\nCopying data from {mysql_host}:{MYSQL_PORT}/{mysql_db_name} '
        f'to {postgres_host}:{POSTGRES_PORT}/{postgres_db_name}\n...\n'
    )
    mysql_engine = create_engine(
        f'mysql+pymysql://{mysql_user}:{mysql_pass}'
        f'@{mysql_host}:{MYSQL_PORT}/{mysql_db_name}'
    )

    postgres_engine = create_engine(
        f'postgresql+psycopg2://{postgres_user}:{postgres_pass}'
        f'@{postgres_host}:{POSTGRES_PORT}/{postgres_db_name}'
    )
    mysql_metadata = MetaData()
    mysql_metadata.reflect(mysql_engine)

    # IMPORTANT:
    # Call to copy_table_schemas_to_postgresdb missed as table creation
    # is handled by Django migrations

    copy_table_data_to_postgresdb(
        mysql_metadata=mysql_metadata,
        mysql_engine=mysql_engine,
        postgres_engine=postgres_engine
    )


if __name__ == '__main__':
    copy_from_mysqldb_to_postgresdb(
        mysql_host=sys.argv[1],
        mysql_db_name=sys.argv[2],
        mysql_user=sys.argv[3],
        mysql_pass=sys.argv[4],
        postgres_host=sys.argv[5],
        postgres_db_name=sys.argv[6],
        postgres_user=sys.argv[7],
        postgres_pass=sys.argv[8],
    )
