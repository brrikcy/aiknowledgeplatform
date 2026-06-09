class KnowledgeAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API error {status_code}: {message}")


class ConnectionError(Exception):
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Could not connect to Knowledge AI Platform at {url}")


class DocumentNotFoundError(Exception):
    def __init__(self, document_id: str):
        self.document_id = document_id
        super().__init__(f"Document not found: {document_id}")
