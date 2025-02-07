import hashlib
import logging
import os.path

import _fs_entry_handler as fshandler
import _path_resolvers as rp

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

    attribute_file_path = rp.get_meta_file_name(relative_path, "md5_hash.txt")
    logging.info(f"Verifying attribute existance for {attribute_file_path}")
    attribute_home_folder = rp.get_meta_home_folder(relative_path)
    if not os.path.exists(attribute_home_folder):
        os.makedirs(attribute_home_folder, exist_ok=True)
        logging.info(f"Created new attribute folder {attribute_home_folder}")

    # if file is missing, we must calculate content for it
    if not os.path.exists(attribute_file_path):
        return True

    return False


def write_attribute_file(relative_path, attribute_file_name, attribute_value):
    attr_file_name = rp.get_meta_file_name(relative_path, attribute_file_name)

    f = open(attr_file_name, "w")
    f.write(attribute_value)
    f.close()

def handle_direct_attribute(file_path, relative_path, channel, args):
    if args == 'md5_hash':
        md5_hash = calculate_file_hash(file_path)
        write_attribute_file(relative_path, "md5_hash.txt", md5_hash)
        return True
    if args == 'parent_folder_name':
        parent_folder_name = calculate_parent_folder_name(file_path)
        write_attribute_file(relative_path, "parent_folder_name.txt", parent_folder_name)
        return True
    if args == 'tags':
        tags = calculate_tags(file_path)
        write_attribute_file(relative_path, "tags.txt", tags)
        return True
    if args == 'extension':
        extension = calculate_extension(file_path)
        write_attribute_file(relative_path, "extension.txt", extension)
        return True
    if args == 'size':
        size = calculate_size(file_path)
        write_attribute_file(relative_path, "size.txt", size)
        return True
    if args == 'file_name':
        file_name = os.path.basename(file_path)
        write_attribute_file(relative_path, "file_name.txt", file_name)
        return True
    if not require_process(relative_path):
        logging.info(f'File {file_path} with relative path {relative_path} is not require for processing')
        return True

    return False

def handle_event_entry(file_path, relative_path, channel, args):

    if args != '':
        logging.info(f'Applying specific meta extract of {args} for {file_path}')
        result = handle_direct_attribute(file_path, relative_path, channel, args)
        if result:
            logging.info(f'File {file_path} with relative path {relative_path} is processed with direct attribute {args}')
            return
    else:
        logging.info(f'Started to calculate file hash for {file_path} and other attributes')
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
        write_attribute_file(relative_path, "file_name.txt", os.path.basename(file_path))

        logging.info(f'Stored file hash and attributes for {relative_path}')


if __name__ == '__main__':
    fshandler.start(handle_event_entry, prefetch_count=100)