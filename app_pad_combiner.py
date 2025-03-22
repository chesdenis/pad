import os
import logging
import _tar_builder as comp
import time
import hashlib
import re

import _crypto_actions as crypto

aes_key_string = os.environ.get("AES_KEY_STRING")
aes_key = hashlib.sha256(aes_key_string.encode()).digest()[:16]

UPLOAD_FOLDER = "/uploads"
OUTPUT_FOLDER = "/output"
DECRYPTED_FOLDER = "/decrypted"

# Define universal regex for matching part information (e.g., part1_of_6)
PART_REGEX = r"part(?P<part_number>\d+)_of_(?P<total_parts>\d+)"

def combine(folder_path, decrypted_folder, output_folder_path):
    try:
        # Dictionary to group parts by filename
        file_groups = {}

        # Iterate over all files in the folder to group by "filename.partX_of_Y" pattern
        for file_name in os.listdir(folder_path):
            if ".part" in file_name and "_of_" in file_name:
                match = re.search(PART_REGEX, file_name)

                part_number = int(match.group('part_number'))  # Extract part number
                total_parts = int(match.group('total_parts'))  # Extract total parts
                base_name = file_name.split('.part')[0]

                # Group by base name
                if base_name not in file_groups:
                    file_groups[base_name] = []
                file_groups[base_name].append((file_name, part_number, total_parts))

        # Process each file group
        for base_name, parts in file_groups.items():
            # Sort parts by part number
            parts = sorted(parts, key=lambda x: x[1])  # Sort by part_number

            # Ensure all parts are present
            total_parts = parts[0][2]  # Total parts should be consistent across the group
            if len(parts) != total_parts:
                logging.warning(
                    f"Incomplete file group for '{base_name}'. Expected {total_parts} parts, got {len(parts)}.")
                continue

            # Combine parts into a single file
            combined_file_path = os.path.join(folder_path, base_name)
            try:
                with open(combined_file_path, 'wb') as combined_file:
                    for part_file, part_number, _ in parts:
                        part_path = os.path.join(folder_path, part_file)
                        decrypted_part_path = os.path.join(decrypted_folder, part_file)
                        if not os.path.exists(part_path):
                            logging.error(f"Missing file part {part_number}/{total_parts}: {part_path}")
                            return

                        crypto.decrypt_file(part_path, decrypted_part_path, aes_key=aes_key)

                        with open(decrypted_part_path, 'rb') as part:
                            combined_file.write(part.read())

                logging.info(f"File parts combined successfully into: {combined_file_path}")
                comp.extract_tar(combined_file_path, output_folder_path)

                # cleanup
                os.remove(combined_file_path)
                logging.info(f"Deleted combined file: {combined_file_path}")
                os.remove(decrypted_part_path)
                logging.info(f"Deleted decrypted file: {decrypted_part_path}")

                for part_file, part_number, _ in parts:
                    part_path = os.path.join(folder_path, part_file)
                    os.remove(part_path)
                    logging.info(f"Deleted file part {part_number}/{total_parts}: {part_path}")

            except Exception as e:
                logging.error(f"Error combining file group '{base_name}': {e}")

    except Exception as e:
        logging.error(f"Error processing folder '{folder_path}': {e}")

if __name__ == "__main__":
    while True:
        combine(UPLOAD_FOLDER, DECRYPTED_FOLDER, OUTPUT_FOLDER)
        time.sleep(60)
