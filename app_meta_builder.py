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

def calculate_parent_folder_path(file_path):
    return os.path.dirname(file_path)

def calculate_tags(file_path):
    return ";#".join(os.path.split(os.path.dirname(file_path)))

def calculate_extension(file_path):
    extension = os.path.splitext(file_path)[1]
    return extension

def calculate_size(file_path):
    size = os.path.getsize(file_path)
    return f'{size}'


rewrite: bool = False

def ensure_attribute_home_folder(relative_path):
    attribute_home_folder = rp.get_meta_home_folder(relative_path)
    if not os.path.exists(attribute_home_folder):
        os.makedirs(attribute_home_folder, exist_ok=True)
        logging.info(f"Created new attribute folder {attribute_home_folder}")

def require_process(relative_path, rewrite):
    if rewrite:
        return True




def write_attribute_file(relative_path, attribute_file_name, attribute_value):
    attr_file_name = rp.get_meta_file_name(relative_path, attribute_file_name)

    f = open(attr_file_name, "w")
    f.write(attribute_value)
    f.close()

def allow_attr_write(args, attr_name, relative_path, write_all):
    can_write = False
    if args["meta_name"] == attr_name:
        if args["rewrite"]:
            can_write = True
        elif write_all:
            can_write = True
        else:
            attribute_file_path = rp.get_meta_file_name(relative_path, f"{attr_name}.txt")
            logging.info(f"Verifying attribute existance for {attribute_file_path}")
            # if file is missing, we allow write
            if not os.path.exists(attribute_file_path):
                can_write = True

    return can_write

def write_md5_hash(args, write_all, file_path, relative_path):
    if allow_attr_write(args, 'md5_hash', relative_path, write_all):
        md5_hash = calculate_file_hash(file_path)
        write_attribute_file(relative_path, "md5_hash.txt", md5_hash)

def write_parent_folder_name(args, write_all, file_path, relative_path):
    if allow_attr_write(args, 'parent_folder_name', relative_path, write_all):
        parent_folder_name = calculate_parent_folder_name(file_path)
        write_attribute_file(relative_path, "parent_folder_name.txt", parent_folder_name)

def write_parent_folder_path(args, write_all, file_path, relative_path):
    if allow_attr_write(args, 'parent_folder_path', relative_path, write_all):
        parent_folder_path = calculate_parent_folder_path(relative_path)
        write_attribute_file(relative_path, "parent_folder_path.txt", parent_folder_path)

def write_tags(args, write_all, file_path, relative_path):
    if allow_attr_write(args, 'tags', relative_path, write_all):
        tags = calculate_tags(file_path)
        write_attribute_file(relative_path, "tags.txt", tags)

def write_extension(args, write_all, file_path, relative_path):
    if allow_attr_write(args, 'extension', relative_path, write_all):
        extension = calculate_extension(file_path)
        write_attribute_file(relative_path, "extension.txt", extension)

def write_size(args, write_all, file_path, relative_path):
    if allow_attr_write(args, 'size',relative_path, write_all):
        size = calculate_size(file_path)
        write_attribute_file(relative_path, "size.txt", size)

def write_file_name(args, write_all, file_path, relative_path):
    if allow_attr_write(args, 'file_name',relative_path, write_all):
        file_name = os.path.basename(file_path)
        write_attribute_file(relative_path, "file_name.txt", file_name)

def write_relative_path(args, write_all, file_path, relative_path):
    if allow_attr_write(args, 'relative_path',relative_path, write_all):
        write_attribute_file(relative_path, "relative_path.txt", relative_path)

def write_attributes(file_path, relative_path, channel, args, write_all = False):

    ensure_attribute_home_folder(relative_path)

    write_md5_hash(args, write_all, file_path, relative_path)
    write_parent_folder_name(args, write_all, file_path, relative_path)
    write_parent_folder_path(args, write_all, file_path, relative_path)
    write_tags(args, write_all, file_path, relative_path)
    write_extension(args, write_all, file_path, relative_path)
    write_size(args, write_all, file_path, relative_path)
    write_file_name(args, write_all, file_path, relative_path)
    write_relative_path(args, write_all, file_path, relative_path)


def handle_event_entry(file_path, relative_path, channel, args):
    if args != '':
        logging.info(f'Applying specific meta extract of {args} for {file_path}')
        write_attributes(file_path, relative_path, channel, args)
    else:
        write_attributes(file_path, relative_path, channel, args, write_all=True)
        logging.info(f'Stored file hash and attributes for {relative_path}')


if __name__ == '__main__':
    fshandler.start(handle_event_entry, prefetch_count=100)