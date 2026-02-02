from enum import Enum

class ServiceMethod(str, Enum):
    SAVE_FILE = "save_file"
    GET_LISTED_FILES = "get_listed_files"
    GET_FILE_METADATA = "get_file_metadata"
    READ_CSV_DATA = "read_csv_data"

class StorageRepositoryType(str, Enum):
    FILE_METADATA = "file_metadata"