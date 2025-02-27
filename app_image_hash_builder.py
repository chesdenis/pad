import os.path

from PIL import Image
import imagehash
import logging

import _fs_entry_handler as fshandler
import _path_resolvers as rp
import app_meta_builder as mb

def calculate_image_hash(file_path):
    try:
        if not os.path.exists(file_path):
            return None

        average_hash = imagehash.average_hash(Image.open(file_path))
        return str(average_hash)
    except Exception as e:
        logging.error(e)

    return None

def write_image16_hash(args, write_all, file_path, relative_path):
    if mb.allow_attr_write(args, 'preview16_hash', relative_path, write_all):
        preview_path = rp.get_meta_file_name(relative_path, 'preview16.jpg')
        image_hash = calculate_image_hash(preview_path)
        if image_hash is not None:
            mb.write_attribute_file(relative_path, "preview16_hash.txt", image_hash)

def write_image32_hash(args, write_all, file_path, relative_path):
    if mb.allow_attr_write(args, 'preview32_hash', relative_path, write_all):
        preview_path = rp.get_meta_file_name(relative_path, 'preview32.jpg')
        image_hash = calculate_image_hash(preview_path)
        if image_hash is not None:
            mb.write_attribute_file(relative_path, "preview32_hash.txt", image_hash)

def write_image64_hash(args, write_all, file_path, relative_path):
    if mb.allow_attr_write(args, 'preview64_hash', relative_path, write_all):
        preview_path = rp.get_meta_file_name(relative_path, 'preview64.jpg')
        image_hash = calculate_image_hash(preview_path)
        if image_hash is not None:
            mb.write_attribute_file(relative_path, "preview64_hash.txt", image_hash)

def write_image128_hash(args, write_all, file_path, relative_path):
    if mb.allow_attr_write(args, 'preview128_hash', relative_path, write_all):
        preview_path = rp.get_meta_file_name(relative_path, 'preview128.jpg')
        image_hash = calculate_image_hash(preview_path)
        if image_hash is not None:
            mb.write_attribute_file(relative_path, "preview128_hash.txt", image_hash)

def write_image512_hash(args, write_all, file_path, relative_path):
    if mb.allow_attr_write(args, 'preview512_hash', relative_path, write_all):
        preview_path = rp.get_meta_file_name(relative_path, 'preview512.jpg')
        image_hash = calculate_image_hash(preview_path)
        if image_hash is not None:
            mb.write_attribute_file(relative_path, "preview512_hash.txt", image_hash)

def write_image2000_hash(args, write_all, file_path, relative_path):
    if mb.allow_attr_write(args, 'preview2000_hash', relative_path, write_all):
        preview_path = rp.get_meta_file_name(relative_path, 'preview2000.jpg')
        image_hash = calculate_image_hash(preview_path)
        if image_hash is not None:
            mb.write_attribute_file(relative_path, "preview2000_hash.txt", image_hash)


def write_attributes(file_path, relative_path, channel, args, write_all = False):
    mb.ensure_attribute_home_folder(relative_path)

    write_image16_hash(args, write_all, file_path, relative_path)
    write_image32_hash(args, write_all, file_path, relative_path)
    write_image64_hash(args, write_all, file_path, relative_path)
    write_image128_hash(args, write_all, file_path, relative_path)
    write_image512_hash(args, write_all, file_path, relative_path)
    write_image2000_hash(args, write_all, file_path, relative_path)


def handle_event_entry(file_path, relative_path, channel, args):
    write_attributes(file_path, relative_path, channel, args, write_all=True)
    logging.info(f'Stored image hash values for {relative_path}')

if __name__ == '__main__':
    fshandler.start(handle_event_entry, prefetch_count=100)