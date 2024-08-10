from pydantic import BaseModel


class GithubLinks(BaseModel):
    self: str
    git: str
    html: str


class GithubContent(BaseModel):
    name: str
    path: str
    sha: str
    size: int
    url: str
    html_url: str
    git_url: str
    download_url: str | None = None
    type: str
    content: str | None = None
    _links: GithubLinks
