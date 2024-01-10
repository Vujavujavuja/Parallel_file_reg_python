import zlib
import hashlib
import os


def process_part(part_data, part_path):
    compressed_part = zlib.compress(part_data)
    md5_hash = hashlib.md5(compressed_part).hexdigest()
    with open(part_path, 'wb') as part_file:
        part_file.write(compressed_part)
    return md5_hash, part_path

def process_part_get(args):
    storage_dir, part_id, md5_hash = args
    part_path = os.path.join(storage_dir, 'file_parts', f"{part_id}.part")
    try:
        with open(part_path, 'rb') as part_file:
            compressed_part = part_file.read()
        calculated_md5_hash = hashlib.md5(compressed_part).hexdigest()
        part_data = zlib.decompress(compressed_part)
        print(f"Calculated MD5: {calculated_md5_hash}")
        print(f"Expected MD5: {md5_hash}")
        if calculated_md5_hash != md5_hash:
            return part_id, False, 'MD5 mismatch'
        return part_id, True, part_data
    except Exception as e:
        return part_id, False, str(e)


def delete_part_file(part_path):
    try:
        os.remove(part_path)
        return True
    except OSError as e:
        print(f"Error deleting part file {part_path}: {e}")
        return False
