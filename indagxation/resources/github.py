import base64

from dagster import ConfigurableResource, InitResourceContext, get_dagster_logger
from pydantic import PrivateAttr
import requests

from ..models import GithubContent

logger = get_dagster_logger()


class GithubResource(ConfigurableResource):
    bearer_token: str
    timeout: int = 10
    _headers = PrivateAttr()

    def setup_for_execution(self, context: InitResourceContext) -> None:
        self._headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        return super().setup_for_execution(context)

    def get_repo_files(
        self, base_url: str, file_type: str = ".mdx"
    ) -> list[GithubContent]:
        """Recursively retrieve content from a GitHub repository.

        Args:
                base_url (str): Base URL from which to retrieve content.
                file_type (str, optional): File type to retrieve. Defaults to '.mdx'.

        Returns:
                list[GithubContent]: List of GitHub content.
        """

        def get_files_from_dir(url):
            response = requests.get(url, headers=self._headers, timeout=self.timeout)
            response.raise_for_status()
            contents = response.json()
            contents = [GithubContent(**item) for item in contents]

            mdx_files = []
            directories = []

            for item in contents:
                if item.type == "file" and item.name.endswith(file_type):
                    mdx_files.append(item)
                elif item.type == "dir":
                    directories.append(item.url)

            for dir_url in directories:
                mdx_files.extend(get_files_from_dir(dir_url))

            return mdx_files

        return get_files_from_dir(base_url)

    def get_file_content(self, url: str) -> str:
        """Retrieve content from a GitHub file.

        Args:
                url (str): URL of the file to retrieve.

        Returns:
                str: Content of the file.
        """
        response = requests.get(url, headers=self._headers, timeout=self.timeout)
        response.raise_for_status()
        content = response.json()

        # Decode the content
        content = content["content"]
        content = base64.b64decode(content).decode("utf-8")

        return content
