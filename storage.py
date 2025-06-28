from enum import Enum
import logging

logger = logging.getLogger(__name__)

class StorageBackendType(Enum):
    FILE = "FILE"
    DATABASE = "DATABASE"

    @classmethod
    def from_string(cls, backend_str: str):
        try:
            return cls[backend_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid storage backend: {backend_str}")
        
    def __str__(self):
        return self.value


class StorageBackend:
    def __init__(self, backend_type: StorageBackendType):
        self.backend_type = backend_type

    def add_line(self, line: str) -> int:
        raise NotImplementedError("This method should be implemented by subclasses")

    def modify_line(self, key: str, new_line: str) -> int:
        raise NotImplementedError("This method should be implemented by subclasses")

    def delete_line(self, key: str) -> int:
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def get_lines(self) -> list:
        raise NotImplementedError("This method should be implemented by subclasses")
    
class FileStorageBackend(StorageBackend):
    def __init__(self, file_path: str):
        super().__init__(StorageBackendType.FILE)
        self.file_path = file_path

    def add_line(self, line: str) -> int:
        with open(self.file_path, "r+") as file:
            lines = file.readlines()
            logger.debug(f"Current lines in file: {lines}")
            last_line = lines[-1] if lines else ""
            logger.debug(f"Last line in file: {last_line.strip()}")
            if last_line:
                last_key = int(last_line.split(": ", 1)[0])
                new_key = last_key + 1
            else:
                new_key = -1
            
            file.seek(0, 2)
            file.write(f"{new_key}: {line}\n")
            return int(new_key)

    def modify_line(self, key: str, new_line: str) -> int:
       with open(self.file_path, "r+") as file:
            lines = file.readlines()
            logger.debug(f"Current lines in file: {lines}")
            for i, line in enumerate(lines):
                logger.debug(f"Checking line {i}: {line.strip()}")
                if line.startswith(f"{key}:"):
                    lines[i] = f"{key}: {new_line}\n"
                    break
            else:
                raise KeyError(f"Key {key} not found for modification.")
            
            logger.debug(f"Current lines in file: {lines}")
            file.truncate(0)
            file.seek(0)
            file.writelines(lines)
            return int(key)

    def delete_line(self, key: str) -> int:
        with open(self.file_path, "r+") as file:
            lines = file.readlines()
            logger.debug(f"Current lines in file: {lines}")
            for i, line in enumerate(lines):
                if line.startswith(f"{key}:"):
                    del lines[i]
                    break
            else:
                raise KeyError(f"Key {key} not found for deletion.")
            
            logger.debug(f"Current lines in file: {lines}")
            file.truncate(0)
            file.seek(0)
            file.writelines(lines)
            return int(key)
    
    def get_lines(self) -> list:
        with open(self.file_path, "r") as file:
            lines = file.readlines()
            logger.debug(f"Current lines in file: {lines}")
            return [line.strip() for line in lines if line.strip()]

class PostgreSQLStorageBackend(StorageBackend):
    def __init__(self, connection_string: str):
        super().__init__(StorageBackendType.DATABASE)
        self.connection_string = connection_string
        # Initialize database connection here

    def add_line(self, line: str) -> int:
        # Implement adding a line to the PostgreSQL database
        pass

    def modify_line(self, key: str, new_line: str) -> int:
        # Implement modifying a line in the PostgreSQL database
        pass

    def delete_line(self, key: str) -> int:
        # Implement deleting a line from the PostgreSQL database
        pass
