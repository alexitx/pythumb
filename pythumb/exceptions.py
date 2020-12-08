class ThumbnailError(Exception):
    pass

class InvalidIDError(ThumbnailError):
    pass

class InvalidURLError(ThumbnailError):
    pass

class NotFetchedError(ThumbnailError):
    pass

class NotFoundError(ThumbnailError):
    pass
