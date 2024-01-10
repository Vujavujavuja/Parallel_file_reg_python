from threading import Lock


class FileRegistry:
    def __init__(self):
        self.files = {}
        self.lock = Lock()
        self.current_id = 0

    def add_file(self, file_name, status='pending'):
        file_id = self.generate_new_id()
        with self.lock:
            self.files[file_id] = {'file_id': file_id, 'file_name': file_name, 'status': status, 'parts': {}}
        return file_id

    def add_parts(self, file_id, part_list):
        with self.lock:
            if file_id in self.files:
                self.files[file_id]['parts'] = part_list

    def generate_new_id(self):
        with self.lock:
            self.current_id += 1
            return self.current_id

    def update_file_status(self, file_id, status):
        if file_id in self.files:
            self.files[file_id]['status'] = status

    def get_file_name(self, file_id):
        name = self.files[file_id]['file_name']
        return name

    def mark_file_as_not_ready(self, file_id):
        with self.lock:
            if file_id in self.files:
                self.files[file_id]['status'] = 'not_ready'
                return True
            return False

    def delete_file(self, file_id):
        with self.lock:
            if file_id in self.files:
                del self.files[file_id]
                return True
            return False

    def get_file_info(self, file_id):
        with self.lock:
            return self.files.get(file_id)
