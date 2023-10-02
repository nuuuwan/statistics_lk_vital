import os

import pyexcel
from utils import Log

log = Log('convert_old_xls')


def main():
    dir_data = os.path.abspath('data')
    for file_only in os.listdir(dir_data):
        if file_only.endswith('.xls'):
            old_file_path = os.path.join(dir_data, file_only)
            new_file_path = old_file_path.replace('.xls', '.xlsx')
            pyexcel.save_book_as(
                file_name=old_file_path, dest_file_name=new_file_path
            )
            log.info(f'convert {old_file_path} to {new_file_path}')


if __name__ == '__main__':
    main()
