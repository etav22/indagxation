from dagster import asset, get_dagster_logger
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader

from .resources import ChromaResource

logger = get_dagster_logger()


@asset
def load_docs() -> list[Document]:
    """Load documents from the web."""

    docs = WebBaseLoader("https://google.com").load()
    logger.debug(f"Loaded {docs} documents from the web.")
    return docs


@asset
def embed_docs(chroma_client: ChromaResource, load_docs: list[Document]) -> None:
    """Embed documents into the Chroma database."""

    _docs = [doc.page_content for doc in load_docs]
    chroma_client.embed_docs(_docs)

    return None
