import uuid

from pydantic import PrivateAttr
from dagster import ConfigurableResource, InitResourceContext, get_dagster_logger
import chromadb

logger = get_dagster_logger()


class ChromaResource(ConfigurableResource):
    """A resource for interacting with a Chroma database."""

    host: str
    port: int = 8000
    default_collection: str = "documents"
    _client = PrivateAttr()
    _collection = PrivateAttr()

    def setup_for_execution(self, context: InitResourceContext) -> None:
        logger.debug(f"Setting up ChromaResource with host {self.host}.")
        self._client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
        )
        try:
            self._collection = self._client.create_collection(self.default_collection)
            logger.info(f"Created collection {self.default_collection}.")
        except Exception as e:
            logger.error(f"Failed to create collection {self.default_collection}: {e}.")
            self._collection = self._client.get_collection(self.default_collection)
        return super().setup_for_execution(context)

    def embed_docs(self, docs: list[str]) -> None:
        """Embed documents into the collection.

        Args:
            docs (list[str]): A list of documents to embed.
        """
        try:
            self._collection.add(documents=docs, ids=[str(uuid.uuid4()) for _ in docs])
            logger.info(
                f"✅ Embedded {len(docs)} documents into collection {self.default_collection}."
            )
        except Exception as e:
            raise Exception(
                f"Failed to embed documents into collection {self.default_collection}."
            ) from e
