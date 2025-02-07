import hashlib
import logging
import os.path
import shutil

import _fs_entry_handler as fshandler
import _path_resolvers as rp

def move_file(file_path, relative_path):
    file_name = os.path.basename(file_path)
    dest_path = rp.get_meta_file_name(relative_path, file_name)

    #shutil.move(file_path, dest_path)
    logging.info(f'Moved file from {file_name} to {dest_path}')

def handle_event_entry(file_path, relative_path, channel, args):
    move_file(file_path, relative_path)
    logging.info(f'Moved file {relative_path}')

if __name__ == '__main__':
    fshandler.start(handle_event_entry, prefetch_count=100)