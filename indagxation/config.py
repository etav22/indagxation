from dagster import Config


class RequestsConfig(Config):
    repo: str = "dagster-io/dagster"
    timeout: int = 30


class RetrievalConfig(Config):
    query: str
    results: int = 1


class CollectionConfig(Config):
    collection: str = "documents"
