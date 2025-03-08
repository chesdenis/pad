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

def read_first_line(file_path: str):
    if os.path.exists(file_path):
        with open(file_path) as f:
            return f.readline().strip('\n')

    return ''

def add_report_entry(file_path, relative_path, channel, args, write_all = False):
    meta_folder_path = os.path.join(meta_folder, relative_path)

    report.append({
        "md5_hash": read_first_line(os.path.join(meta_folder_path, "md5_hash.txt")),
        "parent_folder_name": read_first_line(os.path.join(meta_folder_path, "parent_folder_name.txt")),
        "parent_folder_path": read_first_line(os.path.join(meta_folder_path, "parent_folder_path.txt")),
        "extension": read_first_line(os.path.join(meta_folder_path, "extension.txt")),
        "size": read_first_line(os.path.join(meta_folder_path, "size.txt")),
        "tags": read_first_line(os.path.join(meta_folder_path, "tags.txt")),
        "file_name": read_first_line(os.path.join(meta_folder_path, "file_name.txt")),
        'preview16_hash' :  read_first_line(os.path.join(meta_folder_path, "preview16_hash.txt")),
        'preview32_hash' :  read_first_line(os.path.join(meta_folder_path, "preview32_hash.txt")),
        'preview64_hash' :  read_first_line(os.path.join(meta_folder_path, "preview64_hash.txt")),
        'preview128_hash' :  read_first_line(os.path.join(meta_folder_path, "preview128_hash.txt")),
        'preview512_hash' :  read_first_line(os.path.join(meta_folder_path, "preview512_hash.txt")),
        'preview2000_hash' :  read_first_line(os.path.join(meta_folder_path, "preview2000_hash.txt"))
    })

def handle_event_entry(file_path, relative_path, channel, args):
    logging.info(f'Calculating {args} for {file_path}')
    add_report_entry(file_path, relative_path, channel, args)

@app.route('/report', methods=['GET'])
def trigger_report():
    pd.DataFrame(report).to_csv(os.path.join(report_folder, 'storage.csv'), index=False)
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