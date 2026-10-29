class DomainError(Exception):
    """An actionable error safe to show to the local user."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status
