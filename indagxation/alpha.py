from dagster import asset
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader


@asset
def load_docs() -> list[Document]:
    docs = WebBaseLoader("https://google.com").load()
    return docs
