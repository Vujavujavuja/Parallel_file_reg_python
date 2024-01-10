class PartRegistry:
    def __init__(self):
        self.parts = {}

    def add_part(self, part_id, file_id, part_number, md5_hash):
        if file_id not in self.parts:
            self.parts[file_id] = {}
        self.parts[file_id][part_id] = {
            'part_number': part_number,
            'md5_hash': md5_hash,
            'status': 'not_ready'
        }

    def update_part_status(self, part_id, status):
        for file_parts in self.parts.values():
            if part_id in file_parts:
                file_parts[part_id]['status'] = status
                break

    def update_part(self, part_id, md5_hash):
        for file_id, parts in self.parts.items():
            if part_id in parts:
                parts[part_id]['md5_hash'] = md5_hash
                parts[part_id]['status'] = 'ready'
                break

    def get_part_info(self, part_id):
        for file_parts in self.parts.values():
            if part_id in file_parts:
                return file_parts[part_id]
        return None

    def mark_part_as_not_ready(self, part_id):
        for file_parts in self.parts.values():
            if part_id in file_parts:
                file_parts[part_id]['status'] = 'not_ready'
                return True
        return False

    def delete_part(self, part_id):
        for file_id, parts in list(self.parts.items()):
            if part_id in parts:
                del parts[part_id]
                if not parts:
                    del self.parts[file_id]
                return True
        return False
