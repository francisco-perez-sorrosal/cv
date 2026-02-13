"""Domain models for the CV MCP server."""

from pydantic import BaseModel, HttpUrl


class Links(BaseModel):
    """Named URLs for profiles and documents. Keys are short names (e.g. 'linkedin')."""
    urls: dict[str, HttpUrl] = {}

    def get(self, name: str) -> str | None:
        url = self.urls.get(name.lower())
        return str(url) if url is not None else None

    def names(self) -> list[str]:
        return list(self.urls.keys())


class Candidate(BaseModel):
    """Authoritative identity and contact info for the CV owner."""
    name: str
    surname: str
    title: str = ""
    email: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    country: str = ""
    links: Links = Links()
