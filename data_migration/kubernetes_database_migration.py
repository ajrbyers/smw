#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick'n'dirty script for copying MySQL database for Rua instances.
'ssh' bash workaround used due to difficulties with ssh tunneling.
"""
from datetime import date
import os
import sys
import subprocess

from utils import execute_bash_command
from mysql_to_postgresql import (
    copy_from_mysqldb_to_postgresdb,
    create_mysql_database,
    create_postgres_database,
)

DATABASE_DUMP_DIRECTORY = os.getenv('DATABASE_DUMP_DIRECTORY')
USER_SSH_KEY_PATH = os.getenv('USER_SSH_KEY_PATH')
FROM_DATABASE_SSH_USER = os.getenv('FROM_DATABASE_SSH_USER')
FROM_DATABASE_USER = os.getenv('FROM_DATABASE_USER')
FROM_DATABASE_PASS = os.getenv('FROM_DATABASE_PASS')
FROM_DATABASE_HOST = os.getenv('FROM_DATABASE_HOST')
LOCAL_DATABASE_USER = os.getenv('LOCAL_DATABASE_USER')
LOCAL_DATABASE_PASS = os.getenv('LOCAL_DATABASE_PASS')
LOCAL_DATABASE_HOST = os.getenv('LOCAL_DATABASE_HOST')
TO_DATABASE_USER = os.getenv('TO_DATABASE_USER')
TO_DATABASE_PASS = os.getenv('TO_DATABASE_PASS')
TO_DATABASE_HOST = os.getenv('TO_DATABASE_HOST')


def dump_remote_mysql_production_database(press_code):
    """Runs a bash command run copy the databases from a remote host via ssl."""
    database_dump_filename = f'{str(date.today())}_{press_code}.sql'
    print('Creating dump of remote production database...')
    dump_command_args = [
        'ssh',
        '-i',
        USER_SSH_KEY_PATH,
        f'{FROM_DATABASE_SSH_USER}@{FROM_DATABASE_HOST}',
        'mysqldump',
        f'rua_{press_code}',
        '>',
        database_dump_filename,
        '--single-transaction',
        '-u',
        FROM_DATABASE_USER,
        f'-p{FROM_DATABASE_PASS}'
    ]
    execute_bash_command(dump_command_args)

    database_dump_file_path = os.path.join(
        DATABASE_DUMP_DIRECTORY,
        database_dump_filename,
    )
    print('Copying database dump from remote server...')
    copy_command_args = [
        'scp',
        '-i',
        USER_SSH_KEY_PATH,
        f'{FROM_DATABASE_SSH_USER}@{FROM_DATABASE_HOST}:'
        f'~/{database_dump_filename}',
        database_dump_file_path,
    ]
    execute_bash_command(copy_command_args)

    return database_dump_file_path


def create_local_mysql_database(press_code):
    create_mysql_database(
        database_name=press_code,
        username=LOCAL_DATABASE_USER,
        password=LOCAL_DATABASE_PASS,
        host=LOCAL_DATABASE_HOST,
    )


def load_production_data_to_local_mysql_database(
        press_code,
        database_dump_location,
):
    print('Loading data from dump to local MySQL database...')
    load_database_dump_command_args = [
        'mysql',
        '-h',
        LOCAL_DATABASE_HOST,
        '-u',
        LOCAL_DATABASE_USER,
        f'-p{LOCAL_DATABASE_PASS}',
        press_code,  # Database name
    ]
    with open(database_dump_location, 'r') as dump_stream:
        process = subprocess.Popen(
            load_database_dump_command_args,
            stdin=dump_stream
        )
        stdout, stderr = process.communicate()

    if stderr:
        print(
            f'Command returned error information.\n  '
            f'stderr: {stderr.decode()}\n'
        )
    else:
        print('Command successful.\n')

    if stdout:
        print(f'  stdout: {stdout.decode()}')


def create_remote_postgres_production_database(press_code):
    create_postgres_database(
        database_name=press_code,
        username=TO_DATABASE_USER,
        password=TO_DATABASE_PASS,
        host=TO_DATABASE_HOST,
    )


def copy_rua_production_mysql_database_to_postgresql(press_code):
    copy_from_mysqldb_to_postgresdb(
        mysql_db_name=press_code,
        mysql_user=LOCAL_DATABASE_USER,
        mysql_pass=LOCAL_DATABASE_PASS,
        mysql_host=LOCAL_DATABASE_HOST,
        postgres_db_name=press_code,
        postgres_user=TO_DATABASE_USER,
        postgres_pass=TO_DATABASE_PASS,
        postgres_host=TO_DATABASE_HOST,
    )
    print('\nData copied succesfully :-)')


def migrate_rua_data_for_press(press_code):
    path_to_sql_dump = dump_remote_mysql_production_database(press_code)

    create_local_mysql_database(press_code)
    load_production_data_to_local_mysql_database(press_code, path_to_sql_dump)

    # Call to create_remote_postgres_production_database missed
    # as remote database creation precedes Django migrations,
    # which precede this script.
    copy_rua_production_mysql_database_to_postgresql(press_code)


def migrate_rua_data_for_presses(press_codes):
    for press_code in press_codes:
        migrate_rua_data_for_press(press_code)


if __name__ == '__main__':
    migrate_rua_data_for_presses(sys.argv[1:])
