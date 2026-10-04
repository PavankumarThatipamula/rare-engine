"""Core domain exception hierarchy for RARE Engine."""


class RareException(Exception):
    """Base exception class for all RARE Engine errors."""

    pass


class DomainException(RareException):
    """Raised when a business invariant or domain rule is violated."""

    pass


class ConfigurationError(RareException):
    """Raised when application configuration or environment is invalid."""

    pass


class InfrastructureError(RareException):
    """Raised when external storage or third-party service adapters fail."""

    pass
