
import os
import shutil
def move_files_with_structure(source_dir, target_dir, files_to_move):
    print(f'Started moving')
    for root, dirs, files in os.walk(source_dir):
        # Filter the files that need to be moved
        files_to_transfer = [f for f in files if f in files_to_move]

        for file in files_to_transfer:
            # Create the target directory structure
            relative_path = os.path.relpath(root, source_dir)
            target_path = os.path.join(target_dir, relative_path)
            os.makedirs(target_path, exist_ok=True)

            # Move the file
            source_file_path = os.path.join(root, file)
            target_file_path = os.path.join(target_path, file)
            shutil.move(source_file_path, target_file_path)
            print(f"Moved: {source_file_path} to {target_file_path}")

    print(f'Finished')

if __name__ == '__main__':
    move_files_with_structure(
        os.getenv('SOURCE_DIR'),
        os.getenv('TARGET_DIR'),
        os.getenv('FILENAMES_TO_MOVE', '').split(','))