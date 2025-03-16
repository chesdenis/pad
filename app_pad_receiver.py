from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "/uploads"
TEMP_FOLDER = "/tmp"

# Logger setup
logging.basicConfig(level=logging.INFO)

@app.route('/upload', methods=['POST'])
def upload_part():

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

    temp_path = os.path.join(TEMP_FOLDER, filename)
    file.save(temp_path)

    # Define the target upload path
    part_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        # Move the file from the temporary location to the uploads folder
        os.rename(temp_path, part_path)  # Move the file directly

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
