from datavisyn_project.app.helper.enum import StorageRepositoryType
from .file_repository import FileMetadataRepository

class RepositoryFactory:

    @staticmethod
    def get_repository(repotype: StorageRepositoryType, db_session):

        repositories = {
            StorageRepositoryType.FILE_METADATA: FileMetadataRepository
        }

        repo_class = repositories.get(repotype)

        if not repo_class:
            raise ValueError(f"Repository '{repotype}' not found")

        return repo_class(db_session=db_session)
 
