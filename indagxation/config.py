from dagster import Config


class RequestsConfig(Config):
    base_url: str = "https://api.github.com/repos/dagster-io/dagster/contents/docs/content?ref=master"
    timeout: int = 30


class RetrievalConfig(Config):
    query: str
    results: int = 1


class CollectionConfig(Config):
    collection: str = "documents"
