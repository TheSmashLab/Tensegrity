class TensegrityError(Exception):
    """Base class for errors that can be shown directly to users."""


class TensegrityParseError(TensegrityError):
    """Raised when a tensegrity YAML file cannot be parsed."""


class TensegrityInputError(TensegrityError):
    """Raised when interactive user input cannot be applied."""


class TensegritySolveError(TensegrityError):
    """Raised when the solver cannot produce an updated structure."""
