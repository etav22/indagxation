import uuid
from dataclasses import dataclass

from dagster import ConfigurableResource, InitResourceContext, get_dagster_logger
import chromadb

logger = get_dagster_logger()


@dataclass
class ChromaClient:
    """A resource for interacting with a Chroma database."""

    host: str
    port: int = 8000
    default_collection: str = "documents"
    distance_fn: str = "cosine"

    def __post_init__(self) -> None:
        logger.debug(f"Setting up ChromaResource with host {self.host}.")
        self._client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
        )
        # Validate that the distance fn_ is one of the supported [cosine, l2, ip]
        if self.distance_fn not in ["cosine", "l2", "ip"]:
            logger.warning(
                f"Invalid distance function {self.distance_fn}. Defaulting to cosine."
            )
            self.distance_fn = "cosine"

    def _create_collection(self, collection: str) -> None:
        """Create a collection in the database.

        Args:
            collection (str): The name of the collection to create.
        """
        try:
            self._collection = self._client.create_collection(
                name=collection, metadata={"hnsw:space": self.distance_fn}
            )
            logger.info(f"Created collection {collection}.")
        except Exception as e:
            raise Exception(f"Failed to create collection {collection}.") from e

    def embed(self, docs: list[str], collection: str = "documents") -> None:
        """Embed documents into the collection.

        Args:
            docs (list[str]): A list of documents to embed.
        """
        try:
            self._collection = self._client.get_collection(collection)
        except ValueError as e:
            logger.error(f"Collection {collection} does not exist: {e}.")
            self._create_collection(collection)

        self._collection.add(documents=docs, ids=[str(uuid.uuid4()) for _ in docs])
        logger.info(
            f"✅ Embedded {len(docs)} documents into collection {self.default_collection}."
        )

    def query(self, query: str, results: int) -> chromadb.QueryResult:
        """Query the collection for documents.

        Args:
            query (str): The query to use.
            results (int): The number of results to return.

        Returns:
            chromadb.QueryResult: A list of documents.
        """
        try:
            return self._collection.query(query_texts=[query], n_results=results)
        except Exception as e:
            raise Exception(
                f"Failed to query collection {self.default_collection}."
            ) from e

    def clear_collection(self, name: str) -> None:
        """Delete documents from the collection.

        Args:
            name (str): The name of the collection to delete.
        """

        try:
            self._client.delete_collection(name)
            logger.info(f"✅ Deleted {name} collection.")
        except Exception as e:
            logger.error(f"{e}: {name} collection does not exist.")


class ChromaResource(ConfigurableResource):
    host: str
    port: int = 8000
    default_collection: str = "documents"
    distance_fn: str = "cosine"

    def create_resource(self, context: InitResourceContext) -> ChromaClient:
        return ChromaClient(
            host=self.host,
            port=self.port,
            default_collection=self.default_collection,
            distance_fn=self.distance_fn,
        )
