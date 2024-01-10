import threading
from multiprocessing import Pool, cpu_count
from process import process_part, process_part_get, delete_part_file
import time
import os
import uuid
import zlib
import hashlib
from storage.fileregistry import FileRegistry
from storage.partregistry import PartRegistry
from loader import load_config

current_memory_usage = 0
memory_usage_lock = threading.Condition()
MAX_MEMORY_LIMIT = 1024 * 1024 * 1024
file_registry = FileRegistry()
part_registry = PartRegistry()


def put(file_path):
    global current_memory_usage
    print('Putting file: {}'.format(file_path))
    config = load_config()
    storage_dir = config['storage_dir']
    part_size = config['part_size'] * 1024

    parts_dir = os.path.join(storage_dir, 'file_parts')
    os.makedirs(parts_dir, exist_ok=True)

    file_name = os.path.basename(file_path)
    file_id = file_registry.add_file(file_name)
    print(f"File added: ID={file_id}, Name={file_name}")

    part_data_list = []
    part_id_list = []

    with open(file_path, 'rb') as f:
        part_number = 0
        while True:
            print(f"Reading part {part_number}")
            part_data = f.read(part_size)
            if not part_data:
                break

            with memory_usage_lock:
                while current_memory_usage + len(part_data) > MAX_MEMORY_LIMIT:
                    memory_usage_lock.wait()
                current_memory_usage += len(part_data)

            part_id = str(uuid.uuid4())
            part_id_list.append(part_id)
            part_path = os.path.join(parts_dir, f"{part_id}.part")
            part_data_list.append((part_data, part_path))
            part_registry.add_part(part_id, file_id, part_number, None)
            print(f"Part added: ID={part_id}, File ID={file_id}, Part Number={part_number}")
            part_number += 1

    file_registry.add_parts(file_id, part_id_list)

    with Pool(processes=os.cpu_count()) as pool:
        results = pool.starmap(process_part, part_data_list, chunksize=1)

    with memory_usage_lock:
        current_memory_usage -= len(part_data)
        memory_usage_lock.notify_all()

    part_number += 1

    for md5_hash, part_path in results:
        part_id = os.path.basename(part_path).split('.')[0]
        part_registry.update_part_status(part_id, 'ready')
        part_registry.update_part(part_id, md5_hash)

    file_registry.update_file_status(file_id, 'ready')
    print(f"File stored with ID: {file_id}")
    print(file_registry.files)
    return file_id


def get(file_id):
    global current_memory_usage
    print('Getting file: {}'.format(file_id))

    try:
        file_id = int(file_id)
    except ValueError:
        print('File ID must be an integer')
        return

    tempName = file_registry.get_file_name(file_id)
    print(f"File name = {tempName}")
    print(f"Registry = {file_registry.files}")
    outputFileName = 'retrieved_' + file_registry.files[file_id]['file_name']

    config = load_config()
    storage_dir = config['storage_dir']
    part_size = config['part_size'] * 1024

    file_info = file_registry.files.get(file_id)
    if not file_info:
        print('File not found')
        return

    if file_info['status'] != 'ready':
        print('File not ready')
        return

    parts = file_info['parts']

    part_info_list = []

    for part_id in parts:
        part_info = part_registry.get_part_info(part_id)
        if not part_info:
            print(f"Part: {part_id} not found")
            return
        if part_info['status'] != 'ready':
            print(f"Part: {part_id} not ready")
            return

        with memory_usage_lock:
            while current_memory_usage + part_size > MAX_MEMORY_LIMIT:
                memory_usage_lock.wait()
            current_memory_usage += part_size

        part_info_list.append((storage_dir, part_id, part_info['md5_hash']))

    retrieved_dir = os.path.join(storage_dir, 'retrieved_files')
    os.makedirs(retrieved_dir, exist_ok=True)
    output_file_path = os.path.join(retrieved_dir, f"{outputFileName}")

    print('Part info list:', part_info_list)

    with Pool(processes=os.cpu_count()) as pool:
        results = pool.map(process_part_get, part_info_list)
    print(results)

    with open(output_file_path, 'wb') as output_file:
        print('Writing file')
        for part_id, success, data_or_error in results:
            print(f"Writing part {part_id}")
            if not success:
                print(f'Error with part {part_id}: {data_or_error}')
                continue

            output_file.write(data_or_error)
            with memory_usage_lock:
                current_memory_usage -= part_size
                memory_usage_lock.notify_all()

    print('File retrieved to: {}'.format(output_file_path))

def delete(file_id):
    global current_memory_usage
    print('Deleting file: {}'.format(file_id))

    try:
        file_id = int(file_id)
    except ValueError:
        print('File ID must be an integer')
        return

    file_info = file_registry.get_file_info(file_id)

    if not file_info:
        print(f"File ID {file_id} not found ")
        return
    elif file_info['status'] != 'ready':
        print(f"File ID {file_id} not ready")
        return

    file_registry.mark_file_as_not_ready(file_id)
    parts_for_deletion = file_info['parts'].copy()
    for part in parts_for_deletion:
        part_registry.mark_part_as_not_ready(part)

    config = load_config()
    storage_dir = config['storage_dir']
    part_size = config['part_size'] * 1024

    parts_dir = os.path.join(storage_dir, 'file_parts')
    os.makedirs(parts_dir, exist_ok=True)
    part_paths = [os.path.join(parts_dir, f"{part_id}.part") for part_id in parts_for_deletion]

    successful_deletions = []
    with Pool(processes=cpu_count()) as pool:
        successful_deletions = pool.map(delete_part_file, part_paths)

    for part_id, success in zip(parts_for_deletion, successful_deletions):
        if success:
            part_registry.delete_part(part_id)
            with memory_usage_lock:
                current_memory_usage -= part_size
                memory_usage_lock.notify_all()

    if all(successful_deletions):
        file_registry.delete_file(file_id)
        print('File deleted')
    else:
        print('Some parts could not be deleted')
        return

    file_registry.delete_file(file_id)
    print('File deleted')


def list():
    print('File list:')
    for file_id, file_info in file_registry.files.items():
        print(f"ID: {file_id}, Name: {file_info['file_name']}, Status: {file_info['status']}")


def main():
    threads = []
    while True:
        cmd = input()
        if cmd == "exit":
            print('\nExiting...')
            for thread in threads:
                thread.join()
            break
        elif cmd.startswith("put "):
            file_path = cmd.split(" ", 1)[1]
            thread = threading.Thread(target=put, args=(file_path,))
            thread.start()
            threads.append(thread)
        elif cmd.startswith("get "):
            file_id = cmd.split(" ", 1)[1]
            thread = threading.Thread(target=get, args=(file_id,))
            thread.start()
            threads.append(thread)
        elif cmd.startswith("delete "):
            file_id = cmd.split(" ", 1)[1]
            thread = threading.Thread(target=delete, args=(file_id,))
            thread.start()
            threads.append(thread)
        elif cmd == "list":
            thread = threading.Thread(target=list)
            thread.start()
            threads.append(thread)
        elif cmd == "put":
            print('\nPut command requires a file path')
        elif cmd == "get":
            print('\nGet command requires a file id')
        elif cmd == "delete":
            print('\nDelete command requires a file id')
        elif cmd == "help":
            print('\nCommands:')
            print('put <file_path>')
            print('get <file_id>')
            print('delete <file_id>')
            print('list')
            print('exit')
        else:
            print('\nUnknown command: {}'.format(cmd))

if __name__ == '__main__':
    main()