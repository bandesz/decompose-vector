"""Custom exceptions for decompose-vector operations."""


class DecomposeError(Exception):
    """Base exception for decompose operations."""

    def __init__(self, message: str, original_error=None):
        super().__init__(message)
        self.original_error = original_error
        self.message = message

    def __str__(self):
        if self.original_error:
            return f"{self.message}: {self.original_error}"
        return self.message


class FileError(DecomposeError):
    """Exception raised for file-related errors."""

    pass


class UnsupportedFormatError(DecomposeError):
    """Exception raised when file format is not supported."""

    pass


class ProcessingError(DecomposeError):
    """Exception raised during geometric processing."""

    pass


class ValidationError(DecomposeError):
    """Exception raised during input validation."""

    pass


class ConfigurationError(DecomposeError):
    """Exception raised for configuration-related errors."""

    pass
