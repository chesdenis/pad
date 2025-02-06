import os

def get_meta_home_folder(relative_path):
    return os.path.join("meta", relative_path)

def get_meta_file_name(relative_path, file_name):
    return os.path.join("meta", relative_path, file_name)

def get_merge_home_folder(relative_path):
    return os.path.join("merge", relative_path)

def get_merge_file_name(relative_path, file_name):
    return os.path.join("merge", relative_path, file_name)
