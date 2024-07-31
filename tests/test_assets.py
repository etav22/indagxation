from langchain_core.documents import Document
from indagxation.assets import load_docs


def test_load_docs():
    asset = load_docs()

    assert isinstance(asset, list)
    assert all(isinstance(doc, Document) for doc in asset)
