import os
import pandas as pd
from random import randrange

storage_folder = '/source'
meta_folder = '/meta'
report_folder = '/report'

def get_total_work_size():
    total_numbers = 0
    for root, dirs, files in os.walk(storage_folder):
        if randrange(10) == 5:
            print(f'Collected for processing {total_numbers} files')
        total_numbers = total_numbers + len(files)

    return total_numbers

def build_report():
    report = []
    exceptions = []

    processed_files = 0
    total_numbers = get_total_work_size()

    for root, dirs, files in os.walk(storage_folder):

        if randrange(10) == 5:
            print(f'Processed {processed_files} of {total_numbers}')

        processed_files = processed_files + len(files)
        for name in files:
            try:
                relative_folder_path = os.path.relpath(root, storage_folder)
                relative_file_path = os.path.join(relative_folder_path, name)
                meta_folder_path = os.path.join(meta_folder, relative_file_path)
                filename, file_extension = os.path.splitext(relative_file_path)
                report.append({
                    'extension': file_extension.upper(),
                    'relative_folder_path': relative_folder_path,
                    'relative_file_path': relative_file_path,
                    'storage_folder': os.path.join(root, name),
                    'meta_folder': meta_folder_path,
                    'extension_file_exist': os.path.exists(os.path.join(meta_folder_path, 'extension.txt')),
                    'size_file_exist': os.path.exists(os.path.join(meta_folder_path, 'size.txt')),
                    'tags_file_exist': os.path.exists(os.path.join(meta_folder_path, 'tags.txt')),
                    'md5_hash_file_exist': os.path.exists(os.path.join(meta_folder_path, 'md5_hash.txt')),
                    'parent_folder_name_file_exist': os.path.exists(os.path.join(meta_folder_path, 'parent_folder_name.txt')),
                    'parent_folder_path_file_exist': os.path.exists(os.path.join(meta_folder_path, 'parent_folder_path.txt')),
                    'file_name_file_exist': os.path.exists(os.path.join(meta_folder_path, 'file_name.txt')),
                    'preview16exist': os.path.exists(os.path.join(meta_folder_path, 'preview16.jpg')),
                    'preview32exist': os.path.exists(os.path.join(meta_folder_path, 'preview32.jpg')),
                    'preview64exist': os.path.exists(os.path.join(meta_folder_path, 'preview64.jpg')),
                    'preview128exist': os.path.exists(os.path.join(meta_folder_path, 'preview128.jpg')),
                    'preview512exist': os.path.exists(os.path.join(meta_folder_path, 'preview512.jpg')),
                    'preview2000exist': os.path.exists(os.path.join(meta_folder_path, 'preview2000.jpg')),
                })
            except Exception as e:
                exceptions.append(f'{os.path.join(root, name)}: {e}')
    if len(exceptions) > 0:
        print(exceptions)

    pd.DataFrame(report).to_csv(os.path.join(report_folder, 'storage_vs_meta.csv'), index=False)

if __name__ == '__main__':
    build_report()