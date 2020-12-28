class ThumbnailError(Exception):
    """Base exception."""

class InvalidIDError(ThumbnailError):
    """The specified ID is not a valid YouTube video ID."""

class InvalidURLError(ThumbnailError):
    """The specified ID is not a valid YouTube video URL."""

class NotFetchedError(ThumbnailError):
    """The thumbnail is not fetched."""

class NotFoundError(ThumbnailError):
    """
    Thumbnail with the requested size is not found
    or the video does not exist.
    """
