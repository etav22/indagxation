from dagster import Definitions, EnvVar, load_assets_from_modules

from . import assets
from .resources import ChromaResource, GithubResource

defs = Definitions(
    assets=load_assets_from_modules([assets]),
    resources={
        "chroma_client": ChromaResource(
            host=EnvVar("CHROMA_HOST"),
        ),
        "github_client": GithubResource(
            bearer_token=EnvVar("GITHUB_TOKEN"),
        ),
    },
)
