import errno
import os
import re
import requests
import shutil
from collections import OrderedDict
from io import BytesIO
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
        image (io.BytesIO):
            Byte buffer containing the image data

    Raises:
        InvalidIDError:
            The specified ID is not a valid YouTube video ID
        InvalidURLError:
            The specified URL is not a valid YouTube video URL
    """

    _id_re = re.compile(r'^[\w-]{11}$')
    _size = OrderedDict([
        (0, 'maxresdefault'),
        (1, 'sddefault'),
        (2, 'hqdefault'),
        (3, 'mqdefault'),
        (4, 'default'),
    ])
    _format = OrderedDict([
        (0, ('vi', 'jpg')),
        (1, ('vi_webp', 'webp'))
    ])

    def __init__(self, url: str = None, id: str = None):
        self._url = url
        self._id = id
        if self._url is None and self._id is None:
            raise ValueError('Must provide video URL or ID')
        # Parse ID first, if not present fall back to URL
        self.id: str = self._parse_id() if self._id else self._parse_url()
        self.size: str = None
        self.ext: str = None
        self.image: BytesIO = None

    def fetch(
        self,
        size: int = 0,
        webp: bool = False,
        fallback: bool = True,
        timeout: float = 3.0
    ):
        """
        Sends HTTP HEAD requests to get the available thumbnail sizes.
        After the desired size is chosen, a GET request is sent to fetch the image,
        which is saved as a byte buffer.

        The image data is cached and returned immediately on future calls.

        Args:
            size (int, optional):
                Thumbnail size from 0 (largest) to 4 (smallest)
            webp (bool, optional):
                Use WebP instead of JPEG format
            fallback (bool, optional):
                Fallback to lower sizes if the requested size is not found
            timeout (float, optional):
                Server response timeout in seconds

        Returns:
            io.BytesIO:
                Byte buffer containing the image data

        Raises:
            NotFoundError:
                Thumbnail with the requested size is not found
                or the video does not exist
        """

        if self.image:
            return self.image

        url_template = 'https://i.ytimg.com/{}/{}/{}.{}'
        fmt = self._format[1] if webp else self._format[0]

        # Loop through all valid sizes
        for size_id, size_name in self._size.items():
            # Only attempt to fetch if the current size
            # is smaller than or equal to the requested size
            if size > size_id:
                continue

            url = url_template.format(fmt[0], self.id, size_name, fmt[1])
            # Get response code to verify if the requested size is available
            h = requests.head(url, timeout=timeout, allow_redirects=True)
            if h.ok:
                # Fetch the actual image
                r = requests.get(url, timeout=timeout)
                if r.ok:
                    self.image = BytesIO(r.content)
                    self.size = size_name
                    self.ext = fmt[1]
                    return self.image

            # Don't check lower sizes if fallback is False
            if not fallback:
                break

        raise NotFoundError(
            "Failed to find thumbnail for video ID "
            f"'{self.id}' with size '{self._size[size]}'",
            self.id,
            self._size[size]
        )

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
            try:
                path.mkdir(parents=True, exist_ok=True)
            except FileExistsError:
                raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), str(path))

        dest = path.resolve().joinpath(file)
        if dest.exists() and not overwrite:
            raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), str(dest))

        with open(dest, 'wb') as f:
            shutil.copyfileobj(self.image, f)

        return str(dest)

    def _parse_url(self):
        # Append scheme if missing
        base_url = self._url if self._url.startswith(('http://', 'https://')) else 'https://' + self._url

        url = urlsplit(base_url)

        # Validate YouTube URL
        if all(url.netloc != n for n in ('www.youtube.com', 'youtube.com', 'youtu.be')):
            raise InvalidURLError(f"'{self._url}' is not a valid YouTube video URL", self._url)

        id = ''
        # Parse ID from embed URL
        if url.path.startswith('/embed/'):
            id = url.path.split('/')[2][:11]
        # Parse ID from short URL
        elif url.netloc == 'youtu.be':
            id = url.path[1:12]
        # Parse URL from query
        else:
            query = parse_qs(url.query)
            if 'v' in query:
                id = query['v'][0][:11]

        # Validate ID
        if not self._id_re.fullmatch(id):
            raise InvalidURLError(f"'{self._url}' is not a valid YouTube video URL", self._url)
        return id

    def _parse_id(self):
        # Validate ID
        if not self._id_re.fullmatch(self._id):
            raise InvalidIDError(f"'{self._id}' is not a valid YouTube video ID", self._id)
        return self._id
