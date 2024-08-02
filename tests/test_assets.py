from langchain_core.documents import Document
import pytest
import chromadb

from indagxation.config import CollectionConfig
import indagxation.assets as assets
from indagxation.resources import ChromaClient


@pytest.fixture
def chroma_db():
    class ChromaMock(ChromaClient):
        def __init__(self):
            self._client = chromadb.Client()
            self.distance_fn = "cosine"

    return ChromaMock()


def test_load_docs():
    asset = assets.load_docs()

    assert isinstance(asset, list)
    assert all(isinstance(doc, Document) for doc in asset)


def test_embed_docs(chroma_db):
    config = CollectionConfig(collection="documents")
    docs = assets.load_docs()

    assets.embed_docs(config, chroma_db, docs)

    # Confirm that the right number of documents were embedded.
    assert chroma_db._collection.count() == len(docs)
