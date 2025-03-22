import os

def measure_mb(file_paths):
    return sum(os.path.getsize(file) for file in file_paths) / (1024 * 1024)


def walk_on_parts(file_path, chunk_size=1024 * 1024 * 20):  # Default chunk size: 20 MB
    total_parts = (os.path.getsize(file_path) + chunk_size - 1) // chunk_size

    with open(file_path, 'rb') as f:
        index = 1
        while chunk := f.read(chunk_size):
            chunk_file_path = f"{file_path}.part{index}_of_{total_parts}"
            with open(chunk_file_path, 'wb') as chunk_file:
                chunk_file.write(chunk)
                yield chunk_file_path
            index += 1