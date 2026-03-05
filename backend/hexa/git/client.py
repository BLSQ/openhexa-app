from abc import ABC, abstractmethod


class GitClient(ABC):
    @abstractmethod
    def create_organization(self, org_slug: str, display_name: str) -> dict:
        ...

    @abstractmethod
    def rename_organization(
        self, old_slug: str, new_slug: str, display_name: str
    ) -> dict | None:
        ...

    @abstractmethod
    def delete_organization(self, org_slug: str) -> None:
        ...

    @abstractmethod
    def list_org_repositories(
        self, org_slug: str, page: int = 1, limit: int = 50
    ) -> list[dict]:
        ...

    @abstractmethod
    def create_repository(self, repo_name: str) -> dict:
        ...

    @abstractmethod
    def create_org_repository(self, org_slug: str, repo_name: str) -> dict:
        ...

    @abstractmethod
    def delete_repository(self, org_slug: str, repo_name: str) -> None:
        ...

    @abstractmethod
    def archive_repository(self, org_slug: str, repo_name: str) -> dict | None:
        ...

    @abstractmethod
    def unarchive_repository(self, org_slug: str, repo_name: str) -> dict | None:
        ...

    @abstractmethod
    def get_files_tree(
        self, repo_name: str, ref: str = "main", *, org_slug: str | None = None
    ) -> list[dict]:
        ...

    @abstractmethod
    def get_file(
        self,
        repo_name: str,
        path: str,
        ref: str = "main",
        *,
        org_slug: str | None = None,
    ) -> bytes:
        ...

    @abstractmethod
    def commit_files(
        self,
        repo_name: str,
        files: list[dict],
        message: str,
        author_name: str,
        author_email: str,
        *,
        org_slug: str | None = None,
    ) -> str:
        ...

    @abstractmethod
    def get_commits(
        self,
        org_slug: str,
        repo_name: str,
        ref: str = "main",
        page: int = 1,
        limit: int = 20,
    ) -> list[dict]:
        ...
