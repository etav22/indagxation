from dagster import asset, get_dagster_logger
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader

logger = get_dagster_logger()


@asset
def load_docs() -> list[Document]:
    """Load documents from the web."""

    docs = WebBaseLoader("https://google.com").load()
    logger.debug(f"Loaded {docs} documents from the web.")
    return docs
