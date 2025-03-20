class RSSParsingError(Exception):
    """Exception raised when RSS parsing fails."""

    def __init__(self, message: str) -> None:
        """Initializes the `RSSParsingError` exception.

        Args:
            message: The error message.
        """
        super().__init__(message)


class ArXivRSSMissingFieldError(Exception):
    """Exception raised when a required field is missing in the ArXiv RSS feed."""

    def __init__(self, field_name: str) -> None:
        """Initializes the `ArXivRSSMissingFieldError` exception.

        Args:
            field_name: The name of the missing field.
        """
        super().__init__(f"Missing required field {field_name!r} in the RSS feed entry.")
