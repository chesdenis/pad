import os
import pandas as pd
import logging
from flask import Flask, jsonify
import threading

import _fs_entry_handler as fshandler

storage_folder = '/source'
meta_folder = '/meta'
report_folder = '/report'

report = []
exceptions = []

app = Flask(__name__)


def handle_event_entry(file_path, relative_path, channel, args):
    logging.info(f'Calculating {args} for {file_path}')
    add_report_entry(file_path, relative_path, channel, args)

def add_report_entry(file_path, relative_path, channel, args, write_all = False):
    relative_folder_path = os.path.dirname(relative_path)
    meta_folder_path = os.path.join(meta_folder, relative_path)
    filename, file_extension = os.path.splitext(relative_path)
    report.append({
        'extension': file_extension.upper(),
        'relative_folder_path': relative_folder_path,
        'relative_file_path': relative_path,
        'meta_folder': meta_folder_path,
        'extension_file_exist': os.path.exists(os.path.join(meta_folder_path, 'extension.txt')),
        'size_file_exist': os.path.exists(os.path.join(meta_folder_path, 'size.txt')),
        'tags_file_exist': os.path.exists(os.path.join(meta_folder_path, 'tags.txt')),
        'md5_hash_file_exist': os.path.exists(os.path.join(meta_folder_path, 'md5_hash.txt')),
        'parent_folder_name_file_exist': os.path.exists(os.path.join(meta_folder_path, 'parent_folder_name.txt')),
        'parent_folder_path_file_exist': os.path.exists(os.path.join(meta_folder_path, 'parent_folder_path.txt')),
        'file_name_file_exist': os.path.exists(os.path.join(meta_folder_path, 'file_name.txt')),
        'preview16exist': os.path.exists(os.path.join(meta_folder_path, 'preview16.jpg')),
        'preview32exist': os.path.exists(os.path.join(meta_folder_path, 'preview32.jpg')),
        'preview64exist': os.path.exists(os.path.join(meta_folder_path, 'preview64.jpg')),
        'preview128exist': os.path.exists(os.path.join(meta_folder_path, 'preview128.jpg')),
        'preview512exist': os.path.exists(os.path.join(meta_folder_path, 'preview512.jpg')),
        'preview2000exist': os.path.exists(os.path.join(meta_folder_path, 'preview2000.jpg')),
    })

@app.route('/report', methods=['GET'])
def trigger_report():
    pd.DataFrame(report).to_csv(os.path.join(report_folder, 'storage_vs_meta.csv'), index=False)
    logging.info(f'Finished')
    logging.info(f'Collected exceptions:')
    for e in exceptions:
        logging.info(e)

    return jsonify({"status": "success", "message": "Report generation triggered"}), 200


@app.route('/clear', methods=['GET'])
def trigger_clear():
    global report
    report = []
    logging.info(f'Finished')

    return jsonify({"status": "success", "message": "Cleared. Ready to accept next messages"}), 200

def run_flask_app():
    app.run(host='0.0.0.0', port=5000)

def run_fs_handler():
    fshandler.start(handle_event_entry, prefetch_count=100)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask_app)
    fs_handler_thread = threading.Thread(target=run_fs_handler)

    flask_thread.start()
    fs_handler_thread.start()

    flask_thread.join()
    fs_handler_thread.join()