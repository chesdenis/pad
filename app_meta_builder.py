import hashlib
import logging
import os.path

import _attr_builder as ab

def calculate_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def calculate_parent_folder_name(file_path):
    parent_folder_name = os.path.basename(os.path.dirname(file_path))
    return parent_folder_name

def calculate_tags(file_path):
    return ";#".join(os.path.split(os.path.dirname(file_path)))

def calculate_extension(file_path):
    extension = os.path.splitext(file_path)[1]
    return extension

def calculate_size(file_path):
    size = os.path.getsize(file_path)
    return f'{size}'


rewrite: bool = False


def require_process(relative_path):
    if rewrite:
        return True

    attribute_file_path = get_attribute_file_name(relative_path, "md5_hash")
    logging.info(f"Verifying attribute existance for {attribute_file_path}")
    attribute_home_folder = get_attribute_home_folder(relative_path)
    if not os.path.exists(attribute_home_folder):
        os.makedirs(attribute_home_folder, exist_ok=True)
        logging.info(f"Created new attribute folder {attribute_home_folder}")

    # if file is missing, we must calculate content for it
    if not os.path.exists(attribute_file_path):
        return True

    return False

def get_attribute_home_folder(relative_path):
    return os.path.join("meta", relative_path)

def get_attribute_file_name(relative_path, attribute_file_name):
    return os.path.join("meta", relative_path, attribute_file_name)

def write_attribute_file(relative_path, attribute_file_name, attribute_value):
    attr_file_name = get_attribute_file_name(relative_path, attribute_file_name)

    f = open(attr_file_name, "w")
    f.write(attribute_value)
    f.close()

def build_attribute(file_path, relative_path, channel):
    if not require_process(relative_path):
        logging.info(f'File {file_path} with relative path {relative_path} is not require for processing')
        return

    md5_hash = calculate_file_hash(file_path)
    parent_folder_name = calculate_parent_folder_name(file_path)
    extension = calculate_extension(file_path)
    size = calculate_size(file_path)
    tags = calculate_tags(file_path)
    logging.info(f'Calculated file hash for {file_path} and other attributes')

    write_attribute_file(relative_path, "md5_hash.txt", md5_hash)
    write_attribute_file(relative_path, "parent_folder_name.txt", parent_folder_name)
    write_attribute_file(relative_path, "extension.txt", extension)
    write_attribute_file(relative_path, "size.txt", size)
    write_attribute_file(relative_path, "tags.txt", tags)

    logging.info(f'Stored file hash and attributes for {relative_path}')


if __name__ == '__main__':
    ab.start(build_attribute, prefetch_count=100)