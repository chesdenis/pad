import os.path

from PIL import Image
import imagehash
import logging

import _fs_entry_handler as fshandler
import _path_resolvers as rp
import app_meta_builder as mb

def build_image_hashes(file_path, relative_path, prefix):
    try:
        if not os.path.exists(file_path):
            return None

        img = Image.open(file_path)

        if not mb.attribute_exist(relative_path, f"{prefix}_colorhash.txt"):
            mb.write_attribute_file(relative_path, f"{prefix}_colorhash.txt", imagehash.colorhash(img))

        if not mb.attribute_exist(relative_path, f"{prefix}_phash.txt"):
            mb.write_attribute_file(relative_path, f"{prefix}_phash.txt", imagehash.phash(img))

        if not mb.attribute_exist(relative_path, f"{prefix}_dhash.txt"):
            mb.write_attribute_file(relative_path, f"{prefix}_dhash.txt", imagehash.dhash(img))

        if not mb.attribute_exist(relative_path, f"{prefix}_average_hash.txt"):
            mb.write_attribute_file(relative_path, f"{prefix}_average_hash.txt", imagehash.average_hash(img))

    except Exception as e:
        logging.error(e)

def write_image16_hash(args, write_all, file_path, relative_path):
    preview_path = rp.get_meta_file_name(relative_path, 'preview16.jpg')
    build_image_hashes(preview_path, relative_path, "preview16")

def write_image32_hash(args, write_all, file_path, relative_path):
    preview_path = rp.get_meta_file_name(relative_path, 'preview32.jpg')
    build_image_hashes(preview_path, relative_path, "preview32")

def write_image64_hash(args, write_all, file_path, relative_path):
    preview_path = rp.get_meta_file_name(relative_path, 'preview64.jpg')
    build_image_hashes(preview_path, relative_path, "preview64")

def write_image128_hash(args, write_all, file_path, relative_path):
    preview_path = rp.get_meta_file_name(relative_path, 'preview128.jpg')
    build_image_hashes(preview_path, relative_path, "preview128")

def write_image512_hash(args, write_all, file_path, relative_path):
    preview_path = rp.get_meta_file_name(relative_path, 'preview512.jpg')
    build_image_hashes(preview_path, relative_path, "preview512")

def write_image2000_hash(args, write_all, file_path, relative_path):
    preview_path = rp.get_meta_file_name(relative_path, 'preview2000.jpg')
    build_image_hashes(preview_path, relative_path, "preview2000")

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