import logging
import os.path
import shutil

import _fs_entry_handler as fshandler

def copy_file(file_path, relative_path):
    dest_file_path = os.path.join("_processing", relative_path)
    directory_name = os.path.dirname(dest_file_path)

    os.makedirs(directory_name, exist_ok=True)
    logging.info(f'Created directory here {directory_name}')

    logging.info(f'Copy file from {file_path} to {directory_name}')
    shutil.copy2(file_path, dest_file_path)

def handle_event_entry(file_path, relative_path, channel, args):
    copy_file(file_path, relative_path)
    logging.info(f'Copied file {relative_path}')

if __name__ == '__main__':
    fshandler.start(handle_event_entry, prefetch_count=100)