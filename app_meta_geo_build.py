import os
import json

def find_geo_files(target_dir):
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.startswith("geo_"):
                file_name, file_extension = os.path.splitext(file)
                data_parts = file_name.split("_")
                # geo_United Kingdom_London_20240504
                if len(data_parts) != 4 or any(not part.strip() for part in data_parts):
                    # Identify and log specific missing or invalid properties
                    missing_or_invalid = [
                        f"Part-{i + 1}: '{part}' is empty or invalid"
                        for i, part in enumerate(data_parts)
                        if not part.strip()
                    ]
                    if len(data_parts) != 4:
                        missing_or_invalid.append(f"Expected 4 parts but found {len(data_parts)}")
                    print(
                        f"Skipping invalid file: {file} due to invalid structure. Details: {', '.join(missing_or_invalid)}")
                    continue

                yield (root, {
                    "key": data_parts[0],
                    "country": data_parts[1],
                    "city": data_parts[2],
                    "date": data_parts[3]
                })


def move_files_with_structure(target_dir):
    print(f'Started building')
    for geo_file in find_geo_files(target_dir):
        attr_folder = geo_file[0]
        attr_data = geo_file[1]
        attr_file = os.path.join(attr_folder, "geo.txt")
        with open(attr_file, 'w') as f:
            json.dump(attr_data, f, indent=4)
        print(f"Processed data saved to {attr_file}")


if __name__ == '__main__':
    target_dir = os.getenv('TARGET_DIR')
    move_files_with_structure(target_dir)
    print('Finished')