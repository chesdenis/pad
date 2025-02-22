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

def read_first_line(file_path: str):
    with open(file_path) as f:
        return f.readline().strip('\n')

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

                report.append({
                    "md5_hash": read_first_line(os.path.join(meta_folder_path, "md5_hash.txt")),
                    "parent_folder_name": read_first_line(os.path.join(meta_folder_path, "parent_folder_name.txt")),
                    "parent_folder_path": read_first_line(os.path.join(meta_folder_path, "parent_folder_path.txt")),
                    "extension": read_first_line(os.path.join(meta_folder_path, "extension.txt")),
                    "size": read_first_line(os.path.join(meta_folder_path, "size.txt")),
                    "tags": read_first_line(os.path.join(meta_folder_path, "tags.txt")),
                    "file_name": read_first_line(os.path.join(meta_folder_path, "file_name.txt"))
                })
            except Exception as e:
                exceptions.append(f'{os.path.join(root, name)}: {e}')
    if len(exceptions) > 0:
        print(exceptions)

    pd.DataFrame(report).to_csv(os.path.join(report_folder, 'storage.csv'), index=False)
    print(f'Completed')

if __name__ == '__main__':
    build_report()