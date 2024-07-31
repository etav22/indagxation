from dagster import Definitions

from .assets import load_docs

defs = Definitions(assets=[load_docs])
