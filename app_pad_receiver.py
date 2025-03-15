from flask import Flask, request, jsonify, send_from_directory
import os
import tarfile
import logging
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


aes_key_string = os.environ.get("AES_KEY_STRING")
aes_key = hashlib.sha256(aes_key_string.encode()).digest()[:16]

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "/uploads"
EXTRACTED_FOLDER = "/extracted"

# Logger setup
logging.basicConfig(level=logging.INFO)


@app.route('/upload', methods=['POST'])
def upload_part():
    # to check dummy upload
    return jsonify({'message': 'File part uploaded successfully'}), 200

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = file.filename
    if '.part' not in filename or '_of_' not in filename:
        return jsonify({'error': 'Invalid file part format'}), 400

    part_info = filename.split('.part')[-1]
    try:
        part_number, total_parts = map(int, part_info.split('_of_'))
    except ValueError:
        return jsonify({'error': 'Invalid part information in filename'}), 400

    part_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        aes_key = os.environ.get("AES_KEY").encode()  # Fetch AES key from environment variables
        decrypt_file(file, part_path, aes_key)
        logging.info(f"Received and decrypted file part {part_number}/{total_parts}: {part_path}")
    except Exception as e:
        logging.error(f"Failed to decrypt file part {part_number}: {e}")
        return jsonify({'error': 'Decryption failed'}), 500

    return jsonify({'message': f'File part {part_number} uploaded successfully'}), 200


def decrypt_file(file, part_path, aes_key):
    if len(aes_key) not in (16, 24, 32):
        raise ValueError("Invalid AES key length. Key must be 16, 24, or 32 bytes.")

    # Read the encrypted file content
    encrypted_data = file.read()

    # The first 16 bytes of the encrypted file contain the IV
    iv = encrypted_data[:16]
    encrypted_content = encrypted_data[16:]

    try:
        # Initialize the AES cipher for decryption
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        os.makedirs(os.path.dirname(part_path), exist_ok=True)

        # Decrypt the content in chunks and write to the output path
        with open(part_path, "wb") as output_file:
            output_file.write(decryptor.update(encrypted_content))
            output_file.write(decryptor.finalize())

        logging.info(f"Decrypted file saved to: {part_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to decrypt file: {e}")


@app.route('/combine', methods=['POST'])
def combine_and_extract_files_in_folder(folder_path, output_folder_path):
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
                extract_tar(combined_file_path, output_folder_path)

            except Exception as e:
                logging.error(f"Error combining file group '{base_name}': {e}")

    except Exception as e:
        logging.error(f"Error processing folder '{folder_path}': {e}")

    return jsonify({'message': 'File part combined successfully'}), 200


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
