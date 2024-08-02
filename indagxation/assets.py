from dagster import asset, get_dagster_logger
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader

from .resources import ChromaResource
from .config import RetrievalConfig, CollectionConfig

logger = get_dagster_logger()


@asset
def load_docs() -> list[Document]:
    """Load documents from the web."""

    docs = WebBaseLoader("https://google.com").load()
    logger.debug(f"Loaded {docs} documents from the web.")
    return docs


@asset
def embed_docs(
    config: CollectionConfig, chroma_client: ChromaResource, load_docs: list[Document]
) -> None:
    """Embed documents into the Chroma database."""

    _docs = [doc.page_content for doc in load_docs]
    chroma_client.embed_docs(_docs, collection=config.collection)

    return None


@asset
def retrieve_docs(config: RetrievalConfig, chroma_client: ChromaResource):
    """Retrieve documents from the Chroma database."""
    query_result = chroma_client.query_docs(query=config.query, results=config.results)
    logger.debug(f"Query result: {query_result}")

    return query_result


@asset
def delete_collection(config: CollectionConfig, chroma_client: ChromaResource) -> None:
    """Delete the collection from the Chroma database."""
    chroma_client.clear_collection(config.collection)
