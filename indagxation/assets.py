import os
import requests


from dagster import asset, get_dagster_logger
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader

from .resources import ChromaResource
from .config import RetrievalConfig, CollectionConfig, RequestsConfig

logger = get_dagster_logger()

# The goal with this get_docs_urls is to use the github api to get the urls of the different docs
# We can parse through the different directories and if they are files, we can extract the url
# We can then pass this url into the next step to load the docs


@asset
def get_doc_urls(config: RequestsConfig):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"https://api.github.com/repos/{config.repo}/contents"
    response = requests.get(url, headers=headers, timeout=config.timeout)
    logger.debug(response)
    logger.debug(response.json())


@asset
def load_docs() -> list[Document]:
    """Load documents from the web."""

    docs = WebBaseLoader("https://huggingface.co/docs/transformers/index").load()
    logger.debug(f"Loaded {docs} documents from the web.")
    return docs


@asset
def embed_docs(
    config: CollectionConfig, chroma_client: ChromaResource, load_docs: list[Document]
) -> None:
    """Embed documents into the Chroma database."""

    _docs = [doc.page_content for doc in load_docs]
    chroma_client.embed(_docs, collection=config.collection)

    return None


@asset
def retrieve_docs(config: RetrievalConfig, chroma_client: ChromaResource):
    """Retrieve documents from the Chroma database."""
    query_result = chroma_client.query(query=config.query, results=config.results)
    logger.debug(f"Query result: {query_result}")

    return query_result


@asset
def delete_collection(config: CollectionConfig, chroma_client: ChromaResource) -> None:
    """Delete the collection from the Chroma database."""
    chroma_client.clear_collection(config.collection)
