import requests
import httpx
from pathlib import Path
from typing import Optional
from sdk.exceptions import KnowledgeAPIError, ConnectionError, DocumentNotFoundError


class KnowledgeClient:

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _handle_response(self, response: requests.Response) -> dict:
        if response.status_code == 404:
            raise DocumentNotFoundError(response.url)
        if not response.ok:
            raise KnowledgeAPIError(response.status_code, response.text)
        return response.json()

    def health(self) -> dict:
        try:
            response = self._session.get(self._url("/"))
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            raise ConnectionError(self.base_url)

    
    def upload(self, file_path: str, description: Optional[str] = None) -> dict:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
    
        with open(path, "rb") as f:
            files = {"file": (path.name, f)}
            data = {}
            if description:
                data["description"] = description
            response = self._session.post(
                self._url("/documents"),
                files=files,
                data=data
        )
        return self._handle_response(response)


    def list_documents(self) -> list:
        response = self._session.get(self._url("/documents"))
        return self._handle_response(response)

    def get_document(self, document_id: str) -> dict:
        response = self._session.get(self._url(f"/documents/{document_id}"))
        return self._handle_response(response)

    def delete_document(self, document_id: str) -> dict:
        response = self._session.delete(self._url(f"/documents/{document_id}"))
        return self._handle_response(response)

    def search(self, query: str) -> dict:
        response = self._session.post(
            self._url("/search"),
            json={"query": query}
        )
        return self._handle_response(response)

    def ask(self, query: str) -> dict:
        response = self._session.post(
            self._url("/ask"),
            json={"query": query}
        )
        return self._handle_response(response)

    def ask_stream(self, query: str):
        with httpx.stream(
            "POST",
            self._url("/ask/stream"),
            json={"query": query},
            timeout=120
        ) as response:
            for chunk in response.iter_text():
                if chunk:
                    yield chunk
