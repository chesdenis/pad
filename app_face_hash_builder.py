import os.path

from PIL import Image
import numpy as np

import face_recognition
import hashlib
import logging
import json

import _fs_entry_handler as fshandler
import _path_resolvers as rp
import app_meta_builder as mb

def get_face_vectors(file_path):
    if not os.path.exists(file_path):
        return None

    image = Image.open(file_path)
    for angle in [90, 180, 270]:
        # Find all face locations and their encodings in the image
        face_locations = face_recognition.face_locations(np.array(image))
        face_encodings = face_recognition.face_encodings(np.array(image), face_locations)

        if len(face_locations) > 0:
            return {
                "face_locations":face_locations,
                "face_encodings":[encoding.tolist() for encoding in face_encodings]
            }

        image = image.rotate(angle, expand=True)

    logging.info(f'No face detected on image {file_path}')
    return None

def write_face_hash(args, write_all, file_path, relative_path):
    if mb.allow_attr_write(args, 'face_vectors', relative_path, write_all):
        # we must use large picture to find all faces more accurately
        preview_path = rp.get_meta_file_name(relative_path, 'preview2000.jpg')
        face_vectors = get_face_vectors(preview_path)

        if face_vectors is not None:
            face_vectors_as_json = json.dumps(face_vectors)
            logging.info(f'Serialized face vectors for {relative_path}')
            mb.write_attribute_file(relative_path, "face_vectors.txt", face_vectors_as_json)

def write_attributes(file_path, relative_path, channel, args, write_all = False):
    mb.ensure_attribute_home_folder(relative_path)
    write_face_hash(args, write_all, file_path, relative_path)

def handle_event_entry(file_path, relative_path, channel, args):
    write_attributes(file_path, relative_path, channel, args, write_all=True)
    logging.info(f'Processed {relative_path}')

if __name__ == '__main__':
    fshandler.start(handle_event_entry, prefetch_count=100)