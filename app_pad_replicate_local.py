
import _fs_entry_handler as fshandler
import _path_resolvers as rp
import shutil
import os
import logging

SOURCE = '/source'
TARGET = '/target'
TARGET_META = '/target-meta'

def handle_event_entry(file_path, relative_path, channel, args):

    # Transferred file_path:/source/anna-photograph/.../DSC_0525.NEF
    # and related_meta_folder: meta/anna-photograph/.../DSC_0525.NEF
    # relative_path: anna-photograph/не мама - доп- 25 июня/карантин и мой проект/2020/2020-04-03/DSC_0525.NEF


    replica_path = os.path.join(TARGET, relative_path)
    os.makedirs(os.path.dirname(replica_path), exist_ok=True)

    if os.path.exists(replica_path):
        logging.info(f'File already exists: {replica_path}')
        return

    shutil.copy2(file_path, replica_path)

    replica_meta_folder_path = os.path.join(TARGET_META, relative_path)
    related_meta_folder = rp.get_meta_home_folder(relative_path)
    shutil.copytree(related_meta_folder, replica_meta_folder_path, dirs_exist_ok=True)

    logging.info(f'Replicated file_path and their meta for :{file_path}')

if __name__ == '__main__':
    fshandler.start(handle_event_entry, prefetch_count=100)