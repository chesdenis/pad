import logging
import os.path
import shutil

import _fs_entry_handler as fshandler
import _path_resolvers as rp

def copy_file(file_path, relative_path):
    file_name = os.path.basename(file_path)
    dest_path = rp.get_merge_file_name(relative_path, file_name)
    directoy_name = os.path.dirname(dest_path)

    os.makedirs(directoy_name, exist_ok=True)
    logging.info(f'Created directory here {directoy_name}')

    logging.info(f'Copy file from {file_path} to {directoy_name}')
    shutil.copy2(file_path, dest_path)

def handle_event_entry(file_path, relative_path, channel, args):
    copy_file(file_path, relative_path)
    logging.info(f'Copied file {relative_path}')

if __name__ == '__main__':
    fshandler.start(handle_event_entry, prefetch_count=100)