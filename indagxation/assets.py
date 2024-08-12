import os

from dagster import asset, get_dagster_logger, AssetExecutionContext
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .resources import ChromaResource, GithubResource
from .config import RetrievalConfig, CollectionConfig, RequestsConfig
from .models import GithubContent

logger = get_dagster_logger()

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    "X-GitHub-Api-Version": "2022-11-28",
}


@asset
def github_content(
    context: AssetExecutionContext,
    config: RequestsConfig,
    github_client: GithubResource,
) -> list[GithubContent]:
    """Retrieve content from a GitHub repository.

    Args:
        context (AssetExecutionContext): Dagster asset context.
        config (RequestsConfig): Configuration for the request.

    Returns:
        list[str]: List of doc urls.
    """
    content = github_client.get_repo_files(config.base_url)
    logger.debug(f"First 5 files: {content[:5]}")
    context.add_output_metadata({"num_files": len(content)})

    return content


@asset
def decoded_docs(
    context: AssetExecutionContext,
    github_client: GithubResource,
    github_content: list[GithubContent],
) -> list[Document]:
    """Download the content from the GitHub links.

    Args:
        context (AssetExecutionContext): Dagster asset context.
        github_client (GithubResource): GitHub client.
        github_content (list[str]): List of GitHub content.

    Returns:
        list[Document]: List of Langchain docs.
    """
    documents = []
    for content in github_content:
        logger.debug(f"Downloading content for {content.name}")
        decoded_content = github_client.get_file_content(content.url)
        doc = Document(
            page_content=decoded_content,
            metadata=content.model_dump(exclude={"content"}),
        )
        documents.append(doc)

    # Check the number of tokens in our documents
    model = SentenceTransformer("all-MiniLM-L6-v2")
    num_tokens = sum(
        [
            len(model.encode(doc.page_content, output_value="token_embeddings"))
            for doc in documents
        ]
    )

    context.add_output_metadata({"num_tokens": num_tokens})

    return documents


@asset
def chunked_docs(
    context: AssetExecutionContext, decoded_docs: list[Document]
) -> list[Document]:
    """Chunk the documents into smaller pieces.

    Args:
        context (AssetExecutionContext): Dagster asset context.
        decoded_docs (list[Document]): List of decoded documents.

    Returns:
        list[Document]: List of chunked documents.
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=256,
        chunk_overlap=50,
        length_function=lambda x: len(model.encode(x, output_value="token_embeddings")),
        is_separator_regex=False,
    )
    split_documents = splitter.split_documents(decoded_docs)
    context.add_output_metadata({"num_chunks": len(split_documents)})
    return split_documents


@asset
def embed_docs(
    config: CollectionConfig,
    chroma_client: ChromaResource,
    chunked_docs: list[Document],
) -> None:
    """Embed the document chunks into the Chroma database.

    Args:
        config (CollectionConfig): Config for the collection.
        chroma_client (ChromaResource): Chroma client to conduct vector operations.
        chunked_docs (list[Document]): List of chunked documents to embed.
    """

    _docs = [doc.page_content for doc in decoded_docs]
    metadata = [doc.metadata for doc in decoded_docs]

    chroma_client.embed(_docs, metadata, collection=config.collection)

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
