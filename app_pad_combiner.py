import os
import logging
import _compression as comp
import time

UPLOAD_FOLDER = "/uploads"
OUTPUT_FOLDER = "/output"

def combine(folder_path, output_folder_path):
    try:
        # Dictionary to group parts by filename
        file_groups = {}

        # Iterate over all files in the folder to group by "filename.partX_of_Y" pattern
        for file_name in os.listdir(folder_path):
            if ".part" in file_name and "_of_" in file_name:
                base_name, part_info = file_name.split(".part", 1)
                part_number, total_parts = part_info.split("_of_")
                part_number = int(part_number)
                total_parts = int(total_parts)

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
                        if not os.path.exists(part_path):
                            logging.error(f"Missing file part {part_number}/{total_parts}: {part_path}")
                            return
                        with open(part_path, 'rb') as part:
                            combined_file.write(part.read())

                logging.info(f"File parts combined successfully into: {combined_file_path}")
                comp.extract_tar(combined_file_path, output_folder_path)

            except Exception as e:
                logging.error(f"Error combining file group '{base_name}': {e}")

    except Exception as e:
        logging.error(f"Error processing folder '{folder_path}': {e}")

if __name__ == "__main__":
    while True:
        combine(UPLOAD_FOLDER, OUTPUT_FOLDER)
        time.sleep(60)
