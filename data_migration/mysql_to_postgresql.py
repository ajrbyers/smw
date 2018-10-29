import logging
import os
import sys

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    create_engine,
    MetaData,
    inspect,
    Table,
    Column,
    Boolean,
    DateTime,
    Float,
    Integer
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
from sshtunnel import SSHTunnelForwarder

MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
LOCALHOST = '127.0.0.1'

logger = logging.getLogger('sqlalchemy.pool.QueuePool')
ch = logging.StreamHandler()
logger.addHandler(ch)


class Tunnel(object):
    def __init__(
            self,
            ssh_host,
            ssh_port,
            ssh_username,
            remote_host,
            remote_port,
            ssh_pkey='{home_directory}/.ssh/id_rsa'.format(
                home_directory=os.getenv('HOME'),
            )
    ):
        self._tunnel = SSHTunnelForwarder(
            (
                ssh_host,
                ssh_port
            ),
            ssh_username=ssh_username,
            ssh_pkey=ssh_pkey,
            remote_bind_address=(
                remote_host,
                remote_port
            ),
            set_keepalive=1.0
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, stype, svalue, straceback):
        self.stop()

    def start(self):
        self._tunnel.start()

    def get_local_bind_port(self):
        return self._tunnel.local_bind_port

    def stop(self):
        self._tunnel.stop()


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


def copy_table_data_to_postgresdb(
        mysql_metadata,
        mysql_engine,
        postgres_engine
):
    PostgresSession = sessionmaker(bind=postgres_engine, autoflush=False)
    postgres_session = PostgresSession()
    MySQLSession = sessionmaker(bind=mysql_engine)
    mysql_session = MySQLSession()

    for name, klass in mysql_metadata.tables.items():
        print('copy', klass.name)
        dest_table = Table(
            klass.name,
            MetaData(bind=postgres_engine),
            autoload=True
        )
        dest_columns = dest_table.columns.keys()

        table = Table(klass.name, MetaData(bind=mysql_engine), autoload=True)
        NewRecord = quick_mapper(table)

        for record in mysql_session.query(table).all():
            data = {}
            for column in dest_columns:
                value = getattr(record, column)
                if isinstance(table.columns[column].type, TINYINT):
                    value = bool(value)
                elif isinstance(value, str):
                    value = value.decode('latin8')

                data[str(column)] = value
            postgres_session.merge(NewRecord(**data))
        postgres_session.commit()


def copy_from_mysqldb_to_postgresdb(
        mysql_db_name,
        mysql_user,
        mysql_pass,
        mysql_host,
        postgres_db_name,
        postgres_user,
        postgres_pass,
        postgres_host,
        ssh_username='',
        ssh_pkey='{}/.ssh/id_rsa'.format(os.getenv('HOME'))
):
    with Tunnel(
        ssh_host=LOCALHOST,
        ssh_port=22,
        ssh_username=ssh_username,
        remote_host=mysql_host,
        remote_port=MYSQL_PORT,
        ssh_pkey=ssh_pkey,
    ) as tunnel:
        mysql_engine = create_engine(
            f'mysql+pymysql://{mysql_user}:{mysql_pass}'
            f'@{mysql_host}:{tunnel.get_local_bind_port()}/{mysql_db_name}'
        )

        postgres_engine = create_engine(
            f'postgresql+psycopg2://{postgres_user}:{postgres_pass}'
            f'@{postgres_host}:{POSTGRES_PORT}/{postgres_db_name}'
        )
        mysql_metadata = MetaData()
        mysql_metadata.reflect(mysql_engine)

        copy_table_schemas_to_postgresdb(
            mysql_metadata=mysql_metadata,
            postgres_engine=postgres_engine
        )
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
        ssh_username=sys.argv[5],
        postgres_host=sys.argv[6],
        postgres_db_name=sys.argv[7],
        postgres_user=sys.argv[8],
        postgres_pass=sys.argv[9],
    )
