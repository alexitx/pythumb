import errno
import os
import re
import requests
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .exceptions import (
    InvalidIDError,
    InvalidURLError,
    NotFetchedError,
    NotFoundError
)


class Thumbnail:
    """
    Client for fetching and saving a YouTube video thumbnail.

    Either the `url` or `id` argument is required. If both are present `id` is used.

    Example:
        >>> from pythumb import Thumbnail
        >>> t = Thumbnail('https://youtu.be/aqz-KE-bpKQ')
        >>> t.fetch()
        >>> t.save('.')

    Args:
        url (str):
            YouTube video URL (supports full, short and embed variants)
        id (str):
            11-character YouTube video ID

    Methods:
        fetch:
            Sends an HTTP request and fetches the thumbnail.
        save:
            Writes the fetched image to a file in the specified location.

    Attributes:
        id (str):
            Parsed ID of the video
        size (str):
            Name of the requested size
        ext (str):
            Format-dependent file extension
        image (bytes):
            The image data as bytes

    Raises:
        InvalidIDError:
            The specified ID is not a valid YouTube video ID
        InvalidURLError:
            The specified URL is not a valid YouTube video URL
    """

    _id_regex = re.compile(r'^[\w-]{11}$')
    _size_regex = re.compile(r'^(maxres|sd|hq|mq|)?(default|1|2|3)$')
    _size_prefixes = ('maxres', 'sd', 'hq', 'mq', '')

    def __init__(self, url: str = None, id: str = None):
        self._url = url
        self._id = id
        if self._url is None and self._id is None:
            raise ValueError('Must provide video URL or ID')
        # Parse ID first, if not present fall back to URL
        self.id: str = self._parse_id() if self._id else self._parse_url()
        self.image: bytes = None
        self.size: str = None
        self.ext: str = None

    def fetch(
        self,
        size: str = 'maxresdefault',
        webp: bool = False,
        fallback: bool = True,
        timeout: float = 5.0
    ):
        """
        Sends HTTP HEAD requests to get the available thumbnail sizes.
        After the desired size is chosen, a GET request is sent to fetch the image.

        Args:
            size (str, optional):
                Default thumbnail:
                  - maxresdefault
                  - sddefault
                  - hqdefault
                  - mqdefault
                  - default
                Auto-generated thumbnails (not always available):
                  - maxres1
                  - maxres2
                  - maxres3
                  - sd1
                  - sd2
                  - sd3
                  - hq1
                  - hq2
                  - hq3
                  - mq1
                  - mq2
                  - mq3
                  - 1
                  - 2
                  - 3
                Default: 'maxresdefault'
            webp (bool, optional):
                Use WebP instead of JPEG format
            fallback (bool, optional):
                Fallback to lower sizes if the requested size is not found
            timeout (float, optional):
                Server response timeout in seconds

        Returns:
            bytes:
                The image data as bytes

        Raises:
            NotFoundError:
                Thumbnail with the requested size is not found
                or the video does not exist
        """

        match = self._size_regex.match(size)
        if not match:
            raise ValueError(f'Invalid thumbnail size: {size}')
        prefix, suffix = match.groups()

        url_template = 'https://i.ytimg.com/{}/{}/{}.{}'
        # Start from the requested size for fallback
        start = self._size_prefixes.index(prefix)
        for current_prefix in self._size_prefixes[start:]:
            current_size = f'{current_prefix}{suffix}'
            if webp:
                url = url_template.format('vi_webp', self.id, current_size, 'webp')
            else:
                url = url_template.format('vi', self.id, current_size, 'jpg')
            # Get response code to verify if the requested size is available
            h = requests.head(url, timeout=timeout, allow_redirects=True)
            if h.ok:
                # Fetch the actual image
                r = requests.get(url, timeout=timeout)
                if r.ok:
                    self.image = r.content
                    self.size = current_size
                    self.ext = 'webp' if webp else 'jpg'
                    return self.image

            if not fallback:
                break

        raise NotFoundError(f"Failed to find thumbnail for video ID '{self.id}' with size '{size}'")

    def save(
        self,
        dir: str,
        filename: str = None,
        overwrite: bool = False,
        mkdir: bool = True
    ):
        """
        Writes the fetched image to a file in the specified location,
        with filename defaulting to the video ID.

        Args:
            dir (str):
                Directory in which to save the file
            filename (str, optional):
                Custom filename
            overwrite (bool, optional):
                Overwrite the file if it already exists
            mkdir (bool, optional):
                Create missing directories

        Returns:
            str:
                Absolute path to the saved file

        Raises:
            NotFetchedError:
                The thumbnail is not fetched
        """

        if self.image is None:
            raise NotFetchedError('Must fetch before saving')

        # Use custom filename, default to ID if not specified
        file = f'{filename}.{self.ext}' if filename else f'{self.id}.{self.ext}'
        path = Path(dir)

        if mkdir:
            path.mkdir(parents=True, exist_ok=True)

        dest = path.resolve().joinpath(file)
        if dest.exists() and not overwrite:
            raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), str(dest))

        with open(dest, 'wb') as f:
            f.write(self.image)

        return str(dest)

    def _parse_url(self):
        # Append scheme if missing
        base_url = self._url if self._url.startswith(('http://', 'https://')) else 'https://' + self._url

        url = urlsplit(base_url)

        # Validate YouTube URL
        if all(url.netloc != n for n in ('www.youtube.com', 'youtube.com', 'youtu.be')):
            raise InvalidURLError(f"'{self._url}' is not a valid YouTube video URL")

        id = ''
        # Parse ID from embedded or shorts URL
        if url.path.startswith(('/embed/', '/shorts/')):
            id = url.path.split('/')[2][:11]
        # Parse ID from shortened 'youtu.be' URL
        elif url.netloc == 'youtu.be':
            id = url.path[1:12]
        # Parse ID from query
        else:
            query = parse_qs(url.query)
            if 'v' in query:
                id = query['v'][0][:11]

        if not self._id_regex.match(id):
            raise InvalidURLError(f"'{self._url}' is not a valid YouTube video URL")
        return id

    def _parse_id(self):
        if not self._id_regex.match(self._id):
            raise InvalidIDError(f"'{self._id}' is not a valid YouTube video ID")
        return self._id
