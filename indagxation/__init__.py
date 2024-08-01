from dagster import Definitions, EnvVar, load_assets_from_modules

from . import assets
from .resources import ChromaResource

defs = Definitions(
    assets=load_assets_from_modules([assets]),
    resources={
        "chroma_client": ChromaResource(
            host=EnvVar("CHROMA_HOST"),
        )
    },
)
