from dagster import Config


class RetrievalConfig(Config):
    query: str
    results: int = 1


class CollectionConfig(Config):
    collection: str = "documents"
