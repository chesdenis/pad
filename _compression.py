import tarfile
import logging
import os
import uuid

def create_tar(file_list, base_dir, output_dir=".", tar_name=None):
    if tar_name is None:
        tar_name = f"{uuid.uuid4().hex}.tar"

    os.makedirs(output_dir, exist_ok=True)

    tar_path = os.path.join(output_dir, tar_name)

    try:
        with tarfile.open(tar_path, "w") as tar:
            for file_path in file_list:
                if not os.path.exists(file_path):
                    logging.warning(f"File not found: {file_path}. Skipping.")
                    continue

                rel_path = os.path.relpath(file_path, start=base_dir)

                logging.info(f"Adding file to tar archive: {file_path} as {rel_path}")
                tar.add(file_path, arcname=rel_path)

        logging.info(f"TAR archive created successfully: {tar_path}")
        return tar_path

    except Exception as e:
        raise RuntimeError(f"Failed to create tar archive: {e}")


def extract_tar(filepath, target_folder):
    """Extracts a tar file to the specified folder."""
    try:
        if not tarfile.is_tarfile(filepath):
            logging.error(f"File is not a valid tar archive: {filepath}")
            return

        with tarfile.open(filepath, 'r') as tar:
            tar.extractall(path=target_folder)
            logging.info(f"Files extracted successfully to {target_folder}")
    except Exception as e:
        logging.error(f"Error extracting tar file {filepath}: {e}")
