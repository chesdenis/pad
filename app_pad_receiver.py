from flask import Flask, request, jsonify
import os
import logging
import re
import shutil

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "/uploads"
TEMP_FOLDER = "/tmp"

# Define universal regex for matching part information (e.g., part1_of_6)
PART_REGEX = r"part(?P<part_number>\d+)_of_(?P<total_parts>\d+)"


# Logger setup
logging.basicConfig(level=logging.INFO)

@app.route('/ping')
def ping():
    return "pong"

@app.route('/upload', methods=['POST'])
def upload_part():

    if 'file' not in request.files:
        logging.warning('No file part')
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        logging.warning('No selected file')
        return jsonify({'error': 'No file selected'}), 400

    filename = file.filename
    logging.info(f"Received file part: {filename}")

    match = re.search(PART_REGEX, filename)
    if not match:
        logging.warning('Invalid file part format')
        return jsonify({'error': 'Invalid file part format'}), 400
    try:
        part_number = int(match.group('part_number'))  # Extract part number
        total_parts = int(match.group('total_parts'))  # Extract total parts
    except ValueError:
        logging.warning('Invalid part information in filename')
        return jsonify({'error': 'Invalid part information in filename'}), 400


    temp_path = os.path.join(TEMP_FOLDER, filename)
    file.save(temp_path)

    # Define the target upload path
    part_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        # Move the file from the temporary location to the uploads folder
        shutil.move(temp_path, part_path)  # Move the file directly

        logging.info(f"Received and moved file part {part_number}/{total_parts}: {part_path}")
    except Exception as e:
        logging.error(f"Failed to move file part {part_number}: {e}")

        # Cleanup the temporary file if something goes wrong
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({'error': 'File move failed'}), 500

    return jsonify({'message': f'File part {part_number} uploaded successfully'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
