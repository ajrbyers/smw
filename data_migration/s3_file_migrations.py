#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script for copying Rua instances' files and media from servers to AWS s3."""
import os
import sys

import boto3

from utils import execute_bash_command


REMOTE_SERVER_HOST = os.getenv('REMOTE_SERVER_HOST')
REMOTE_SERVER_SSH_USER = os.getenv('REMOTE_SERVER_SSH_USER')
USER_SSH_KEY_PATH = os.getenv('USER_SSH_KEY_PATH')
LOCAL_FILES_DIRECTORY = os.getenv('LOCAL_FILES_DIRECTORY')
REMOTE_FILES_DIRECTORY = os.getenv('REMOTE_FILES_DIRECTORY')
RUA_S3_BUCKET_NAME = os.getenv('RUA_S3_BUCKET_NAME')


def copy_press_files_to_local(press_code):
    remote_files_subdirectory = os.path.join(REMOTE_FILES_DIRECTORY, press_code)
    copy_files_command_args = [
        'scp',
        '-r',
        '-i',
        USER_SSH_KEY_PATH,
        f'{REMOTE_SERVER_SSH_USER}@{REMOTE_SERVER_HOST}'
        f':{remote_files_subdirectory}',
        LOCAL_FILES_DIRECTORY,
    ]
    print('Copying remote files to local machine...\n')
    execute_bash_command(copy_files_command_args)
    return os.path.join(LOCAL_FILES_DIRECTORY, press_code)


def copy_local_press_files_to_s3(press_code, local_files_directory):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(RUA_S3_BUCKET_NAME)

    print('Copying files to AWS s3...\n')
    for directory, subdirectories, file_names in os.walk(local_files_directory):

        for filename in file_names:

            file_path = os.path.join(directory, filename)

            with open(file_path, 'rb') as file_stream:

                django_file_path = strip_directory_part(
                    directory,
                    local_files_directory
                )
                s3_path = os.path.join(
                    press_code,
                    'files',
                    django_file_path,
                    filename
                )
                print('Copying file: {s3_path}'.format(s3_path=s3_path))
                bucket.put_object(
                    Key=s3_path,
                    Body=file_stream
                )


def strip_directory_part(directory, part_to_strip):
    subpath = directory.replace(part_to_strip, '')
    return subpath.strip('/')


def migrate_press_files_to_s3(press_code):
    local_files_directory = copy_press_files_to_local(press_code)
    copy_local_press_files_to_s3(press_code, local_files_directory)
    print('\nFiles copied successfully :-)')


def migrate_presses_files_to_s3(*press_codes):
    for press_code in press_codes:
        migrate_press_files_to_s3(press_code)


if __name__ == '__main__':
    migrate_presses_files_to_s3(*sys.argv[1:])
